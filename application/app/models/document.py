import uuid
from enum import Enum
from sqlalchemy import UUID as sa_UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship, func
from fastapi import UploadFile
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class ProcessingStatus(str, Enum):
    """Status of document processing in RAG pipeline"""

    PENDING = "pending"  # Document uploaded, processing not started
    PROCESSING = "processing"  # Extracting text, chunking, embedding, indexing
    COMPLETED = "completed"  # Successfully processed and indexed
    FAILED = "failed"  # Processing failed (error details in meta)


class DocumentBase(SQLModel):
    pass


class Document(DocumentBase, table=True):
    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )
    user_id: uuid.UUID | None = Field(
        foreign_key="user.id", ondelete="SET NULL"
    )

    filename: str = Field(max_length=500, index=True)
    content_type: str = Field(max_length=100)
    size_bytes: int
    storage_key: str = Field(unique=True, max_length=1000, index=True)

    processing_status: ProcessingStatus = Field(
        default=ProcessingStatus.PENDING
    )

    # Additional metadata (extraction config, errors, etc.)
    # meta: dict = Field(default_factory=dict, sa_type=JSONB)

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}
    )
    deleted_at: datetime | None = None
    is_deleted: bool = Field(default=False, index=True)

    user: "User" = Relationship(back_populates="documents")


class DocumentCreateRequest(DocumentBase):
    """Not used - FastAPI cannot handle UploadFile in Pydantic models.

    Use direct parameters in route instead:
    @router.post("/")
    async def create_document(document: UploadFile, user_id: UUID, ...)
    """

    pass


class DocumentCreateDB(DocumentBase):
    user_id: uuid.UUID
    document: UploadFile
    processing_status: ProcessingStatus = ProcessingStatus.PENDING


class DocumentPublic(DocumentBase):
    id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    processing_status: ProcessingStatus
    created_at: datetime
    is_deleted: bool


class DocumentUpdate(DocumentBase):
    processing_status: ProcessingStatus | None = None
