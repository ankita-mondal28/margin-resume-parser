"""
Centralized application settings.

All configuration is read from environment variables (via a local .env
file during development). Nothing sensitive is hard-coded here — this
file only defines *names*, *types*, and *safe defaults*.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Required ---
    groq_api_key: str

    # --- Optional, with sensible defaults ---
    groq_model: str = "openai/gpt-oss-120b"
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_file_size_mb: int = 8
    rate_limit_per_minute: int = 10

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings loader.

    Raises a clear, actionable error at startup if GROQ_API_KEY is
    missing, instead of failing confusingly later on the first request.
    """
    try:
        return Settings()
    except Exception as exc:  # pydantic ValidationError
        raise RuntimeError(
            "Missing or invalid configuration. Did you create a `.env` file "
            "in `backend/` with a valid GROQ_API_KEY? "
            "See `.env.example` for the required format."
        ) from exc
