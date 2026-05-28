# Enterprise Knowledge Copilot

An internal HR knowledge chatbot that answers employee questions — leave policies, onboarding, incident escalation, and similar — using grounded retrieval over a curated knowledge base.

> **Status:** in active development. Setup and run instructions below will be filled in as the implementation lands.

## Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | React + TypeScript + Vite | Required by the assignment; fast dev loop and typed contracts |
| Backend | FastAPI (Python) | Mature RAG / LLM ecosystem (sentence-transformers, ChromaDB) |
| LLM | Google Gemini (free tier) | Free public LLM, requires only an API key |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) | Local, free, no external API call |
| Vector store | ChromaDB (local persistent) | File-backed, simple, appropriate for a POC |
| Knowledge base | Synthetic HR markdown documents | Public/synthetic only — no PHI, no private data |

## Repository layout

```
backend/    FastAPI app, RAG pipeline, knowledge base, ingestion script
frontend/   React + TypeScript chat UI
docs/       Architecture, Responsible-AI, and assumption notes
```

## Setup

_To be filled in._

## Running locally

_To be filled in._

## Configuration

_To be filled in — Gemini API key and environment variables._

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) (to be added).

## Responsible AI

See [`docs/RESPONSIBLE_AI.md`](docs/RESPONSIBLE_AI.md) (to be added).

## Accuracy and limitations

_To be filled in._

## License

Developed as a take-home assignment. Not licensed for redistribution.
