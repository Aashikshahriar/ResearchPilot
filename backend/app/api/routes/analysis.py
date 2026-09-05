import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import BadRequestError, NotFoundError
from app.database import get_db
from app.models.paper import Paper
from app.models.user import User
from app.schemas.analysis import ComparisonRequest, ComparisonResponse, ComparisonResult, SummaryResponse
from app.services.analysis_service import compare_papers
from app.services.paper_service import generate_summary
import json

router = APIRouter(tags=["analysis"])


def _get_owned_paper(db: Session, paper_id: uuid.UUID, user: User) -> Paper:
    paper = db.get(Paper, paper_id)
    if paper is None or paper.owner_id != user.id:
        raise NotFoundError("PAPER_NOT_FOUND", "The requested paper could not be found.")
    return paper


@router.post("/api/papers/{paper_id}/summarize", response_model=SummaryResponse)
def summarize_paper(
    paper_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    paper = _get_owned_paper(db, paper_id, current_user)
    source_text = "\n\n".join(s.content for s in paper.sections) or (paper.abstract or "")
    if not source_text:
        raise BadRequestError("NO_CONTENT", "This paper has no extracted content to summarize yet.")

    generate_summary(db, paper, source_text)
    db.commit()
    db.refresh(paper)
    return SummaryResponse(paper_id=paper.id, summary=paper.ai_summary or "")


@router.post("/api/papers/compare", response_model=ComparisonResponse)
def compare_papers_endpoint(
    payload: ComparisonRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if len(payload.paper_ids) < 2:
        raise BadRequestError("INSUFFICIENT_PAPERS", "Select at least two papers to compare.")

    for pid in payload.paper_ids:
        _get_owned_paper(db, pid, current_user)

    analysis = compare_papers(db, payload.paper_ids)
    data = json.loads(analysis.content)
    return ComparisonResponse(paper_ids=payload.paper_ids, comparison=ComparisonResult(**data))
