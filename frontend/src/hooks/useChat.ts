// Conversation state + send logic.
//
// Every /api/chat call sends the full client-side history. The backend
// is stateless by design (no session storage, no DB-backed history)
// so this hook owns the entire conversation lifecycle.

import { useState } from 'react';
import { ApiError, postChat } from '../api/client';
import type { Message, Source } from '../types';

export interface UserTurn {
  role: 'user';
  content: string;
}

export interface AssistantTurn {
  role: 'assistant';
  content: string;
  sources: Source[];
  latency_ms: number;
  message_id: string;
}

export type ChatTurn = UserTurn | AssistantTurn;

export interface UseChat {
  turns: ChatTurn[];
  loading: boolean;
  error: string | null;
  send: (content: string) => Promise<void>;
  reset: () => void;
}

function turnsToMessages(turns: ChatTurn[]): Message[] {
  return turns.map((t) => ({ role: t.role, content: t.content }));
}

function describeError(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 0) {
      return "Couldn't reach the assistant. Is the backend running on localhost:8000?";
    }
    if (err.status === 503) {
      return err.message || 'The assistant is not configured. Set GEMINI_API_KEY in backend/.env.';
    }
    if (err.status === 422) {
      return `Invalid request: ${err.message}`;
    }
    return `Something went wrong (HTTP ${err.status}).`;
  }
  return 'Unknown error sending the message.';
}

export function useChat(): UseChat {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send(content: string): Promise<void> {
    const trimmed = content.trim();
    if (!trimmed || loading) return;

    setError(null);
    const userTurn: UserTurn = { role: 'user', content: trimmed };
    const nextTurns: ChatTurn[] = [...turns, userTurn];
    setTurns(nextTurns);
    setLoading(true);

    try {
      const response = await postChat({
        messages: turnsToMessages(nextTurns),
      });
      const assistantTurn: AssistantTurn = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        latency_ms: response.latency_ms,
        message_id: response.message_id,
      };
      setTurns((prev) => [...prev, assistantTurn]);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setLoading(false);
    }
  }

  function reset(): void {
    setTurns([]);
    setError(null);
  }

  return { turns, loading, error, send, reset };
}
