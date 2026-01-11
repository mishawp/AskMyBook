from fastapi import (
    APIRouter,
    HTTPException,
    status,
    UploadFile,
)
from models import Document
from schemas import (
    DocumentCreateRequest,
    DocumentCreateDB,
    DocumentPublic,
    DocumentUpdate,
    ProcessingStatus,
    ChatPublic,
)
from services.document import DocumentService
from core.database import AsyncSessionDep, ScopedSessionDep
from core.storage import MinIOManagerDep
import uuid

router = APIRouter(tags=["Document"])


@router.get("/", response_model=list[DocumentPublic])
async def get_documents(session: AsyncSessionDep):
    document_service = DocumentService(session)
    return await document_service.get_all()


@router.get("/{document_id}", response_model=DocumentPublic)
async def get_document(document_id: uuid.UUID, session: AsyncSessionDep):
    document_service = DocumentService(session)
    document = await document_service.get_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found",
        )
    return document


@router.post("/", response_model=DocumentPublic)
async def create_document(
    document: UploadFile,
    user_id: uuid.UUID,
    session: ScopedSessionDep,
    minio: MinIOManagerDep,
):
    document_service = DocumentService(session, minio)
    document_create_db = DocumentCreateDB(document=document, user_id=user_id)
    return await document_service.create(document_create_db)


@router.get("/{document_id}/chats", response_model=list[ChatPublic])
async def get_document_chats(document_id: uuid.UUID, session: AsyncSessionDep):
    """Get all chats that use this document."""
    document_service = DocumentService(session)
    chats = await document_service.get_chats(document_id)
    if chats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found",
        )
    return chats
