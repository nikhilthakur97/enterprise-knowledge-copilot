// Typed API client.
//
// One function per backend endpoint. All errors are normalized to the
// `ApiError` class so the UI can react to HTTP status codes (e.g. show
// the configuration-required message on 503, surface validation
// details on 422) without parsing strings.

import type {
  ChatRequest,
  ChatResponse,
  FeedbackRequest,
  FeedbackResponse,
  HealthResponse,
} from '../types';

const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  /** HTTP status code, or 0 for a network failure. */
  public readonly status: number;
  /** Parsed response body (FastAPI 422 errors include a `detail` array). */
  public readonly body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

async function request<TRes>(
  path: string,
  init: RequestInit = {},
): Promise<TRes> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Network error';
    throw new ApiError(message, 0, null);
  }

  let body: unknown = null;
  const text = await response.text();
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }

  if (!response.ok) {
    const detail =
      body && typeof body === 'object' && 'detail' in body
        ? (body as { detail: unknown }).detail
        : response.statusText;
    const message =
      typeof detail === 'string' ? detail : `HTTP ${response.status}`;
    throw new ApiError(message, response.status, body);
  }

  return body as TRes;
}

function postJson<TRes>(path: string, payload: unknown): Promise<TRes> {
  return request<TRes>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function postChat(req: ChatRequest): Promise<ChatResponse> {
  return postJson<ChatResponse>('/api/chat', req);
}

export function postFeedback(
  req: FeedbackRequest,
): Promise<FeedbackResponse> {
  return postJson<FeedbackResponse>('/api/feedback', req);
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/api/health');
}
