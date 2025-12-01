from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DRAFT_HUB_", env_file=".env", extra="ignore")

    app_name: str = "Draft Hub API"
    database_url: str = "sqlite:///./docs.db"
    secret_key: str = "dev-secret-key"
    jwt_expiration_minutes: int = 60
    redis_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
