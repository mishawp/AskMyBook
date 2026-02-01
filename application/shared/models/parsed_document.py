import uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .document import Document
    from .parsing_config import ParsingConfig
    from .chunk import Chunk


class ParsingStatus(str, Enum):
    """Status of document parsing"""

    PENDING = "pending"  # Parsing not started
    PROCESSING = "processing"  # Extracting text and structure
    COMPLETED = "completed"  # Successfully parsed
    FAILED = "failed"  # Parsing failed


class ParsedDocument(SQLModel, table=True):
    """Stores the result of parsing a document with a specific config.

    Represents extracted text and structural metadata from the original document.
    One Document can have multiple ParsedDocuments (different parsing configs/versions).
    """

    __tablename__ = "parsed_document"

    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )

    document_id: uuid.UUID = Field(
        foreign_key="document.id", ondelete="CASCADE", index=True
    )

    parsing_config_id: uuid.UUID = Field(
        foreign_key="parsing_config.id", ondelete="RESTRICT", index=True
    )

    # Version tag for this parsed version
    version_tag: str = Field(max_length=50, index=True)

    # Extracted text stored in MinIO (like Document.storage_key)
    storage_key: str | None = Field(default=None, max_length=1000)
    text_size: int | None = None  # Size in bytes

    # Document structure metadata
    page_count: int | None = None

    # Structural metadata (TOC, sections, etc.)
    structure: dict | None = Field(default=None, sa_type=JSONB)
    # Example: {
    #     "toc": [
    #         {"title": "Chapter 1", "page": 1, "level": 1},
    #         {"title": "Section 1.1", "page": 5, "level": 2}
    #     ],
    #     "sections": [
    #         {"name": "Chapter 1", "start_page": 1, "end_page": 20},
    #         {"name": "Section 1.1", "start_page": 5, "end_page": 10}
    #     ]
    # }

    # Processing status
    status: ParsingStatus = Field(default=ParsingStatus.PENDING, index=True)
    error_message: str | None = None

    # Flags
    is_latest: bool = Field(default=True, index=True)

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}, index=True
    )

    # Relationships
    document: "Document" = Relationship(back_populates="parsed_documents")
    parsing_config: "ParsingConfig" = Relationship(
        back_populates="parsed_documents"
    )
    chunks: list["Chunk"] = Relationship(back_populates="parsed_document")
