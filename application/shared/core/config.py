"""Shared configuration settings for all services."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class DBSettings(BaseSettings):
    """Класс настроек подключения к базе данных PostgreSQL."""

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(extra="ignore")


class MinIOSettings(BaseSettings):
    """Класс настроек подключения к MinIO."""

    MINIO_ENDPOINT: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "askmybook"

    model_config = SettingsConfigDict(extra="ignore")


@lru_cache()
def get_db_settings() -> DBSettings:
    """Фабрика настроек базы данных с кешированием."""
    return DBSettings()


@lru_cache()
def get_minio_settings() -> MinIOSettings:
    """Фабрика настроек MinIO с кешированием."""
    return MinIOSettings()
