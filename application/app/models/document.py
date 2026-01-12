import uuid
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from enum import Enum

if TYPE_CHECKING:
    from .user import User
    from .chat import Chat
    from .chunk import Chunk


class ProcessingStatus(str, Enum):
    """Status of document processing in RAG pipeline"""

    PENDING = "pending"  # Document uploaded, processing not started
    PROCESSING = "processing"  # Extracting text, chunking, embedding, indexing
    COMPLETED = "completed"  # Successfully processed and indexed
    FAILED = "failed"  # Processing failed (error details in meta)


class Document(SQLModel, table=True):
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

    user: Optional["User"] = Relationship(back_populates="documents")
    chats: list["Chat"] = Relationship(
        back_populates="documents",
        sa_relationship_kwargs={"secondary": "chat_document"},
    )
    chunks: list["Chunk"] = Relationship(back_populates="document")
