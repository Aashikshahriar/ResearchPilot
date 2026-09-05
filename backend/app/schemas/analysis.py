import uuid

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    paper_id: uuid.UUID
    summary: str


class ComparisonRequest(BaseModel):
    paper_ids: list[uuid.UUID]


class ComparisonResult(BaseModel):
    research_problem: str
    methodology: str
    datasets: str
    models: str
    results: str
    strengths: str
    limitations: str
    key_differences: str


class ComparisonResponse(BaseModel):
    paper_ids: list[uuid.UUID]
    comparison: ComparisonResult
