"""POST /api/chat endpoint.

Orchestrates the RAG flow:
  1. Validate that the latest message is a non-empty user turn.
  2. Retrieve top-k relevant chunks from the vector store using the
     latest user message as the query.
  3. Build a grounded prompt that injects the retrieved context.
  4. Call Gemini with the grounded message plus the prior conversation
     history (so follow-up questions still see context).
  5. Return the answer, sources, latency, and a server-issued
     message_id that the frontend can attach to feedback.

The retriever and LLM client are synchronous; we offload them to
asyncio threads so the FastAPI event loop stays responsive.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid

from fastapi import APIRouter, HTTPException, status

from app.rag.prompt import REFUSAL_TEXT, SYSTEM_PROMPT, build_grounded_user_message
from app.rag.retriever import retrieve
from app.schemas import ChatRequest, ChatResponse
from app.services.llm import LLMCallError, LLMConfigurationError, generate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Answer a user question grounded in the HR knowledge base."""
    last = request.messages[-1]
    if last.role != "user":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The last message must be from the user.",
        )
    if not last.content.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The user message must not be empty.",
        )

    question = last.content
    history = request.messages[:-1]
    message_id = str(uuid.uuid4())
    started = time.perf_counter()

    try:
        sources = await asyncio.to_thread(retrieve, question)
    except Exception as exc:
        logger.exception("Retrieval failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Knowledge base unavailable. Run "
                "`python -m app.rag.ingest` from backend/ first."
            ),
        ) from exc

    grounded_user_message = build_grounded_user_message(question, sources)

    try:
        answer = await asyncio.to_thread(
            generate, SYSTEM_PROMPT, grounded_user_message, history
        )
    except LLMConfigurationError as exc:
        logger.error("LLM not configured: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except LLMCallError as exc:
        # Graceful degradation: return the refusal so the user sees
        # something useful instead of a 500. Sources are blanked because
        # we cannot claim to have grounded an answer on them.
        logger.warning("LLM call failed; returning refusal to client: %s", exc)
        return ChatResponse(
            answer=REFUSAL_TEXT,
            sources=[],
            latency_ms=int((time.perf_counter() - started) * 1000),
            message_id=message_id,
        )

    return ChatResponse(
        answer=answer,
        sources=sources,
        latency_ms=int((time.perf_counter() - started) * 1000),
        message_id=message_id,
    )
