# Responsible AI and Governance

## Intended use

A demo internal HR knowledge assistant for a fictional company ("Lumina").
It answers questions grounded in a synthetic policy knowledge base —
leave, onboarding, incident response, expenses, benefits, conduct, IT
security, remote work. Designed to be defensible in an interview, not
deployed.

## Out of scope

Things this assistant explicitly should **not** be used for:

- Anything safety-critical (medical, financial, legal advice).
- Decisions about individual employees (performance, compensation,
  termination). The assistant has no employee data.
- Authoritative interpretation of policy. People Operations is the
  source of truth; this is a lookup convenience.
- Anything not in the synthetic knowledge base. The refusal path is
  there exactly to handle this — the system says "I don't know based on
  the available HR documents" rather than guessing.

## Controls implemented

The flow has multiple layered controls, each addressing a specific
failure mode.

| Failure mode | Where it's caught |
|---|---|
| Hallucination | System prompt instructs the model to answer ONLY from context. Low temperature (0.2) keeps the model close to the retrieved text. Inline citations (`[leave-policy.md]`) make every claim traceable. |
| Out-of-domain question | Retriever drops chunks below similarity 0.30. Empty context + system prompt's exact refusal phrase ("I don't know based on the available HR documents.") force a clean refusal instead of a confident wrong answer. |
| User can't tell where an answer came from | Citations are required inline by the system prompt, AND every assistant message has an expandable Sources panel showing the chunk text, filename, heading, and similarity score. |
| User can't correct the model | Per-message thumbs up / thumbs down. Thumbs-down opens an optional comment box. Submission appends to `backend/data/feedback.jsonl` with the question, answer, rating, and timestamp — self-contained for offline review. |
| Prompt injection via user content | System prompt is passed via Gemini's `system_instruction` field, not in the conversation history. User-turn content cannot override system rules without exploiting the LLM itself, which is a model-level concern outside POC scope. |
| LLM call fails | Three-attempt retry with exponential backoff for transient errors only. On final failure, the chat endpoint returns the refusal phrase and empty sources at HTTP 200 — the user sees a sensible message instead of a 500. The actual error is logged server-side at WARN. |
| Telemetry leakage | ChromaDB anonymous telemetry is disabled. No outbound calls except the explicit Gemini API call. |

## Accuracy and limitations

### What works well

- Concrete-fact questions with clear policy text: "How many sick days?",
  "What is the parental leave for primary caregivers?", "What's the
  expense per-diem for dinner?". Top-1 similarity is consistently
  ≥ 0.65 and the answer cites the right doc.
- Refusal: out-of-domain questions ("capital of France?") return zero
  sources and produce the exact refusal phrase.
- Multi-turn conversation: a follow-up like "What about sick leave?"
  after a leave question correctly stays grounded in `leave-policy.md`.

### Known weaknesses

- **Tabular content.** The incident-response severity table (`P0 → 15
  minutes`, `P1 → 30 minutes`, etc.) is a Markdown table. Vector
  embeddings of tables are weaker than narrative prose, so the SLA-table
  chunk doesn't always make top-1 even on a direct "P0 SLA" question.
  The model usually still finds the right number from neighbouring
  chunks, but it's a real failure mode. Fix: hybrid search (BM25 +
  vector) plus a reranker, on the production roadmap.
- **Paraphrase drift.** Even with low temperature, the model paraphrases
  the source. Numeric facts ("20 working days", "15 minutes") have
  survived every test, but exact-quote questions could in principle
  drift. Fix: post-hoc fact-check against the source chunks.
- **Synthetic data only.** The knowledge base is fictional. Real-world
  HR policies have edge cases this dataset doesn't cover (multi-region
  payroll, jurisdiction-specific leave, union contracts).
- **No grounding score returned to the user.** We could surface a
  confidence number, but raw cosine similarity is misleading and there's
  no way to compute calibrated confidence without a labelled eval set.
  Better to show citations and let the user judge than to present a
  fake number.
- **Single-tenant.** No per-user / per-document access control.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Incorrect answer presented confidently | Low | Inline citations + Sources panel let the user check the source in seconds. The user is always told where the answer came from. |
| Over-reliance on the bot for authoritative interpretation | Medium | The "Out of scope" framing in this doc plus a real production deployment would surface a "consult People Ops for binding decisions" disclaimer. |
| Prompt injection through retrieved content (a malicious doc could try to override the system prompt) | Low for synthetic data; medium for real | System instructions are passed in a separate channel from conversation history; this isn't bulletproof but raises the bar. Production fix: content filters at ingestion + output filters before return. |
| PII leak via feedback comments | Low | Comment is optional and capped at 1000 chars. **Production must add server-side PII redaction** before persisting. Documented in `ASSUMPTIONS.md` as a known gap. |
| Stale knowledge base | Inevitable | Re-running `python -m app.rag.ingest` is idempotent; in production this would be a scheduled job triggered on document updates. |
| Model API downtime | Low | The graceful-degradation path returns the refusal phrase + 200 OK with the actual error logged at WARN. The user sees a useful message; monitoring sees the failure. |

## Feedback handling

Each row in `backend/data/feedback.jsonl` looks like:

```json
{
  "timestamp": "2026-05-28T22:53:18.445491+00:00",
  "message_id": "3702f322-b3b6-46cf-8ff6-a882feee2cb7",
  "rating": "up",
  "comment": "clear and concise",
  "question": "How many sick days do I get?",
  "answer": "Employees receive 10 paid sick days per calendar year [leave-policy.md, benefits.md]..."
}
```

Server-stamped UTC timestamp (never trust the client). Question + answer
attached so the row is self-contained for offline analysis without
joining against any other log.

In production, this becomes a relational table with a unique constraint
on `(user_id, message_id)` so a single user can't spam ratings, plus a
retention policy and PII redaction on the comment field. Documented in
`ARCHITECTURE.md` under Scale-out.
