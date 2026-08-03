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

    # Seed realistic demo data (alerts, lifecycle runs, agent
    # analytics, model usage, knowledge docs) on application
    # startup so the frontend is populated without manual setup.
    SEED_DEMO_DATA: bool = True

    # Repository configuration
    REPOSITORY_TYPE: str = "memory"

    # MongoDB configuration
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "openops"

    GEMINI_API_KEY: str = ""

    # Redis cache connection (optional; in-memory fallback)
    CACHE_URL: str = ""

# ------------------------------------------------------------------
# OpenRouter
# ------------------------------------------------------------------

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "openrouter/free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

# ------------------------------------------------------------------
# Embeddings & Knowledge Base
# ------------------------------------------------------------------

    # "hashing" (local, deterministic) or "gemini"
    EMBEDDING_PROVIDER: str = "hashing"
    EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIMENSION: int = 768

    KNOWLEDGE_COLLECTION: str = "knowledge_vectors"
    VECTOR_SEARCH_INDEX: str = "vector_index"
    INCIDENT_MEMORY_COLLECTION: str = "incident_memory"

# ------------------------------------------------------------------
# Google ADK bridge
# ------------------------------------------------------------------

    # Default model used by ADK-wrapped agents. Leave empty to let
    # the google-adk SDK fall back to its own default model.
    ADK_MODEL: str = ""
    ADK_APP_NAME: str = "openops"
    ADK_SESSION_TIMEOUT_S: int = 30

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
