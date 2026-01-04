from sqlmodel import select
from models import (
    Chat,
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

    async def create(self, chat: ChatCreateDB) -> Chat:
        db_chat = Chat(**chat.model_dump())
        self.session.add(db_chat)
        await self.session.commit()
        return db_chat
