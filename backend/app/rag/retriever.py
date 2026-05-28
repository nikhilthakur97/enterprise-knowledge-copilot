"""Vector similarity retrieval over the ChromaDB collection populated by ingest.py.

The retriever is the read-side counterpart to the ingestion pipeline.
It embeds the user's question with the same model, queries Chroma for
the top-k most similar chunks, filters out noisy matches below a
similarity floor, and returns Pydantic `Source` objects ready to be
serialised in /api/chat responses.
"""

from __future__ import annotations

import logging
import os

# Chroma reads these on import, so they must be set before importing chromadb.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)

from functools import lru_cache  # noqa: E402

import chromadb  # noqa: E402
from chromadb.config import Settings as ChromaSettings  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.rag.embeddings import embed_query  # noqa: E402
from app.schemas import Source  # noqa: E402

COLLECTION_NAME = "hr_docs"
DEFAULT_TOP_K = 4

# Cosine similarity below this is treated as "not relevant enough to
# ground on". Tuned empirically against the synthetic HR dataset; the
# bot will refuse rather than ground on borderline matches. The LLM's
# grounding instructions are the primary safeguard; this is a backstop.
MIN_SIMILARITY = 0.30

# Trim chunk text to this many characters before sending to the frontend.
# The full text still goes to the LLM via the prompt; this is just to
# keep the citation snippet readable in the UI.
MAX_SNIPPET_CHARS = 400


@lru_cache(maxsize=1)
def _get_collection() -> chromadb.Collection:
    settings = get_settings()
    client = chromadb.PersistentClient(
        path=str(settings.chroma_path),
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    return client.get_collection(COLLECTION_NAME)


def _truncate(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def retrieve(query: str, top_k: int = DEFAULT_TOP_K) -> list[Source]:
    """Return up to top_k chunks most similar to the query.

    Results below MIN_SIMILARITY are dropped. An empty query returns
    an empty list (no embedding cost, no Chroma call).
    """
    if not query.strip():
        return []

    collection = _get_collection()
    embedding = embed_query(query)
    result = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
    )

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    sources: list[Source] = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        similarity = 1.0 - float(dist)
        if similarity < MIN_SIMILARITY:
            continue
        sources.append(
            Source(
                file=str(meta.get("source", "unknown")),
                heading=meta.get("heading") or None,
                snippet=_truncate(doc, MAX_SNIPPET_CHARS),
                score=round(similarity, 4),
            )
        )
    return sources
