import uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chunk import Chunk


class ChunkingConfig(SQLModel, table=True):
    """Stores chunking algorithm configurations.

    Tracks which chunking strategy and parameters were used.
    Examples: recursive_512_64, semantic_768_128, chapter_aware_v1
    """

    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )

    # Human-readable name
    name: str = Field(max_length=200, unique=True, index=True)

    # Version identifier
    version: str = Field(max_length=50)

    # Algorithm type (recursive, semantic, chapter-aware, etc.)
    algorithm: str = Field(max_length=100)

    # Configuration parameters (chunk_size, overlap, etc.)
    config: dict = Field(sa_type=JSONB)
    # Example: {
    #     "chunk_size": 512,
    #     "overlap": 64,
    #     "separator": "\n\n",
    #     "keep_separator": true
    # }

    # Description
    description: str | None = None

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}
    )

    # Relationships
    chunks: list["Chunk"] = Relationship(back_populates="chunking_config")
