import uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .document import Document
    from .message_chunk import MessageChunk
    from .chunking_config import ChunkingConfig


class ChunkStatus(str, Enum):
    """Status of chunk"""

    ACTIVE = "active"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"


class Chunk(SQLModel, table=True):
    """Stores chunks with versioning handled via version_tag field."""

    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )

    document_id: uuid.UUID = Field(
        foreign_key="document.id", ondelete="CASCADE", index=True
    )

    chunking_config_id: uuid.UUID = Field(
        foreign_key="chunking_config.id", ondelete="RESTRICT", index=True
    )

    # Logical chunk identifier (stable across versions)
    # Combination of document_id + logical_chunk_id identifies same chunk across versions
    logical_chunk_id: str = Field(max_length=100, index=True)
    # Example: "doc123_ch1_sec2_p5-7" (document + chapter + section + pages)

    # Version tag for this chunk
    version_tag: str = Field(max_length=50, index=True)

    # The actual content
    content: str

    # Positional metadata
    start_page: int | None = None

    end_page: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None

    # Structural metadata
    section_number: str | None = Field(default=None, max_length=50)
    section_name: str | None = Field(default=None, max_length=500)
    chunk_order_in_section: int | None = None

    token_count: int | None = None
    status: ChunkStatus = Field(default=ChunkStatus.ACTIVE, index=True)
    is_latest: bool = Field(default=True, index=True)

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}, index=True
    )

    # Relationships
    document: "Document" = Relationship(back_populates="chunks")
    message_chunks: list["MessageChunk"] = Relationship(back_populates="chunk")
    chunking_config: "ChunkingConfig" = Relationship(back_populates="chunks")
