from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    database_url: str = "postgresql+psycopg://researchpilot:researchpilot@localhost:5432/researchpilot"

    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    llm_provider: str = "mock"
    # Comma-separated provider names tried in order, e.g. "gemini,groq,mistral,openai".
    # When set, the factory builds a FallbackLLMProvider that tries each configured
    # provider in turn and falls through to the next on any failure, always ending
    # with the offline mock provider as a guaranteed-available last resort.
    llm_fallback_order: str = ""

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    gemini_api_key: str = ""
    gemini_chat_model: str = "gemini-3.6-flash"
    gemini_embedding_model: str = "gemini-embedding-001"

    mistral_api_key: str = ""
    mistral_chat_model: str = "mistral-small-latest"
    mistral_embedding_model: str = "mistral-embed"

    groq_api_key: str = ""
    groq_chat_model: str = "openai/gpt-oss-120b"

    # Fixed dimension for the pgvector column (see alembic/versions/0001_initial_schema.py).
    # Every embedding, regardless of which provider produced it, is normalized
    # (truncated/padded) to this length so retrieval stays consistent even when
    # the embedding provider changes between requests in a fallback chain.
    embedding_dim: int = 1536

    vision_provider: str = "mock"
    gemini_vision_model: str = "gemini-3.6-flash"

    backend_cors_origins: str = "http://localhost:3000"
    max_upload_mb: int = 25
    storage_dir: str = "./storage"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
