import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.deps import get_current_user
from app.core.errors import BadRequestError, NotFoundError
from app.database import get_db
from app.models.paper import Paper, ProcessingStatus
from app.models.user import User
from app.schemas.paper import PaperDetailOut, PaperListItem, PaperOut, PaperStatusOut
from app.services.paper_service import process_paper_job

router = APIRouter(prefix="/api/papers", tags=["papers"])
settings = get_settings()

ALLOWED_CONTENT_TYPES = {"application/pdf"}


def _get_owned_paper(db: Session, paper_id: uuid.UUID, user: User) -> Paper:
    paper = db.get(Paper, paper_id)
    if paper is None:
        raise NotFoundError("PAPER_NOT_FOUND", "The requested paper could not be found.")
    if paper.owner_id != user.id:
        raise NotFoundError("PAPER_NOT_FOUND", "The requested paper could not be found.")
    return paper


@router.post("", response_model=PaperOut, status_code=201)
async def upload_paper(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise BadRequestError("INVALID_FILE_TYPE", "Only PDF files are supported.")

    contents = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise BadRequestError("FILE_TOO_LARGE", f"File exceeds the {settings.max_upload_mb}MB limit.")

    paper_id = uuid.uuid4()
    papers_dir = Path(settings.storage_dir) / "papers" / str(current_user.id)
    papers_dir.mkdir(parents=True, exist_ok=True)
    file_path = papers_dir / f"{paper_id}.pdf"
    file_path.write_bytes(contents)

    paper = Paper(
        id=paper_id,
        owner_id=current_user.id,
        filename=file.filename or "paper.pdf",
        file_path=str(file_path),
        file_size_bytes=len(contents),
        status=ProcessingStatus.uploaded,
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    background_tasks.add_task(process_paper_job, paper.id)

    return PaperOut.model_validate(paper)


@router.get("", response_model=list[PaperListItem])
def list_papers(
    q: str | None = None,
    status_filter: ProcessingStatus | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Paper).where(Paper.owner_id == current_user.id)
    if status_filter:
        stmt = stmt.where(Paper.status == status_filter)
    if q:
        stmt = stmt.where(Paper.title.ilike(f"%{q}%"))
    stmt = stmt.order_by(Paper.created_at.desc())
    papers = db.scalars(stmt).all()
    return [PaperListItem.model_validate(p) for p in papers]


@router.get("/{paper_id}", response_model=PaperDetailOut)
def get_paper(paper_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    paper = _get_owned_paper(db, paper_id, current_user)
    return PaperDetailOut.model_validate(paper)


@router.delete("/{paper_id}", status_code=204)
def delete_paper(paper_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    paper = _get_owned_paper(db, paper_id, current_user)
    file_path = Path(paper.file_path)
    db.delete(paper)
    db.commit()
    if file_path.exists():
        file_path.unlink(missing_ok=True)
    return None


@router.get("/{paper_id}/status", response_model=PaperStatusOut)
def get_status(paper_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    paper = _get_owned_paper(db, paper_id, current_user)
    return PaperStatusOut(id=paper.id, status=paper.status, processing_error=paper.processing_error)


@router.post("/{paper_id}/process", response_model=PaperStatusOut)
def reprocess_paper(
    paper_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper = _get_owned_paper(db, paper_id, current_user)
    paper.status = ProcessingStatus.uploaded
    paper.processing_error = None
    db.commit()
    background_tasks.add_task(process_paper_job, paper.id)
    return PaperStatusOut(id=paper.id, status=paper.status)
