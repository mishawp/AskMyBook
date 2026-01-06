"""Модуль для работы с MinIO хранилищем."""

from typing import Annotated, AsyncGenerator
from contextlib import asynccontextmanager
import aioboto3
from botocore.config import Config
from fastapi import Depends

from .config import MinIOSettings, get_minio_settings


class MinIOManager:
    """Менеджер для работы с MinIO через aioboto3."""

    def __init__(self, settings: MinIOSettings):
        """Инициализация MinIO менеджера.

        Args:
            settings: Настройки подключения к MinIO
        """
        self.settings = settings
        self.session = aioboto3.Session()
        self._config = Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "adaptive"},
        )

    @asynccontextmanager
    async def get_client(self):
        """Асинхронный контекстный менеджер для получения S3 клиента.

        Yields:
            Асинхронный S3 клиент aioboto3
        """
        async with self.session.client(
            "s3",
            endpoint_url=self.settings.MINIO_ENDPOINT,
            aws_access_key_id=self.settings.MINIO_ROOT_USER,
            aws_secret_access_key=self.settings.MINIO_ROOT_PASSWORD,
            use_ssl=self.settings.MINIO_SECURE,
            config=self._config,
        ) as client:
            yield client

    async def ensure_bucket_exists(self):
        """Проверяет существование bucket и создает его при необходимости."""
        async with self.get_client() as client:
            try:
                await client.head_bucket(
                    Bucket=self.settings.MINIO_BUCKET_NAME
                )
            except Exception:
                await client.create_bucket(
                    Bucket=self.settings.MINIO_BUCKET_NAME
                )

    async def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Загружает файл в MinIO.

        Args:
            file_data: Данные файла в виде байтов
            object_name: Имя объекта в MinIO
            content_type: MIME тип файла

        Returns:
            Имя загруженного объекта
        """
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.settings.MINIO_BUCKET_NAME,
                Key=object_name,
                Body=file_data,
                ContentType=content_type,
            )
        return object_name

    async def download_file(self, object_name: str) -> bytes:
        """Скачивает файл из MinIO.

        Args:
            object_name: Имя объекта в MinIO

        Returns:
            Данные файла в виде байтов
        """
        async with self.get_client() as client:
            response = await client.get_object(
                Bucket=self.settings.MINIO_BUCKET_NAME, Key=object_name
            )
            async with response["Body"] as stream:
                return await stream.read()

    async def delete_file(self, object_name: str) -> None:
        """Удаляет файл из MinIO.

        Args:
            object_name: Имя объекта в MinIO
        """
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.settings.MINIO_BUCKET_NAME, Key=object_name
            )

    async def file_exists(self, object_name: str) -> bool:
        """Проверяет существование файла в MinIO.

        Args:
            object_name: Имя объекта в MinIO

        Returns:
            True если файл существует, False иначе
        """
        async with self.get_client() as client:
            try:
                await client.head_object(
                    Bucket=self.settings.MINIO_BUCKET_NAME, Key=object_name
                )
                return True
            except Exception:
                return False

    async def get_file_url(
        self, object_name: str, expires_in: int = 3600
    ) -> str:
        """Генерирует presigned URL для файла.

        Args:
            object_name: Имя объекта в MinIO
            expires_in: Время жизни ссылки в секундах (по умолчанию 1 час)

        Returns:
            Presigned URL для скачивания файла
        """
        async with self.get_client() as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.settings.MINIO_BUCKET_NAME,
                    "Key": object_name,
                },
                ExpiresIn=expires_in,
            )
            return url


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


async def init_minio() -> None:
    """Инициализирует MinIO при запуске приложения.

    Создает bucket если он не существует.
    """
    settings = get_minio_settings()
    manager = MinIOManager(settings)
    await manager.ensure_bucket_exists()


# Типы для dependency injection
MinIOManagerDep = Annotated[MinIOManager, Depends(get_minio_manager)]
