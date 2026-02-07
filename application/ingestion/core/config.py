"""Configuration re-exported from shared package with FastAPI-specific additions."""

from shared.core.config import (
    DBSettings,
    MinIOSettings,
    RabbitMQSettings,
    get_db_settings,
    get_minio_settings,
    get_rabbitmq_settings,
)

__all__ = [
    "DBSettings",
    "MinIOSettings",
    "RabbitMQSettings",
    "get_db_settings",
    "get_minio_settings",
    "get_rabbitmq_settings",
]
