import { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import type { ChatTurn } from '../hooks/useChat';

interface Props {
  turns: ChatTurn[];
  loading: boolean;
  error: string | null;
  onPickExample: (text: string) => void;
}

const EXAMPLE_QUESTIONS = [
  'How many days of annual leave do I get?',
  'What is the response time for a P0 incident?',
  'Walk me through the new-hire onboarding process.',
];

function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined' || !window.matchMedia) return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export function ChatWindow({ turns, loading, error, onPickExample }: Props) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({
      behavior: prefersReducedMotion() ? 'auto' : 'smooth',
      block: 'end',
    });
  }, [turns.length, loading, error]);

  return (
    <section
      className="chat-window"
      role="log"
      aria-live="polite"
      aria-relevant="additions"
      aria-label="Conversation"
      aria-busy={loading}
    >
      {turns.length === 0 && !loading && !error && (
        <div className="chat-empty">
          <p className="chat-empty-headline">
            Ask me about Lumina&apos;s HR policies.
          </p>
          <p className="chat-empty-sub">
            Answers are grounded in 8 internal policy documents. Pick an
            example or type your own question below.
          </p>
          <div className="chat-empty-chips">
            {EXAMPLE_QUESTIONS.map((q) => (
              <button
                key={q}
                type="button"
                className="chat-empty-chip"
                onClick={() => onPickExample(q)}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {turns.map((turn, i) => {
        const prev = i > 0 ? turns[i - 1] : null;
        const question =
          turn.role === 'assistant' && prev?.role === 'user'
            ? prev.content
            : undefined;
        return <MessageBubble key={i} turn={turn} question={question} />;
      })}

      {loading && (
        <div className="chat-loading" aria-label="Assistant is thinking">
          <div className="assistant-avatar" aria-hidden="true">
            AI
          </div>
          <div className="chat-loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}

      {error && (
        <div className="chat-error" role="alert">
          {error}
        </div>
      )}

      <div ref={endRef} />
    </section>
  );
}
