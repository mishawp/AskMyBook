import uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from enum import Enum

if TYPE_CHECKING:
    from .rag_config import RAGConfig
    from .message import Message


class PromptTemplateStatus(str, Enum):
    """Status of prompt template"""

    ACTIVE = "active"
    DRAFT = "draft"
    DEPRECATED = "deprecated"


class PromptIntent(str, Enum):
    """Defines the intent or purpose of a prompt"""

    REWRITE = "rewrite"
    GENERATE = "generate"


class PromptTemplate(SQLModel, table=True):
    """Stores versioned prompt templates.

    Simplified: template_name + version_tag is unique.
    All metadata in JSONB for flexibility.
    """

    __tablename__ = "prompt_template"

    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )

    template_name: str = Field(max_length=200, index=True)
    version_tag: str = Field(max_length=50, index=True)
    template: str

    # Store type, language, variables in JSONB
    meta: dict = Field(default_factory=dict, sa_type=JSONB)
    # Example: {
    #     "type": "qa",
    #     "language": "en",
    #     "variables": ["context", "question"],
    #     "description": "Default QA prompt"
    # }

    status: PromptTemplateStatus = Field(
        default=PromptTemplateStatus.ACTIVE, index=True
    )

    intent: PromptIntent = Field(index=True)

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}, index=True
    )

    # Relationships
    rag_config: Optional["RAGConfig"] = Relationship(
        back_populates="prompt_template",
        sa_relationship_kwargs={"uselist": False},
    )
    messages_for_generation: list["Message"] = Relationship(
        back_populates="prompt_template",
        sa_relationship_kwargs={
            "foreign_keys": "[Message.prompt_template_id]"
        },
    )
    messages_for_rewrite: list["Message"] = Relationship(
        back_populates="rewrite_prompt_template",
        sa_relationship_kwargs={
            "foreign_keys": "[Message.rewrite_prompt_template_id]"
        },
    )
