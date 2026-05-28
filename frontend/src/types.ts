// Mirror of backend/app/schemas.py.
//
// This file is the single source of truth for API types on the frontend.
// Keep it in sync when the backend contract changes. For production we
// would auto-generate this from the FastAPI OpenAPI schema (e.g.
// `openapi-typescript`); for a take-home, hand-mirroring keeps the
// dependency footprint small and the types easy to inspect.

export type Role = 'user' | 'assistant' | 'system';

export interface Message {
  role: Role;
  content: string;
}

export interface ChatRequest {
  messages: Message[];
}

export interface Source {
  file: string;
  snippet: string;
  score: number;
  heading: string | null;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  latency_ms: number;
  message_id: string;
}

export type Rating = 'up' | 'down';

export interface FeedbackRequest {
  message_id: string;
  rating: Rating;
  comment?: string;
  question?: string;
  answer?: string;
}

export interface FeedbackResponse {
  ok: boolean;
}

export interface HealthResponse {
  status: 'ok';
}
