# Enterprise Knowledge Copilot

An internal HR knowledge chatbot that answers employee questions —
leave policy, onboarding, incident escalation, expenses, benefits,
remote work, code of conduct, IT security — using **grounded
retrieval** over a curated knowledge base.

Every answer is generated only from retrieved policy chunks, every
claim is cited inline, and questions outside the knowledge base trigger
an explicit refusal rather than a guess.

## What it does

- **Grounded answers.** Top-k vector retrieval over a chunked HR
  knowledge base; the LLM is instructed to answer only from retrieved
  context.
- **Inline citations** like `[leave-policy.md]` plus an expandable
  Sources panel showing the chunk text, heading, and similarity score.
- **Explicit refusal** when retrieval returns nothing useful (no
  hallucinated answers).
- **Per-message feedback** (Yes / No, with an optional comment box on
  No), persisted to a JSONL audit log.
- **Conversation history** — multi-turn questions stay coherent
  because prior turns are sent on every request.
- **Accessibility built in:** keyboard navigation, focus management,
  `aria-live`, `aria-busy`, `prefers-reduced-motion` support, WCAG-AA
  contrast.

## Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | React 19 + TypeScript + Vite | Required by the assignment; fast dev loop and typed contracts |
| Backend | FastAPI (Python 3.10+) | Mature RAG / LLM ecosystem (sentence-transformers, ChromaDB) |
| LLM | Google Gemini (`gemini-2.5-flash`) | Free tier, fast, single-key auth |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Local, free, 384-d, no external API call per query |
| Vector store | ChromaDB (local persistent) | File-backed, cosine retrieval, no DB server to run |
| Feedback log | Append-only JSONL | Line-atomic, easy to grep / load into pandas |

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full picture
and a POC-vs-production scale-out table.

## Quick start

You'll need:

- **Python 3.10+** (tested on 3.13)
- **Node.js 20+** and **npm 10+** (tested on Node 22)
- A free **Gemini API key** from <https://aistudio.google.com/apikey>

### 1. Backend

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (pinned in requirements.txt)
pip install -r requirements.txt

# Configure
cp .env.example .env
# then open .env and paste your GEMINI_API_KEY

# Build the vector index from the knowledge base
# (idempotent — safe to re-run after editing docs)
python -m app.rag.ingest

# Run the API on http://localhost:8000
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

In a second terminal:

```bash
cd frontend

# Install dependencies (pinned in package-lock.json)
npm install

# Configure (only needed if the backend isn't on localhost:8000)
cp .env.example .env.local

# Run the dev server on http://localhost:5173
npm run dev
```

Open <http://localhost:5173> and try:

- *"How many days of annual leave do I get?"*
- *"What is the response time for a P0 incident?"*
- *"Walk me through the new-hire onboarding process."*

For a question outside the knowledge base — *"What's the capital of
France?"* — the assistant should refuse rather than guess.

## API reference

All endpoints are JSON. Schemas live in
[`backend/app/schemas.py`](backend/app/schemas.py).

### `GET /api/health`

Liveness probe.

```json
{ "status": "ok", "model": "gemini-2.5-flash" }
```

### `POST /api/chat`

Stateless chat. The frontend sends the full conversation on each call.

```json
// Request
{
  "messages": [
    { "role": "user", "content": "How many sick days do I get?" }
  ]
}

// Response
{
  "message_id": "3702f322-b3b6-46cf-8ff6-a882feee2cb7",
  "answer": "Employees receive 10 paid sick days per calendar year [leave-policy.md]...",
  "sources": [
    {
      "file": "leave-policy.md",
      "heading": "Sick leave",
      "snippet": "Employees receive 10 paid sick days per calendar year...",
      "score": 0.81
    }
  ],
  "latency_ms": 1342
}
```

### `POST /api/feedback`

Records a thumbs-up / thumbs-down for a previous assistant message.

