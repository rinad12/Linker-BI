from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # OpenAI
    openai_api_key: str | None = None

    # Anthropic
    anthropic_api_key: str | None = None

    # Gemini
    google_api_key: str | None = None
    google_cse_id: str | None = None

    # Database
    database_url: PostgresDsn

    # LangGraph checkpoint store (defaults to the same DB)
    checkpoint_db_url: PostgresDsn | None = None

    # Application
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    environment: Literal["development", "staging", "production"] = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
