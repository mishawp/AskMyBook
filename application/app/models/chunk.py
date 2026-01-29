import uuid
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .parsed_document import ParsedDocument
    from .message_chunk import MessageChunk
    from .chunking_config import ChunkingConfig
    from .indexing_config import IndexingConfig


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

    parsed_document_id: uuid.UUID = Field(
        foreign_key="parsed_document.id", ondelete="CASCADE", index=True
    )

    chunking_config_id: uuid.UUID = Field(
        foreign_key="chunking_config.id", ondelete="RESTRICT", index=True
    )

    indexing_config_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="indexing_config.id",
        ondelete="RESTRICT",
        index=True,
    )

    # Logical chunk identifier (stable across versions)
    # Combination of parsed_document_id + logical_chunk_id identifies same chunk across versions
    logical_chunk_id: str = Field(max_length=100, index=True)
    # Example: "ch1_sec2_p5-7" (chapter + section + pages)

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
    parsed_document: "ParsedDocument" = Relationship(back_populates="chunks")
    message_chunks: list["MessageChunk"] = Relationship(back_populates="chunk")
    chunking_config: "ChunkingConfig" = Relationship(back_populates="chunks")
    indexing_config: "IndexingConfig" = Relationship(back_populates="chunks")
