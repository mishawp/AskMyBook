import uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .user import User
    from .document import Document


class Chat(SQLModel, table=True):
    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )
    title: str = "New Chat"
    user_id: uuid.UUID | None = Field(
        foreign_key="user.id", ondelete="SET NULL"
    )
    meta: dict = Field(default_factory=dict, sa_type=JSONB)
    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now(),
        },
    )

    user: Optional["User"] = Relationship(back_populates="chats")
    documents: list["Document"] = Relationship(
        back_populates="chats",
        sa_relationship_kwargs={"secondary": "chatdocument"},
    )
