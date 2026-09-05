import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import NotFoundError
from app.database import get_db
from app.models.figure import Figure, FigureType
from app.models.paper import Paper
from app.models.user import User
from app.schemas.figure import FigureOut
from app.services.inference_logger import log_inference
from app.services.vision import get_vision_provider

router = APIRouter(tags=["figures"])


@router.get("/api/papers/{paper_id}/figures", response_model=list[FigureOut])
def list_figures(paper_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    paper = db.get(Paper, paper_id)
    if paper is None or paper.owner_id != current_user.id:
        raise NotFoundError("PAPER_NOT_FOUND", "The requested paper could not be found.")

    figures = db.scalars(
        select(Figure).where(Figure.paper_id == paper_id).order_by(Figure.page_number)
    ).all()
    return [FigureOut.model_validate(f) for f in figures]


@router.post("/api/figures/{figure_id}/analyze", response_model=FigureOut)
def analyze_figure(figure_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    figure = db.get(Figure, figure_id)
    if figure is None:
        raise NotFoundError("FIGURE_NOT_FOUND", "The requested figure could not be found.")
    paper = db.get(Paper, figure.paper_id)
    if paper is None or paper.owner_id != current_user.id:
        raise NotFoundError("FIGURE_NOT_FOUND", "The requested figure could not be found.")

    vision = get_vision_provider()
    with log_inference(db, operation="figure_classify", provider=vision.name, model=vision.name, user_id=current_user.id) as record:
        classification = vision.classify(figure.image_path)
        record["confidence"] = classification.confidence
    description = vision.describe(figure.image_path, classification.label, figure.caption)

    figure.classification = FigureType(classification.label)
    figure.confidence = classification.confidence
    figure.description = description
    figure.vision_model = vision.name
    db.commit()
    db.refresh(figure)
    return FigureOut.model_validate(figure)
