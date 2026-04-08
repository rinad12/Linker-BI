from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # OpenAI
    openai_api_key: str

    # Antrhopic
    anthropic_api_key: str

    # Gemini
    google_api_key: str
    google_cse_id: str

    # Database
    database_url: PostgresDsn

    # LangGraph checkpoint store (defaults to the same DB)
    checkpoint_db_url: PostgresDsn | None = None

    # Application
    log_level: str = "INFO"
    environment: str = "development"


settings = Settings()  # type: ignore[call-arg]
