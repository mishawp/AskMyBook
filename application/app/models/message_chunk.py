import uuid
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message
    from .chunk import Chunk


class MessageChunk(SQLModel, table=True):
    """Links messages to chunks used in generation.

    DENORMALIZED: store chunk version for quick filtering.
    """

    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )

    message_id: uuid.UUID = Field(
        foreign_key="message.id", ondelete="CASCADE", index=True
    )

    chunk_id: uuid.UUID = Field(
        foreign_key="chunk.id", ondelete="CASCADE", index=True
    )

    chunk_version_tag: str = Field(max_length=50, index=True)

    # Retrieval metadata
    relevance_score: float | None = None
    rank: int | None = None
    included_in_context: bool = Field(default=True)

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}
    )

    # Relationships
    message: "Message" = Relationship(back_populates="message_chunks")
    chunk: "Chunk" = Relationship(back_populates="message_chunks")
