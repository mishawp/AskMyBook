import uuid
from sqlmodel import SQLModel, Field
from datetime import datetime


class ChatBase(SQLModel):
    pass


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
