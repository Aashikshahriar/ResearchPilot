import uuid

from pydantic import BaseModel

from app.schemas.experiment import ExperimentOut
from app.schemas.paper import PaperListItem


class DashboardStats(BaseModel):
    paper_count: int
    experiment_count: int
    ai_insight_count: int
    conversation_count: int


class DashboardOut(BaseModel):
    stats: DashboardStats
    recent_papers: list[PaperListItem]
    recent_experiments: list[ExperimentOut]


class SearchResultItem(BaseModel):
    type: str  # "paper" | "chunk" | "experiment"
    id: uuid.UUID
    title: str
    snippet: str
    paper_id: uuid.UUID | None = None
