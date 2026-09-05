import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.conversation import MessageRole


class ChatRequest(BaseModel):
    question: str
    conversation_id: uuid.UUID | None = None


class Citation(BaseModel):
    section_title: str
    chunk_id: uuid.UUID
    excerpt: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: MessageRole
    content: str
    created_at: datetime


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    answer: str
    citations: list[Citation]


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    paper_id: uuid.UUID
    title: str | None
    created_at: datetime


class ConversationDetailOut(ConversationOut):
    messages: list[MessageOut] = []
