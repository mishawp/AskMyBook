"""MinIO storage module for ingestion service (without FastAPI dependencies)."""

from shared.core.storage import MinIOManager, create_minio_manager


# Глобальная переменная для хранения единственного экземпляра MinIOManager
_minio_manager: MinIOManager | None = None


def get_minio_manager() -> MinIOManager:
    """Получить глобальный экземпляр MinIOManager (singleton).

    Returns:
        MinIOManager: Менеджер для работы с MinIO
    """
    global _minio_manager
    if _minio_manager is None:
        _minio_manager = create_minio_manager()
    return _minio_manager
