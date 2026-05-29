import { FeedbackButtons } from './FeedbackButtons';
import { Sources } from './Sources';
import { renderMarkdown } from '../utils/markdown';
import type { ChatTurn } from '../hooks/useChat';

interface Props {
  turn: ChatTurn;
  question?: string;
}

export function MessageBubble({ turn, question }: Props) {
  if (turn.role === 'user') {
    return (
      <article className="bubble-user" aria-label="Your message">
        <div className="bubble-role">You</div>
        <div>{turn.content}</div>
      </article>
    );
  }

  return (
    <article className="assistant" aria-label="Assistant message">
      <div className="assistant-avatar" aria-hidden="true">
        AI
      </div>
      <div className="assistant-body">
        <div className="assistant-role">Assistant</div>
        <div className="assistant-content">{renderMarkdown(turn.content)}</div>
        <div className="assistant-meta">
          Answered in {(turn.latency_ms / 1000).toFixed(1)}s
        </div>
        <Sources sources={turn.sources} />
        <FeedbackButtons
          messageId={turn.message_id}
          question={question ?? ''}
          answer={turn.content}
        />
      </div>
    </article>
  );
}
