"""Entry point for ingestion worker service.

This file provides:
1. Health checks for database, MinIO, and RabbitMQ connections
2. Startup verification before running worker
3. Logging configuration

Worker is started via: taskiq worker tasks:broker
"""

import sys

sys.path.insert(0, "/application")

import asyncio
import logging
from sqlalchemy import text

from core import (
    get_db_manager,
    get_minio_manager,
    get_broker,
    get_session,
    get_db_settings,
    get_minio_settings,
    get_rabbitmq_settings,
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def check_database_connection() -> bool:
    """Проверка подключения к PostgreSQL.

    Returns:
        bool: True если подключение успешно
    """
    try:
        logger.info("🔍 Проверка подключения к PostgreSQL...")
        db_settings = get_db_settings()
        logger.info(f"   Host: {db_settings.POSTGRES_HOST}")
        logger.info(f"   Port: {db_settings.POSTGRES_PORT}")
        logger.info(f"   Database: {db_settings.POSTGRES_DB}")

        async with get_session() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar_one()
            logger.info(f"✅ PostgreSQL подключен успешно!")
            logger.info(f"   Версия: {version[:50]}...")
            return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
        return False


async def check_minio_connection() -> bool:
    """Проверка подключения к MinIO.

    Returns:
        bool: True если подключение успешно
    """
    try:
        logger.info("🔍 Проверка подключения к MinIO...")
        minio_settings = get_minio_settings()
        logger.info(f"   Endpoint: {minio_settings.MINIO_ENDPOINT}")
        logger.info(f"   Bucket: {minio_settings.MINIO_BUCKET_NAME}")

        minio_manager = get_minio_manager()

        # Проверяем существование bucket
        async with minio_manager.get_client() as client:
            try:
                await client.head_bucket(
                    Bucket=minio_settings.MINIO_BUCKET_NAME
                )
                logger.info(
                    f"✅ MinIO подключен успешно! Bucket '{minio_settings.MINIO_BUCKET_NAME}' существует."
                )
            except Exception:
                logger.warning(
                    f"⚠️  Bucket '{minio_settings.MINIO_BUCKET_NAME}' не существует, создаю..."
                )
                await minio_manager.ensure_bucket_exists()
                logger.info(
                    f"✅ MinIO подключен! Bucket '{minio_settings.MINIO_BUCKET_NAME}' создан."
                )

            return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к MinIO: {e}")
        return False


async def check_rabbitmq_connection() -> bool:
    """Проверка подключения к RabbitMQ.

    Returns:
        bool: True если подключение успешно
    """
    try:
        logger.info("🔍 Проверка подключения к RabbitMQ...")
        rabbitmq_settings = get_rabbitmq_settings()
        logger.info(f"   Host: {rabbitmq_settings.RABBITMQ_HOST}")
        logger.info(f"   Port: {rabbitmq_settings.RABBITMQ_PORT}")
        logger.info(f"   VHost: {rabbitmq_settings.RABBITMQ_VHOST}")

        broker = get_broker()
        await broker.startup()
        logger.info("✅ RabbitMQ подключен успешно!")
        await broker.shutdown()
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к RabbitMQ: {e}")
        return False


async def startup_checks() -> bool:
    """Выполняет все проверки при запуске.

    Returns:
        bool: True если все проверки прошли успешно
    """
    logger.info("=" * 80)
    logger.info("🚀 INGESTION WORKER SERVICE - STARTUP CHECKS")
    logger.info("=" * 80)

    # Проверяем все соединения
    db_ok = await check_database_connection()
    logger.info("")

    minio_ok = await check_minio_connection()
    logger.info("")

    rabbitmq_ok = await check_rabbitmq_connection()
    logger.info("")

    logger.info("=" * 80)
    if db_ok and minio_ok and rabbitmq_ok:
        logger.info("✅ Все проверки пройдены успешно!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📌 Для запуска worker используйте команду:")
        logger.info("   taskiq worker tasks:broker")
        logger.info("")
        logger.info("Worker будет принимать задачи от FastAPI сервиса:")
        logger.info("   - process_document: обработка загруженных документов")
        logger.info("")
        return True
    else:
        logger.error("❌ Некоторые проверки не прошли!")
        logger.error(
            "Проверьте конфигурацию в .env файле и доступность сервисов."
        )
        logger.info("=" * 80)
        return False


async def main():
    """Основная функция для запуска проверок."""
    success = await startup_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
