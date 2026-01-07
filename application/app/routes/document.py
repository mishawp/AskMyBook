from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Header,
)
from fastapi.responses import JSONResponse
from models import (
    Document,
    DocumentCreateRequest,
    DocumentCreateDB,
    DocumentPublic,
    DocumentUpdate,
    ProcessingStatus,
)
from services.document import DocumentService
from core.database import AsyncSessionDep, ScopedSessionDep
from core.storage import MinIOManagerDep
import uuid
from typing import Optional

router = APIRouter(tags=["Document"])


@router.get("/", response_model=list[DocumentPublic])
async def get_documents(session: AsyncSessionDep):
    document_service = DocumentService(session)
    return await document_service.get_all()


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
