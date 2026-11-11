"""Configuração tipada com BaseSettings (OO) e cache via decorador @lru_cache."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Modelo OO de configurações; type hints validam valores lidos do ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./pylogic.db"
    jwt_secret_key: SecretStr | None = None
    jwt_access_token_expire_minutes: int = 30
    aws_region: str = "us-east-1"
    sqs_queue_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Lê o ambiente uma vez; @lru_cache reaproveita a instância tipada."""

    return Settings()
