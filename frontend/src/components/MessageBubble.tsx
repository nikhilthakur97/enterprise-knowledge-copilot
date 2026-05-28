import { FeedbackButtons } from './FeedbackButtons';
import { Sources } from './Sources';
import type { ChatTurn } from '../hooks/useChat';

interface Props {
  turn: ChatTurn;
  question?: string;
}

export function MessageBubble({ turn, question }: Props) {
  const isAssistant = turn.role === 'assistant';
  return (
    <article
      className={`bubble bubble-${turn.role}`}
      aria-label={isAssistant ? 'Assistant message' : 'Your message'}
    >
      <div className="bubble-role">{isAssistant ? 'Assistant' : 'You'}</div>
      <div className="bubble-content">{turn.content}</div>
      {isAssistant && (
        <>
          <div className="bubble-meta">
            Answered in {(turn.latency_ms / 1000).toFixed(1)}s
          </div>
          <Sources sources={turn.sources} />
          <FeedbackButtons
            messageId={turn.message_id}
            question={question ?? ''}
            answer={turn.content}
          />
        </>
      )}
    </article>
  );
}
