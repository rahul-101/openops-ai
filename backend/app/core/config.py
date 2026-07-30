from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root: openops-ai/
BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    APP_NAME: str = "OpenOps AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    LOG_LEVEL: str = "INFO"

    # Repository configuration
    REPOSITORY_TYPE: str = "memory"

    # MongoDB configuration
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "openops"

    GEMINI_API_KEY: str = ""

# ------------------------------------------------------------------
# OpenRouter
# ------------------------------------------------------------------

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "openrouter/free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()