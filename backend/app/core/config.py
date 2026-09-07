"""
Application configuration.

Centralizes all backend settings so the rest of the codebase never
reads environment variables directly. Values are loaded from a local
.env file (see .env.example) with sane defaults for local development.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VISTARA backend"
    environment: str = "development"

    # Stored as a raw string in .env (comma-separated) and split into a list.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Reserved for Phase 5 - not used yet.
    database_url: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance - avoids re-parsing .env on every import."""
    return Settings()
