import uuid
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from models import Document, Chat
from schemas import (
    DocumentCreateRequest,
    DocumentCreateDB,
    DocumentPublic,
    DocumentUpdate,
    ProcessingStatus,
)
from core import MinIOManager, _broker
from shared.tasks import TaskNames


# Task stub for sending messages to ingestion service
# Actual implementation is in ingestion/tasks.py
@_broker.task(task_name=str(TaskNames.PROCESS_DOCUMENT))
async def _process_document_task(document_id: str, storage_key: str) -> dict:
    """Client-side stub for sending document to ingestion service.

    This function body never executes - it's only for task registration.
    The actual task runs in the ingestion worker service.
    """
    pass


class DocumentService:
    def __init__(
        self, session: AsyncSession, minio: MinIOManager | None = None
    ):
        self.session = session
        self.minio = minio

    @staticmethod
    def get_storage_key(
        user_id: uuid.UUID, document_id: uuid.UUID, filename: str
    ) -> str:
        """Generates unique storage key for document.

        Format: {user_id}/{document_id}_{filename}
        This ensures uniqueness even if user uploads files with same name.
        """
        return f"{user_id}/{document_id}_{filename}"

    async def get_all(self) -> list[Document]:
        stmt = select(Document).order_by(Document.created_at)
        result: Result = await self.session.execute(stmt)
        documents = result.scalars().all()
        return list(documents)

    async def create(
        self,
        document: DocumentCreateDB,
    ) -> Document:
        file = document.document
        user_id = document.user_id
        filename = file.filename or "untitled"
        content_type = file.content_type or "application/octet-stream"

        # Create DB record first to get document_id
        db_document = Document(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            size_bytes=0,  # Will update after upload
            storage_key="",  # Will update after generating key
            processing_status=document.processing_status,
        )
        self.session.add(db_document)
        await self.session.flush()  # Get ID without committing

        # Generate storage key with document_id
        storage_key = self.get_storage_key(user_id, db_document.id, filename)
        db_document.storage_key = storage_key

        try:
            # Get file size from underlying file object (SpooledTemporaryFile)
            file.file.seek(0, 2)  # Seek to end (sync operation)
            size_bytes = file.file.tell()
            file.file.seek(0)  # Reset to beginning
            db_document.size_bytes = size_bytes

            # Upload file to MinIO using streaming
            await self.minio.upload_file_stream(
                file_stream=file.file,
                object_name=storage_key,
                content_type=content_type,
            )

            await self.session.commit()

            # Отправляем задачу на обработку документа в ingestion сервис
            await _process_document_task.kiq(
                document_id=str(db_document.id),
                storage_key=storage_key,
            )

            return db_document

        except Exception as e:
            await self.session.rollback()
            # Try to cleanup MinIO if upload succeeded but DB failed
            try:
                if await self.minio.file_exists(storage_key):
                    await self.minio.delete_file(storage_key)
            except Exception:
                pass  # Ignore cleanup errors
            raise e

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        """Get document by ID with chats loaded."""
        stmt = (
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.chats))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_chats(self, document_id: uuid.UUID) -> list[Chat] | None:
        """Get all chats that use this document. Returns None if document not found."""
        document = await self.get_by_id(document_id)
        if not document:
            return None

        return document.chats
