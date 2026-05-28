"""FastAPI application entry point.

Wires up CORS and exposes the liveness probe. Feature endpoints (chat,
feedback) are mounted in later commits.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.schemas import HealthResponse

settings = get_settings()

app = FastAPI(
    title="Enterprise Knowledge Copilot",
    description="Internal HR knowledge chatbot with grounded RAG responses.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Liveness probe. Returns ok if the service is running."""
    return HealthResponse()
