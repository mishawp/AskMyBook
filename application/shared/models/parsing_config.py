import uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship, func
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .parsed_document import ParsedDocument


class ParsingConfig(SQLModel, table=True):
    """Stores parsing algorithm configurations.

    Tracks which parsing strategy and parameters were used to extract
    text and structure from documents.
    Examples: pymupdf_default, pdfplumber_v1, marker_ocr_enabled
    """

    __tablename__ = "parsing_config"

    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )

    # Human-readable name
    name: str = Field(max_length=200, unique=True, index=True)

    # Version identifier
    version: str = Field(max_length=50)

    # Parser type (pymupdf, pdfplumber, marker, etc.)
    parser_type: str = Field(max_length=100)

    # Configuration parameters
    config: dict = Field(sa_type=JSONB)
    # Example: {
    #     "extract_images": false,
    #     "extract_tables": true,
    #     "ocr_enabled": false,
    #     "ocr_language": "rus+eng",
    #     "preserve_formatting": true
    # }

    # Description
    description: str | None = None

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}
    )

    # Relationships
    parsed_documents: list["ParsedDocument"] = Relationship(
        back_populates="parsing_config"
    )