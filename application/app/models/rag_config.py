import uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .prompt_template import PromptTemplate
    from .message import Message


class RAGConfigStatus(str, Enum):
    """Status of RAG configuration"""

    ACTIVE = "active"
    TESTING = "testing"
    DEPRECATED = "deprecated"


class RAGConfig(SQLModel, table=True):
    """Stores versioned RAG configurations."""

    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )

    config_name: str = Field(max_length=200, index=True)
    version_tag: str = Field(max_length=50, index=True)

    # FK to prompt template
    prompt_template_id: uuid.UUID = Field(
        foreign_key="prompttemplate.id",
        ondelete="RESTRICT",
    )

    # DENORMALIZED: full config snapshot for easy access
    full_config: dict = Field(sa_type=JSONB)
    # Example: {
    #     "embedding_model": "all-mpnet-base-v2",
    #     "embedding_version": "v1",
    #     "chunk_version_tag": "v1.0",
    #     "retrieval": {
    #         "top_k": 10,
    #         "use_reranker": true,
    #         "hybrid_alpha": 0.5
    #     },
    #     "generation": {
    #         "model": "mistral-7b",
    #         "temperature": 0.7,
    #         "max_tokens": 512
    #     }
    # }

    status: RAGConfigStatus = Field(default=RAGConfigStatus.ACTIVE, index=True)
    description: str | None = None

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}, index=True
    )

    # Relationships
    prompt_template: "PromptTemplate" = Relationship(back_populates="rag_config")
    messages: list["Message"] = Relationship(back_populates="rag_config")
