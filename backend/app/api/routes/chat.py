import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import NotFoundError
from app.database import get_db
from app.models.conversation import Conversation
from app.models.paper import Paper
from app.models.user import User
from app.schemas.conversation import ChatRequest, ChatResponse, Citation, ConversationDetailOut, ConversationOut
from app.services.rag_service import answer_question

router = APIRouter(tags=["chat"])


def _get_owned_paper(db: Session, paper_id: uuid.UUID, user: User) -> Paper:
    paper = db.get(Paper, paper_id)
    if paper is None or paper.owner_id != user.id:
        raise NotFoundError("PAPER_NOT_FOUND", "The requested paper could not be found.")
    return paper


@router.post("/api/papers/{paper_id}/chat", response_model=ChatResponse)
def chat_with_paper(
    paper_id: uuid.UUID,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_paper(db, paper_id, current_user)

    if payload.conversation_id:
        conv = db.get(Conversation, payload.conversation_id)
        if conv is None or conv.user_id != current_user.id or conv.paper_id != paper_id:
            raise NotFoundError("CONVERSATION_NOT_FOUND", "The requested conversation could not be found.")

    conversation, message, citations = answer_question(
        db,
        paper_id=paper_id,
        user_id=current_user.id,
        question=payload.question,
        conversation_id=payload.conversation_id,
    )

    return ChatResponse(
        conversation_id=conversation.id,
        answer=message.content,
        citations=[Citation(**c) for c in citations],
    )


@router.get("/api/papers/{paper_id}/conversations", response_model=list[ConversationOut])
def list_conversations(
    paper_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    _get_owned_paper(db, paper_id, current_user)
    conversations = db.scalars(
        select(Conversation)
        .where(Conversation.paper_id == paper_id, Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
    ).all()
    return [ConversationOut.model_validate(c) for c in conversations]


@router.get("/api/conversations/{conversation_id}", response_model=ConversationDetailOut)
def get_conversation(
    conversation_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    conv = db.get(Conversation, conversation_id)
    if conv is None or conv.user_id != current_user.id:
        raise NotFoundError("CONVERSATION_NOT_FOUND", "The requested conversation could not be found.")
    return ConversationDetailOut.model_validate(conv)
