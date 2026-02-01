"""MinIO storage module re-exported from shared with FastAPI-specific dependencies."""

from typing import Annotated
from fastapi import Depends

from shared.core.storage import MinIOManager, create_minio_manager
from shared.core.config import MinIOSettings, get_minio_settings


# Глобальная переменная для хранения единственного экземпляра MinIOManager
_minio_manager: MinIOManager | None = None


def get_minio_manager(
    settings: Annotated[MinIOSettings, Depends(get_minio_settings)],
) -> MinIOManager:
    """Dependency injection фабрика для получения MinIOManager.

    Args:
        settings: Настройки MinIO (инжектируются через Depends)

    Returns:
        Единственный экземпляр MinIOManager
    """
    global _minio_manager
    if _minio_manager is None:
        _minio_manager = MinIOManager(settings)
    return _minio_manager


async def create_bucket_if_not_exists() -> None:
    """Создаёт bucket в MinIO, если он не существует."""
    settings = get_minio_settings()
    manager = MinIOManager(settings)
    await manager.ensure_bucket_exists()


async def clear_bucket() -> None:
    """Удаляет все файлы из bucket.

    Опасно для production (удаляет все файлы).
    """
    settings = get_minio_settings()
    manager = MinIOManager(settings)

    async with manager.get_client() as client:
        paginator = client.get_paginator("list_objects_v2")
        async for page in paginator.paginate(
            Bucket=settings.MINIO_BUCKET_NAME
        ):
            objects = page.get("Contents", [])
            if objects:
                await client.delete_objects(
                    Bucket=settings.MINIO_BUCKET_NAME,
                    Delete={
                        "Objects": [{"Key": obj["Key"]} for obj in objects]
                    },
                )


async def init_minio() -> None:
    """Инициализирует MinIO при запуске приложения.

    Создаёт bucket если он не существует, затем очищает его.
    Используется для отладки.
    """
    await create_bucket_if_not_exists()
    await clear_bucket()


# Типы для dependency injection
MinIOManagerDep = Annotated[MinIOManager, Depends(get_minio_manager)]
