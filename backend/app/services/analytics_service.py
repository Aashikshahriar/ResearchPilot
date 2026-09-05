import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai_inference import AIInference
from app.models.conversation import Conversation
from app.models.experiment import Experiment
from app.models.paper import Paper
from app.schemas.dashboard import DashboardOut, DashboardStats
from app.schemas.experiment import ExperimentOut
from app.schemas.paper import PaperListItem


def build_dashboard(db: Session, user_id: uuid.UUID) -> DashboardOut:
    paper_count = db.scalar(select(func.count(Paper.id)).where(Paper.owner_id == user_id)) or 0
    experiment_count = db.scalar(select(func.count(Experiment.id)).where(Experiment.owner_id == user_id)) or 0
    conversation_count = db.scalar(select(func.count(Conversation.id)).where(Conversation.user_id == user_id)) or 0

    ai_insight_count = (
        db.scalar(
            select(func.count(AIInference.id)).where(AIInference.user_id == user_id, AIInference.success.is_(True))
        )
        or 0
    )

    recent_papers = db.scalars(
        select(Paper).where(Paper.owner_id == user_id).order_by(Paper.created_at.desc()).limit(5)
    ).all()
    recent_experiments = db.scalars(
        select(Experiment).where(Experiment.owner_id == user_id).order_by(Experiment.created_at.desc()).limit(5)
    ).all()

    return DashboardOut(
        stats=DashboardStats(
            paper_count=paper_count,
            experiment_count=experiment_count,
            ai_insight_count=ai_insight_count,
            conversation_count=conversation_count,
        ),
        recent_papers=[PaperListItem.model_validate(p) for p in recent_papers],
        recent_experiments=[ExperimentOut.model_validate(e) for e in recent_experiments],
    )
