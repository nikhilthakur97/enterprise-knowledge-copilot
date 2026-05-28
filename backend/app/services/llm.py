"""Google Gemini client wrapper.

Encapsulates the LLM call with timeout, retry, and structured errors so
the chat endpoint can stay focused on orchestration. Exposes a single
function `generate(...)` that returns the model's answer text.

Two distinct error types let callers distinguish "the LLM is not
configured at all" (user fix: set the API key) from "the LLM call
failed at request time" (caller can fall back to a refusal message).
"""

from __future__ import annotations

import logging
import time
from functools import lru_cache
from typing import Iterable

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import Message

logger = logging.getLogger(__name__)


class LLMConfigurationError(RuntimeError):
    """Raised when the client cannot be constructed (e.g. no API key)."""


class LLMCallError(RuntimeError):
    """Raised when an LLM call fails after exhausting retries."""


# --- Tunables ---------------------------------------------------------------

# Per-call HTTP timeout. 30 seconds is generous for a single Gemini Flash
# call; anything longer almost always indicates a hung connection.
TIMEOUT_MS = 30_000

# Exponential backoff: 1s, 2s, 4s. Three attempts total, retried only
# for transient errors (see `_is_retryable`).
MAX_ATTEMPTS = 3
BASE_DELAY_S = 1.0

# Generation parameters tuned for grounded HR Q&A:
#   - Low temperature: stay close to the retrieved facts; do not be creative.
#   - Bounded output: prevents runaway responses and keeps latency predictable.
TEMPERATURE = 0.2
MAX_OUTPUT_TOKENS = 1024


@lru_cache(maxsize=1)
def _get_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise LLMConfigurationError(
            "GEMINI_API_KEY is not set. Add it to backend/.env to enable chat."
        )
    return genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(timeout=TIMEOUT_MS),
    )


def _to_gemini_history(history: Iterable[Message]) -> list[types.Content]:
    """Translate our Message objects to Gemini's Content list.

    Gemini uses 'user' and 'model' (not 'assistant'). System messages
    are passed via system_instruction in the config, NOT in the
    contents list, so we drop them here.
    """
    out: list[types.Content] = []
    for m in history:
        if m.role == "system":
            continue
        role = "model" if m.role == "assistant" else "user"
        out.append(types.Content(role=role, parts=[types.Part(text=m.content)]))
    return out


def _is_retryable(exc: Exception) -> bool:
    """Decide whether an exception is worth retrying.

    Auth/configuration errors are not retried — they will keep failing
    until the operator fixes the key. Network blips, rate limits, and
    5xx-style transient errors are retried.
    """
    msg = str(exc).lower()
    non_retryable_markers = (
        "api key",
        "permission",
        "unauthorized",
        "forbidden",
        "invalid argument",
    )
    if any(marker in msg for marker in non_retryable_markers):
        return False
    return True


def generate(
    system_prompt: str,
    user_message: str,
    history: list[Message] | None = None,
) -> str:
    """Call Gemini and return the model's answer text.

    Args:
        system_prompt: Sent via Gemini's system_instruction.
        user_message: The current user-turn content (already grounded
            with retrieved context by app.rag.prompt).
        history: Prior conversation, excluding the current turn.
            System messages in history are dropped.

    Raises:
        LLMConfigurationError: if the API key is missing.
        LLMCallError: if all retry attempts fail or output is empty.
    """
    client = _get_client()
    settings = get_settings()

    contents = _to_gemini_history(history or [])
    contents.append(
        types.Content(role="user", parts=[types.Part(text=user_message)])
    )

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=TEMPERATURE,
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )

    last_exc: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=contents,
                config=config,
            )
            text = (response.text or "").strip()
            if text:
                return text
            last_exc = LLMCallError("Empty response from Gemini")
            logger.warning("Gemini returned empty response on attempt %d", attempt)
            break
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            logger.warning(
                "Gemini call failed (attempt %d/%d): %s",
                attempt,
                MAX_ATTEMPTS,
                exc,
            )
            if not _is_retryable(exc) or attempt == MAX_ATTEMPTS:
                break
            time.sleep(BASE_DELAY_S * (2 ** (attempt - 1)))

    raise LLMCallError(f"Gemini call failed: {last_exc}") from last_exc
