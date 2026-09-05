from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.chunk import PaperChunk
from app.models.experiment import Experiment
from app.models.paper import Paper
from app.models.user import User
from app.schemas.dashboard import DashboardOut, SearchResultItem
from app.services.analytics_service import build_dashboard

router = APIRouter(tags=["dashboard"])


@router.get("/api/dashboard", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return build_dashboard(db, current_user.id)


@router.get("/api/search", response_model=list[SearchResultItem])
def search(q: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    results: list[SearchResultItem] = []
    if not q or len(q.strip()) < 2:
        return results

    like = f"%{q}%"

    papers = db.scalars(
        select(Paper).where(Paper.owner_id == current_user.id, Paper.title.ilike(like)).limit(10)
    ).all()
    for p in papers:
        results.append(
            SearchResultItem(type="paper", id=p.id, title=p.title or p.filename, snippet=(p.abstract or "")[:200], paper_id=p.id)
        )

    chunks = db.scalars(
        select(PaperChunk)
        .join(Paper, Paper.id == PaperChunk.paper_id)
        .where(Paper.owner_id == current_user.id, PaperChunk.content.ilike(like))
        .limit(10)
    ).all()
    for c in chunks:
        results.append(
            SearchResultItem(type="chunk", id=c.id, title=c.paper.title or c.paper.filename, snippet=c.content[:200], paper_id=c.paper_id)
        )

    experiments = db.scalars(
        select(Experiment).where(Experiment.owner_id == current_user.id, Experiment.name.ilike(like)).limit(10)
    ).all()
    for e in experiments:
        results.append(SearchResultItem(type="experiment", id=e.id, title=e.name, snippet=e.notes or ""))

    return results
