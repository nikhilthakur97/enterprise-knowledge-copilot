"""Typed application settings loaded from environment variables / .env file.

Defaults are chosen so the app can boot for a smoke test (e.g. /api/health)
without a .env file. Endpoints that actually need the LLM will fail loudly
later if `gemini_api_key` is empty.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-2.0-flash")

    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2"
    )
    chroma_path: Path = Field(default=Path("./data/chroma"))
    knowledge_base_path: Path = Field(default=Path("./data/hr_docs"))

    cors_origins: str = Field(default="http://localhost:5173")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
