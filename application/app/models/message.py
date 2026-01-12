import uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .chat import Chat
    from .message_chunk import MessageChunk
    from .rag_config import RAGConfig
    from .prompt_template import PromptTemplate


class Message(SQLModel, table=True):
    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )

    chat_id: uuid.UUID = Field(
        foreign_key="chat.id", ondelete="CASCADE", index=True
    )

    # Message content (can be updated for streaming)
    user_message: str
    rewrite_message: str | None
    ai_message: str | None

    # FK to prompt templates
    prompt_template_id: uuid.UUID | None = Field(
        foreign_key="prompttemplate.id", ondelete="RESTRICT"
    )
    # Переписывание запроса пользователя,
    # чтобы уловить контекст чата
    rewrite_prompt_template_id: uuid.UUID | None = Field(
        foreign_key="prompttemplate.id", ondelete="RESTRICT"
    )

    # Sequence number within chat (for ordering)
    sequence_number: int = Field(index=True)

    # For streaming: track if content is complete
    is_complete: bool = Field(default=False)

    rag_config_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="ragconfig.id",
        ondelete="RESTRICT",
    )

    # Additional metadata (token counts, generation params, etc.)
    meta: dict = Field(default_factory=dict, sa_type=JSONB)

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}, index=True
    )
    updated_at: datetime = Field(
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now(),
        },
    )

    # Relationships
    chat: "Chat" = Relationship(back_populates="messages")
    message_chunks: list["MessageChunk"] = Relationship(
        back_populates="message"
    )
    rag_config: Optional["RAGConfig"] = Relationship(back_populates="messages")
    prompt_template: Optional["PromptTemplate"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Message.prompt_template_id]"}
    )
    rewrite_prompt_template: Optional["PromptTemplate"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Message.rewrite_prompt_template_id]"
        }
    )
