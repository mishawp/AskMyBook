import uuid
from sqlmodel import SQLModel
from fastapi import UploadFile
from datetime import datetime

from models.document import ProcessingStatus


class DocumentBase(SQLModel):
    pass


class DocumentCreateRequest(DocumentBase):
    """Not used - FastAPI cannot handle UploadFile in Pydantic models.

    Use direct parameters in route instead:
    @router.post("/")
    async def create_document(document: UploadFile, user_id: UUID, ...)
    """

    pass


class DocumentCreateDB(DocumentBase):
    user_id: uuid.UUID
    document: UploadFile
    processing_status: ProcessingStatus = ProcessingStatus.PENDING


class DocumentPublic(DocumentBase):
    id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    processing_status: ProcessingStatus
    created_at: datetime
    is_deleted: bool


class DocumentUpdate(DocumentBase):
    processing_status: ProcessingStatus | None = None
