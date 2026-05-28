"""POST /api/feedback endpoint.

Persists a feedback record (thumbs up/down + optional comment) to a
JSONL file at backend/data/feedback.jsonl. JSONL is chosen because:
  - Line-atomic appends are safe on POSIX for small records.
  - It is trivial to grep/jq for analysis or load into pandas later.
  - It mirrors the "append-only audit log" pattern that a real
    governance system would use; only the storage backend would
    differ in production.

POC scope:
  - No auth, no per-user identity, no deduplication.
  - One process writes; multiple workers writing concurrently is
    safe for short records but not generally guaranteed.
  - For production we would write to a database with constraints
    (one rating per user per message_id), an audit trail, and
    PII redaction. Documented in docs/RESPONSIBLE_AI.md.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.schemas import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["feedback"])

FEEDBACK_FILENAME = "feedback.jsonl"


def _feedback_path() -> Path:
    settings = get_settings()
    # Feedback lives next to the knowledge base, under data/. The
    # directory should already exist (created by the ingest script),
    # but we ensure it on first feedback write to keep the API
    # robust even if feedback is the first thing the user does.
    data_dir = settings.knowledge_base_path.parent
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / FEEDBACK_FILENAME


@router.post("/feedback", response_model=FeedbackResponse)
def feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Record a thumbs-up/down on a previously returned message_id."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message_id": request.message_id,
        "rating": request.rating,
        "comment": request.comment,
        "question": request.question,
        "answer": request.answer,
    }

    try:
        path = _feedback_path()
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        # Log details server-side; surface a generic message to the user.
        logger.exception("Failed to persist feedback")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record feedback. Please try again.",
        )

    return FeedbackResponse()
