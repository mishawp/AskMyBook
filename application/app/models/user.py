import uuid
from sqlmodel import Field, SQLModel, Relationship, func
from pydantic import EmailStr
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chat import Chat
    from .document import Document


class User(SQLModel, table=True):
    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )
    email: EmailStr = Field(index=True)
    password: str  # TODO: password type?
    chats: list["Chat"] = Relationship(back_populates="user")
    documents: list["Document"] = Relationship(back_populates="user")
