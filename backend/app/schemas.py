"""API request/response contracts.

These are defined up-front so the frontend has a stable contract to mirror,
even before the /api/chat and /api/feedback endpoints are implemented.
The frontend's `src/types.ts` should be kept in sync with this module.
"""

from typing import Literal

from pydantic import BaseModel, Field


# --- Chat ---


class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    messages: list[Message] = Field(..., min_length=1)


class Source(BaseModel):
    file: str
    snippet: str
    score: float
    heading: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    latency_ms: int
    message_id: str


# --- Feedback ---


class FeedbackRequest(BaseModel):
    message_id: str
    rating: Literal["up", "down"]
    comment: str | None = Field(default=None, max_length=1000)
    # Optional context the frontend can attach so feedback records are
    # self-contained for offline evaluation. Server does not store any
    # chat history keyed by message_id, so without these fields the
    # feedback would be uncorrelatable.
    question: str | None = Field(default=None, max_length=4000)
    answer: str | None = Field(default=None, max_length=8000)


class FeedbackResponse(BaseModel):
    ok: bool = True


# --- Health ---


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
