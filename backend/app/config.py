"""Configuração tipada com BaseSettings (OO) e cache via decorador @lru_cache."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Modelo OO de configurações; type hints validam valores lidos do ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    database_url: str = "sqlite:///./pylogic.db"
    jwt_secret_key: SecretStr | None = None
    jwt_access_token_expire_minutes: int = 30
    aws_region: str = "us-east-1"
    sqs_queue_url: str | None = None
    ai_api_url: str | None = None
    ai_api_key: SecretStr | None = None
    ai_model: str = "default"
    ai_timeout_seconds: float = Field(default=20.0, gt=0, le=120)


@lru_cache
def get_settings() -> Settings:
    """Lê o ambiente uma vez; @lru_cache reaproveita a instância tipada."""

    return Settings()
