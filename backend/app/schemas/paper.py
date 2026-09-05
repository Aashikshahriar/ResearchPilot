import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.paper import ProcessingStatus


class PaperOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    title: str | None
    authors: list[str] | None
    abstract: str | None
    ai_summary: str | None
    status: ProcessingStatus
    processing_error: str | None
    page_count: int | None
    file_size_bytes: int
    created_at: datetime


class PaperListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    title: str | None
    status: ProcessingStatus
    page_count: int | None
    created_at: datetime


class PaperStatusOut(BaseModel):
    id: uuid.UUID
    status: ProcessingStatus
    processing_error: str | None = None


class SectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    content: str
    order_index: int
    page_start: int | None
    page_end: int | None


class PaperDetailOut(PaperOut):
    sections: list[SectionOut] = []
