import uuid
from fastapi import APIRouter, Depends
from models import (
    Chat,
    ChatCreateRequest,
    ChatCreateDB,
    ChatPublic,
    ChatUpdate,
)
from services import ChatService
from core.database import AsyncSessionDep, ScopedSessionDep

router = APIRouter(tags=["Chat"])


@router.get("/", response_model=list[ChatPublic])
async def get_chats(session: AsyncSessionDep):
    chat_service = ChatService(session)
    return await chat_service.get_all()


@router.post("/", response_model=ChatPublic)
async def create_chat(
    chat: ChatCreateRequest, user_id: uuid.UUID, session: AsyncSessionDep
):
    chat_service = ChatService(session)
    chat_create_db = ChatCreateDB(**chat.model_dump(), user_id=user_id)
    return await chat_service.create(chat_create_db)
