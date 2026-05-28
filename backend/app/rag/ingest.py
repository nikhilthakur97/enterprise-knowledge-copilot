"""One-shot ingestion: chunk markdown docs, embed, persist to ChromaDB.

Usage (from the backend/ directory):
    python -m app.rag.ingest

Idempotent: stable chunk IDs + `collection.upsert` mean re-running this
script updates existing chunks rather than duplicating them. Safe to
run after editing any document in data/hr_docs/.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Disable Chroma's anonymous telemetry before import. We also silence the
# telemetry logger because chromadb 0.5.x has a posthog version mismatch
# that prints harmless but noisy "Failed to send telemetry event" lines
# even when telemetry is disabled.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.rag.embeddings import embed_texts

COLLECTION_NAME = "hr_docs"

# Tuned for ~200-token chunks with the all-MiniLM-L6-v2 tokenizer.
# Overlap protects against boundary loss without bloating the index.
MAX_CHUNK_CHARS = 800
OVERLAP_CHARS = 100


@dataclass
class Chunk:
    text: str
    source: str          # file name, e.g. "leave-policy.md"
    chunk_idx: int       # 0-based position within the file
    heading: str         # nearest preceding ## heading, or "" if none


def split_by_heading(markdown: str) -> list[tuple[str, str]]:
    """Split markdown into (heading, body) sections at level-2 headings.

    Content before the first ## is grouped under an empty heading. Empty
    sections are dropped.
    """
    sections: list[tuple[str, str]] = []
    current_heading = ""
    current_body: list[str] = []

    heading_re = re.compile(r"^##\s+(.+?)\s*$")

    for line in markdown.splitlines():
        m = heading_re.match(line)
        if m:
            if current_body:
                sections.append((current_heading, "\n".join(current_body).strip()))
                current_body = []
            current_heading = m.group(1).strip()
        else:
            current_body.append(line)

    if current_body:
        sections.append((current_heading, "\n".join(current_body).strip()))

    return [(h, b) for h, b in sections if b]


def split_long(text: str, max_chars: int, overlap: int) -> list[str]:
    """Split a too-long section by paragraph, then char-window with overlap.

    Tries to keep paragraph boundaries intact; only falls back to a hard
    sliding window if a single paragraph exceeds max_chars.
    """
    if len(text) <= max_chars:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buf = ""

    for p in paragraphs:
        if buf and len(buf) + 2 + len(p) > max_chars:
            chunks.append(buf)
            buf = ""

        if len(p) > max_chars:
            if buf:
                chunks.append(buf)
                buf = ""
            start = 0
            step = max_chars - overlap
            while start < len(p):
                chunks.append(p[start : start + max_chars])
                start += step
        else:
            buf = f"{buf}\n\n{p}" if buf else p

    if buf:
        chunks.append(buf)

    return chunks


def chunk_document(markdown: str, source: str) -> list[Chunk]:
    """Heading-aware chunking. Long sections are sub-split with overlap.

    The heading is prepended to each chunk's text so the LLM sees the
    section context, AND stored in metadata for use in frontend citations.
    """
    chunks: list[Chunk] = []
    sections = split_by_heading(markdown)
    idx = 0
    for heading, body in sections:
        for piece in split_long(body, MAX_CHUNK_CHARS, OVERLAP_CHARS):
            text = f"## {heading}\n\n{piece}" if heading else piece
            chunks.append(
                Chunk(text=text, source=source, chunk_idx=idx, heading=heading)
            )
            idx += 1
    return chunks


def ingest(kb_path: Path, chroma_path: Path) -> int:
    if not kb_path.is_dir():
        print(f"[error] knowledge base not found: {kb_path}", file=sys.stderr)
        return 1

    md_files = sorted(kb_path.glob("*.md"))
    if not md_files:
        print(f"[error] no .md files in {kb_path}", file=sys.stderr)
        return 1

    print(f"Reading {len(md_files)} markdown file(s) from {kb_path}")

    all_chunks: list[Chunk] = []
    for f in md_files:
        text = f.read_text(encoding="utf-8")
        chunks = chunk_document(text, source=f.name)
        print(f"  {f.name:<32} -> {len(chunks):>3} chunk(s)")
        all_chunks.extend(chunks)

    print(f"Total chunks to embed: {len(all_chunks)}")

    settings = get_settings()
    print(f"Embedding model: {settings.embedding_model}")
    embeddings = embed_texts([c.text for c in all_chunks])
    dim = len(embeddings[0]) if embeddings else 0
    print(f"Embeddings: {len(embeddings)} x {dim}-d vectors")

    chroma_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [f"{c.source}#{c.chunk_idx}" for c in all_chunks]
    metadatas = [
        {"source": c.source, "chunk_idx": c.chunk_idx, "heading": c.heading}
        for c in all_chunks
    ]
    documents = [c.text for c in all_chunks]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    print(
        f"Upserted {len(all_chunks)} chunks into '{COLLECTION_NAME}' "
        f"at {chroma_path} (collection now holds {collection.count()})"
    )
    return 0


def main() -> int:
    settings = get_settings()
    return ingest(settings.knowledge_base_path, settings.chroma_path)


if __name__ == "__main__":
    sys.exit(main())
