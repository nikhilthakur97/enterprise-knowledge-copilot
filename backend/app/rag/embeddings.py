"""Sentence-transformers embedding wrapper.

The model is loaded once and cached. SentenceTransformer load takes a
few seconds and consumes ~80 MB of memory, so we never want to do it
per-request. `lru_cache` provides thread-safe lazy initialisation.
"""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    settings = get_settings()
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns one vector per input, as plain lists.

    Plain Python lists are returned (not numpy arrays) so the result is
    directly serialisable to JSON and acceptable to ChromaDB.
    """
    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    """Embed a single query. Thin wrapper around `embed_texts`."""
    return embed_texts([text])[0]
