import uuid
from fastapi import APIRouter, HTTPException, status
from models import Chat
from schemas import (
    ChatCreateRequest,
    ChatCreateDB,
    ChatPublic,
    ChatUpdate,
    DocumentPublic,
)
from services import ChatService
from core import AsyncSessionDep, ScopedSessionDep
from dependencies import CurrentUser

router = APIRouter(tags=["Chat"])


@router.get("/", response_model=list[ChatPublic])
async def get_chats(session: AsyncSessionDep):
    chat_service = ChatService(session)
    return await chat_service.get_all()


@router.get("/{chat_id}", response_model=ChatPublic)
async def get_chat(chat_id: uuid.UUID, session: AsyncSessionDep):
    chat_service = ChatService(session)
    chat = await chat_service.get_by_id(chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat with id {chat_id} not found",
        )
    return chat


@router.post("/", response_model=ChatPublic)
async def create_chat(
    chat: ChatCreateRequest,
    current_user: CurrentUser,
    session: AsyncSessionDep,
):
    chat_service = ChatService(session)
    chat_create_db = ChatCreateDB(**chat.model_dump(), user_id=current_user.id)
    return await chat_service.create(chat_create_db)


@router.get("/{chat_id}/documents", response_model=list[DocumentPublic])
async def get_chat_documents(chat_id: uuid.UUID, session: AsyncSessionDep):
    """Get all documents associated with a chat."""
    chat_service = ChatService(session)
    documents = await chat_service.get_documents(chat_id)
    if documents is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat with id {chat_id} not found",
        )
    return documents


@router.post("/{chat_id}/documents/{document_id}", response_model=ChatPublic)
async def add_document_to_chat(
    chat_id: uuid.UUID, document_id: uuid.UUID, session: AsyncSessionDep
):
    """Add a document to a chat."""
    chat_service = ChatService(session)
    chat = await chat_service.add_document(chat_id, document_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat with id {chat_id} or document with id {document_id} not found",
        )
    return chat


@router.delete("/{chat_id}/documents/{document_id}", response_model=ChatPublic)
async def remove_document_from_chat(
    chat_id: uuid.UUID, document_id: uuid.UUID, session: AsyncSessionDep
):
    """Remove a document from a chat."""
    chat_service = ChatService(session)
    chat = await chat_service.remove_document(chat_id, document_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat with id {chat_id} not found",
        )
    return chat
