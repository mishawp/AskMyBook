"""Taskiq tasks for document ingestion and processing."""

import logging
from uuid import UUID
from sqlmodel import select

from core import get_broker, get_session, get_minio_manager
from shared.models import Document, ProcessingStatus
from shared.tasks import TaskNames

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
)

# Получаем брокер
broker = get_broker()


@broker.task(task_name=str(TaskNames.PROCESS_DOCUMENT))
async def process_document(document_id: str, storage_key: str) -> dict:
    """Обработка загруженного документа.

    Args:
        document_id: ID документа в базе данных
        storage_key: Ключ файла в MinIO

    Returns:
        dict: Результат обработки с полями success, document_id, message
    """
    logger.info("=" * 80)
    logger.info("📥 Получена задача на обработку документа")
    logger.info(f"   Document ID: {document_id}")
    logger.info(f"   Storage Key: {storage_key}")
    logger.info("=" * 80)

    try:
        # Получаем менеджеры
        minio_manager = get_minio_manager()

        # Работаем с базой данных
        async with get_session() as session:
            # Ищем документ
            stmt = select(Document).where(Document.id == UUID(document_id))
            result = await session.execute(stmt)
            document = result.scalar_one_or_none()

            if not document:
                error_msg = f"Документ с ID {document_id} не найден в БД"
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "document_id": document_id,
                    "message": error_msg,
                }

            logger.info(f"✅ Документ найден в БД:")
            logger.info(f"   Filename: {document.filename}")
            logger.info(f"   Size: {document.size_bytes} bytes")
            logger.info(f"   Content Type: {document.content_type}")
            logger.info(f"   Status: {document.processing_status}")

            # Проверяем существование файла в MinIO
            file_exists = await minio_manager.file_exists(storage_key)
            if not file_exists:
                error_msg = (
                    f"Файл {storage_key} не найден в MinIO storage"
                )
                logger.error(f"❌ {error_msg}")

                # Обновляем статус на FAILED
                document.processing_status = ProcessingStatus.FAILED
                await session.commit()

                return {
                    "success": False,
                    "document_id": document_id,
                    "message": error_msg,
                }

            logger.info(f"✅ Файл найден в MinIO storage: {storage_key}")

            # Обновляем статус на PROCESSING
            document.processing_status = ProcessingStatus.PROCESSING
            await session.commit()
            logger.info(
                f"📝 Статус документа обновлен на: {ProcessingStatus.PROCESSING}"
            )

            # Здесь будет логика обработки документа:
            # - Извлечение текста из PDF
            # - Разбиение на чанки
            # - Создание embeddings
            # - Индексация в Qdrant/Elasticsearch
            logger.info("🔄 Начинается обработка документа...")
            logger.info("   (Логика обработки будет добавлена позже)")

            # Симулируем успешную обработку
            # В реальности здесь будет вызов RAG pipeline
            document.processing_status = ProcessingStatus.COMPLETED
            await session.commit()

            logger.info(
                f"✅ Документ успешно обработан! Статус: {ProcessingStatus.COMPLETED}"
            )
            logger.info("=" * 80)

            return {
                "success": True,
                "document_id": document_id,
                "message": "Document processed successfully",
            }

    except Exception as e:
        error_msg = f"Ошибка при обработке документа: {str(e)}"
        logger.exception(f"❌ {error_msg}")

        # Пытаемся обновить статус на FAILED
        try:
            async with get_session() as session:
                stmt = select(Document).where(Document.id == UUID(document_id))
                result = await session.execute(stmt)
                document = result.scalar_one_or_none()
                if document:
                    document.processing_status = ProcessingStatus.FAILED
                    await session.commit()
        except Exception:
            logger.exception("Не удалось обновить статус документа на FAILED")

        logger.info("=" * 80)
        return {
            "success": False,
            "document_id": document_id,
            "message": error_msg,
        }
