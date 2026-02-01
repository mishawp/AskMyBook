import uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chunk import Chunk


class IndexingConfig(SQLModel, table=True):
    """Stores vector indexing configurations.

    Tracks which embedding model and vector indexing strategy were used.
    Examples: mpnet-faiss-flat-v1, minilm-qdrant-hnsw-v2
    """

    __tablename__ = "indexing_config"

    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )

    # Human-readable name
    name: str = Field(max_length=200, unique=True, index=True)

    # Version identifier
    version: str = Field(max_length=50)

    # Embedding model (e.g., "all-mpnet-base-v2", "all-MiniLM-L6-v2")
    embedding_model: str = Field(max_length=100)

    # Index type (e.g., "faiss_flat", "faiss_hnsw", "qdrant")
    index_type: str = Field(max_length=100)

    # Configuration parameters
    config: dict = Field(sa_type=JSONB)
    # Example: {
    #     "embedding_dimension": 768,
    #     "index_type": "faiss_flat",
    #     "normalize_embeddings": true,
    #     "batch_size": 32,
    #     "index_path": "./faiss_index",
    #     "nlist": 100,
    #     "nprobe": 10,
    #     "extra_options": {}
    # }

    # Description
    description: str | None = None

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}
    )

    # Relationships
    chunks: list["Chunk"] = Relationship(back_populates="indexing_config")
