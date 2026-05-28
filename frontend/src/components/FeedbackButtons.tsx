// Per-message thumbs up/down. Calls /api/feedback with the rating and
// (for thumbs down) an optional comment. Sends question + answer in the
// payload so the JSONL log on the backend is self-contained for
// offline analysis.
//
// Each instance owns its own state machine; no global feedback store.
// Once submitted, the buttons collapse to a "thanks" message — there's
// intentionally no "change my rating" UI in the POC scope.

import { useState, type FormEvent } from 'react';
import { ApiError, postFeedback } from '../api/client';

interface Props {
  messageId: string;
  question: string;
  answer: string;
}

type State =
  | { kind: 'idle' }
  | { kind: 'commenting' }
  | { kind: 'submitting' }
  | { kind: 'submitted' }
  | { kind: 'error'; message: string };

export function FeedbackButtons({ messageId, question, answer }: Props) {
  const [state, setState] = useState<State>({ kind: 'idle' });
  const [comment, setComment] = useState('');

  async function send(rating: 'up' | 'down', commentText?: string) {
    setState({ kind: 'submitting' });
    try {
      await postFeedback({
        message_id: messageId,
        rating,
        comment: commentText?.trim() ? commentText.trim() : undefined,
        question,
        answer,
      });
      setState({ kind: 'submitted' });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? `Couldn't save feedback (${err.status === 0 ? 'network error' : `HTTP ${err.status}`}).`
          : "Couldn't save feedback.";
      setState({ kind: 'error', message });
    }
  }

  if (state.kind === 'submitted') {
    return <div className="feedback feedback-thanks">Thanks for your feedback.</div>;
  }

  if (state.kind === 'commenting' || state.kind === 'submitting') {
    const onSubmit = (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      void send('down', comment);
    };
    const submitting = state.kind === 'submitting';
    return (
      <form className="feedback feedback-commenting" onSubmit={onSubmit}>
        <label className="visually-hidden" htmlFor={`fb-comment-${messageId}`}>
          What was wrong with this answer?
        </label>
        <textarea
          id={`fb-comment-${messageId}`}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Optional: what was wrong with this answer?"
          rows={2}
          disabled={submitting}
        />
        <div className="feedback-actions">
          <button
            type="button"
            className="feedback-cancel"
            onClick={() => setState({ kind: 'idle' })}
            disabled={submitting}
          >
            Cancel
          </button>
          <button type="submit" disabled={submitting}>
            {submitting ? 'Sending…' : 'Send'}
          </button>
        </div>
      </form>
    );
  }

  return (
    <div className="feedback" role="group" aria-label="Was this answer helpful?">
      <span className="feedback-prompt">Was this helpful?</span>
      <button
        type="button"
        className="feedback-button"
        onClick={() => void send('up')}
        aria-label="Mark answer helpful"
      >
        Yes
      </button>
      <button
        type="button"
        className="feedback-button"
        onClick={() => setState({ kind: 'commenting' })}
        aria-label="Mark answer not helpful"
      >
        No
      </button>
      {state.kind === 'error' && (
        <span className="feedback-error" role="alert">
          {state.message}
        </span>
      )}
    </div>
  );
}
