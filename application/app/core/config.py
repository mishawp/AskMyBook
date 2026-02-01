"""Configuration re-exported from shared package with FastAPI-specific additions."""

from shared.core.config import (
    DBSettings,
    MinIOSettings,
    get_db_settings,
    get_minio_settings,
)

__all__ = [
    "DBSettings",
    "MinIOSettings",
    "get_db_settings",
    "get_minio_settings",
]
