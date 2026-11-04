from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    """Environment-backed configuration; secrets are never committed."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    frontend_origin: str = "http://localhost:3000"
    database_url: str = "postgresql+psycopg://jarvis:change-me@localhost:5432/jarvis"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    app_secret_key: str = "unsafe-development-secret-change-me"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    llm_provider: str = ""
    openai_api_key: str | None = None
    openai_model: str | None = None

    @model_validator(mode="after")
    def require_secure_production_secret(self):
        if self.app_env == "production" and (self.app_secret_key == "unsafe-development-secret-change-me" or len(self.app_secret_key) < 32):
            raise ValueError("APP_SECRET_KEY must be a random value of at least 32 characters in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
