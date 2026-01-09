import uuid
from sqlmodel import Field, SQLModel, func


class ChatDocument(SQLModel, table=True):
    """Link table for many-to-many relationship between Chat and Document.

    A chat can reference multiple documents for context, and a document
    can be used in multiple chats.
    """

    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )

    chat_id: uuid.UUID = Field(foreign_key="chat.id", ondelete="CASCADE")
    document_id: uuid.UUID = Field(
        foreign_key="document.id", ondelete="CASCADE"
    )
