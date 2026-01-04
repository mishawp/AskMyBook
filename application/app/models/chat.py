import uuid
from sqlalchemy import UUID as sa_UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship, func, text
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class ChatBase(SQLModel):
    pass


class Chat(ChatBase, table=True):
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

    user: "User" = Relationship(back_populates="chats")


class ChatCreateRequest(ChatBase):
    pass


class ChatCreateDB(ChatBase):
    user_id: uuid.UUID
    title: str = "New Chat"
    meta: dict = Field(default_factory=dict)


class ChatPublic(ChatBase):
    id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    title: str


class ChatUpdate(ChatBase):
    title: str | None
