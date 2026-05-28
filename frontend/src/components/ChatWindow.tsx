import { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import type { ChatTurn } from '../hooks/useChat';

interface Props {
  turns: ChatTurn[];
  loading: boolean;
  error: string | null;
}

export function ChatWindow({ turns, loading, error }: Props) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [turns.length, loading, error]);

  return (
    <section
      className="chat-window"
      role="log"
      aria-live="polite"
      aria-relevant="additions"
      aria-label="Conversation"
    >
      {turns.length === 0 && !loading && !error && (
        <div className="chat-empty">
          <p>Ask me about Lumina&apos;s HR policies.</p>
          <p className="chat-empty-examples">
            Try: &ldquo;How many days of annual leave do I get?&rdquo;,
            &ldquo;What is the response time for a P0 incident?&rdquo;, or
            &ldquo;Find information about onboarding.&rdquo;
          </p>
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
          <span></span>
          <span></span>
          <span></span>
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