```json
// Request
{
  "message_id": "3702f322-b3b6-46cf-8ff6-a882feee2cb7",
  "rating": "up",
  "comment": "Clear and cited the right doc.",
  "question": "How many sick days do I get?",
  "answer": "Employees receive 10 paid sick days..."
}

// Response
{ "status": "ok" }
```

Feedback is appended to `backend/data/feedback.jsonl`. The file is
gitignored.

## Project structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, router registration
│   │   ├── config.py          # Pydantic settings from .env
│   │   ├── schemas.py         # Pydantic API contracts
│   │   ├── rag/
│   │   │   ├── embeddings.py  # sentence-transformers wrapper
│   │   │   ├── ingest.py      # CLI: chunk + embed + upsert into Chroma
│   │   │   ├── retriever.py   # Top-k vector search with similarity floor
│   │   │   └── prompt.py      # System prompt + grounded user message
│   │   ├── services/
│   │   │   └── llm.py         # Gemini client: retry, timeout, structured errors
│   │   └── routes/
│   │       ├── chat.py        # POST /api/chat
│   │       └── feedback.py    # POST /api/feedback
│   ├── data/
│   │   ├── hr_docs/           # 8 synthetic markdown policy docs
│   │   ├── chroma/            # gitignored — built by ingest.py
│   │   └── feedback.jsonl     # gitignored — written by /api/feedback
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/client.ts      # Typed fetch wrapper with ApiError
│   │   ├── components/        # ChatWindow, ChatInput, MessageBubble, Sources, FeedbackButtons
│   │   ├── hooks/useChat.ts   # Conversation state, optimistic UI, error mapping
│   │   ├── types.ts           # Hand-mirrored from backend/app/schemas.py
│   │   ├── App.tsx
│   │   └── App.css
│   ├── package.json
│   └── .env.example
├── docs/
│   ├── ARCHITECTURE.md        # Components, request lifecycle, scale-out
│   ├── RESPONSIBLE_AI.md      # Intended use, controls, limitations, risks
│   └── ASSUMPTIONS.md         # Assumption log + "what I'd improve with more time"
└── README.md
```

## Configuration

### Backend — `backend/.env`

| Variable | Default | Notes |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | From <https://aistudio.google.com/apikey> |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Free-tier model with quota at the time of writing |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Downloaded automatically on first run (~80 MB) |
| `CHROMA_PATH` | `./data/chroma` | Where the vector index is persisted |
| `KNOWLEDGE_BASE_PATH` | `./data/hr_docs` | Where the markdown knowledge base lives |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated list of allowed frontend origins |

### Frontend — `frontend/.env.local`

| Variable | Default | Notes |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Override only if the backend runs elsewhere |

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — components, request
  lifecycle, storage decisions, and the POC-vs-production scale-out
  table. Includes a mermaid diagram.
- [`docs/RESPONSIBLE_AI.md`](docs/RESPONSIBLE_AI.md) — intended use,
  out-of-scope use, the layered controls (grounding, refusal,
  citations, feedback, graceful-degradation retry path), known
  weaknesses, and a risk table.
- [`docs/ASSUMPTIONS.md`](docs/ASSUMPTIONS.md) — what I decided rather
  than discovered, plus a ranked **"what I'd improve with more time"**
  list.

## Notes

- **The knowledge base is fully synthetic.** "Lumina" is not a real
  company. No PHI, no PII, no real customer or employee data.
- **No authentication.** Anyone who can reach the backend can call the
  endpoints. CORS is locked to `localhost:5173` in development. Auth
  is on the production roadmap in `docs/ARCHITECTURE.md`.
- **POC scale.** Local ChromaDB, JSONL feedback, single uvicorn worker.
  The app is stateless and would scale horizontally as-is; the
  storage layers are the parts that change. See the scale-out table in
  `docs/ARCHITECTURE.md`.

## License

Developed as a take-home assignment. Not licensed for redistribution.
