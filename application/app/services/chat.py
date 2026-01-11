import uuid
from sqlmodel import select
from sqlalchemy.orm import selectinload
from models import Chat, Document
from schemas import (
    ChatCreateRequest,
    ChatCreateDB,
    ChatPublic,
    ChatUpdate,
)
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Chat]:
        stmt = select(Chat).order_by(Chat.id)
        result: Result = await self.session.execute(stmt)
        chats = result.scalars().all()
        return list(chats)

    async def get_by_id(self, chat_id: uuid.UUID) -> Chat | None:
        """Get chat by ID with documents loaded."""
        stmt = (
            select(Chat)
            .where(Chat.id == chat_id)
            .options(selectinload(Chat.documents))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, chat: ChatCreateDB) -> Chat:
        db_chat = Chat(**chat.model_dump())
        self.session.add(db_chat)
        await self.session.commit()
        return db_chat

    async def add_document(
        self, chat_id: uuid.UUID, document_id: uuid.UUID
    ) -> Chat | None:
        """Add a document to a chat. Returns None if chat or document not found."""
        chat = await self.get_by_id(chat_id)
        if not chat:
            return None

        # Load the document
        stmt = select(Document).where(Document.id == document_id)
        result = await self.session.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            return None

        # Add document to chat if not already added
        if document not in chat.documents:
            chat.documents.append(document)
            await self.session.commit()

        return chat

    async def remove_document(
        self, chat_id: uuid.UUID, document_id: uuid.UUID
    ) -> Chat | None:
        """Remove a document from a chat. Returns None if chat not found."""
        chat = await self.get_by_id(chat_id)
        if not chat:
            return None

        # Find and remove the document
        document_to_remove = None
        for doc in chat.documents:
            if doc.id == document_id:
                document_to_remove = doc
                break

        if document_to_remove:
            chat.documents.remove(document_to_remove)
            await self.session.commit()

        return chat

    async def get_documents(self, chat_id: uuid.UUID) -> list[Document] | None:
        """Get all documents associated with a chat. Returns None if chat not found."""
        chat = await self.get_by_id(chat_id)
        if not chat:
            return None

        return chat.documents
