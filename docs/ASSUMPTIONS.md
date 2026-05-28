# Assumptions and "What I'd Improve With More Time"

## Assumptions

Things I decided rather than discovered. Each one is defensible; some
would be wrong for production.

### Data and domain

- **The knowledge base is fully synthetic.** "Lumina" is not a real
  company. Specific numbers (20 days leave, 15-minute P0 SLA, $1,000
  home-office stipend) are plausible but invented. No PHI, no PII, no
  real customer or employee data is referenced.
- **Eight documents is a representative POC sample.** They cover the
  three example questions in the assignment plus five more for breadth.
  At ~830 lines / 4,600 words / 78 chunks, retrieval is meaningful but
  the index is small enough to ingest in seconds.
- **Some topics intentionally appear in multiple docs** (parental leave
  in `leave-policy.md` and `benefits.md`, remote-work security in
  `remote-work.md` and `it-security.md`) so the retriever has to pick
  the better-grounded source. This is what makes RAG demonstrably
  useful versus naive keyword match.

### Stack and infrastructure

- **Python 3.10+ is acceptable.** I tested on 3.13. The code uses
  `str | None` syntax which requires 3.10+.
- **Node 22 + npm 10 is acceptable.** Tested on 22.15.1.
- **The Gemini free tier is enough for grading.** The free quota covers
  the request volume any reviewer would generate. `gemini-2.5-flash`
  was picked because the free-tier quota for `gemini-2.0-flash` was
  silently set to zero by the time of writing.
- **A single uvicorn worker is enough.** The app is stateless and would
  run multi-worker as-is; the single process is just simpler to demo.
- **Local file-backed ChromaDB is enough.** A managed vector DB would
  cost money, add operational surface, and not change the demo.
- **JSONL is enough for feedback.** A real DB would be better but adds
  setup complexity. Append-only writes are line-atomic on POSIX for
  short records, which is good enough for a POC's audit log.

### API and contracts

- **Frontend types are hand-mirrored from `backend/app/schemas.py`.**
  The honest production move is `openapi-typescript` in a build step
  to generate types from the live OpenAPI schema. For 6 types this
  isn't worth the extra dep; the trade-off is documented inline at
  the top of `frontend/src/types.ts`.
- **No auth.** Anyone who can reach the backend can call the chat and
  feedback endpoints. CORS is the only gate, locked down to
  `localhost:5173`.
- **Conversation history lives client-side.** The backend is stateless
  by design; every `/api/chat` call sends the full history. Trade-off:
  no resume across browser tabs/devices.
- **`message_id` is generated server-side.** Frontend uses it to attach
  feedback. The chat endpoint doesn't store any chat history keyed by
  `message_id`, so feedback alone is uncorrelatable. The frontend
  re-sends `question` and `answer` in the feedback payload to make
  each JSONL row self-contained.

### Retrieval and prompting

- **Heading-aware chunking with 800-char chunks and 100-char overlap.**
  Tuned empirically; ~200 tokens fits comfortably in MiniLM's
  256-token context window. Heading-aware preserves semantic
  boundaries; pure character splitting would slice mid-policy.
- **`MIN_SIMILARITY = 0.30` similarity floor.** Tuned empirically against
  the synthetic dataset. Low enough to keep useful matches, high enough
  to drop noise. The grounding instructions in the system prompt are
  the primary safeguard; this is a backstop.
- **Top-k = 4.** Empirical sweet spot for short policy chunks. More
  context dilutes the signal and risks confusing the model.
- **Temperature 0.2.** This is grounded retrieval, not creative
  writing. We want the model to stick close to the retrieved text.

### Frontend

- **Plain CSS, no UI library.** No Tailwind, MUI, shadcn. The
  assignment specifically asks not to optimise for UI polish, and a
  framework on a 200-line app earns nothing on the rubric.
- **Light mode only.** Dark mode means a colour variant for every
  bubble / source / button state. Not worth the time.
- **Plain text "Yes" / "No" feedback buttons.** Not 👍/👎 emoji.
  Emoji rendering is wildly inconsistent across OS / browser, and
  screen readers narrate them in weird ways.

## What I'd improve with more time

Ranked by impact-per-hour, not alphabetically.

### High impact

1. **Streaming responses.** Server-Sent Events on the backend, an
   `EventSource` on the frontend. The current ~1.5s wait for a
   complete answer is fine but feels slow next to streaming chat
   UIs. Biggest perceived UX improvement available.
2. **Hybrid retrieval + cross-encoder reranker.** BM25 (via Whoosh
   or rank-bm25) merged with the existing vector search, then a
   cheap cross-encoder rerank on the merged top-20 to produce the
   final top-4. Fixes the tabular-content weakness called out in
   `RESPONSIBLE_AI.md`.
3. **Golden Q&A evaluation set.** ~30 hand-curated question / expected-
   answer-substring pairs that run on every commit (or nightly). This
   is the single highest-leverage thing for catching regressions in
   retrieval quality.

### Medium impact

4. **Real DB for feedback.** Postgres + SQLAlchemy with a unique
   constraint on `(user_id, message_id)`, plus PII redaction on the
   comment field before persistence.
5. **Auto-generated frontend types.** `openapi-typescript` in a
   `prebuild` step. Removes the "remember to update both sides" drift
   risk.
6. **Auth + per-document access control.** OIDC for the front door,
   metadata filters at retrieval time so users only see chunks they're
   allowed to see.
7. **Docker Compose** for the full stack so a reviewer can run
   everything with one command.
8. **CI workflow.** GitHub Actions running `npm run build` + `npm run
   lint` for the frontend and `pytest` + `ruff` for the backend on
   every PR.

### Lower impact, still worth it

9. **Tests.** Pytest for the RAG pipeline (chunking edge cases,
   retrieval similarity bounds), Playwright for the UI happy path
   plus the refusal path.
10. **Observability.** Structured JSON logs from FastAPI, basic metrics
    (request count, latency, retrieval hit-rate, refusal rate, feedback
    aggregates) exposed at `/metrics` for Prometheus scraping.
11. **Conversation persistence.** Optional server-side conversation
    storage keyed by user, so chat resumes across devices.
12. **Per-user rate limiting.** Defends the Gemini quota from abusive
    callers and gives a clean failure mode.
13. **Empty-state quick prompts.** Click-to-fill example questions
    instead of just text examples. Tiny UX win.
14. **Markdown rendering in the assistant bubble.** Gemini sometimes
    emits markdown bullets / bold; we render them as plain text. A
    small markdown component would let those render properly.
