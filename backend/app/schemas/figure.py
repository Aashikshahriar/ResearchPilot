import uuid

from pydantic import BaseModel, ConfigDict

from app.models.figure import FigureType


class FigureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    paper_id: uuid.UUID
    page_number: int
    image_path: str
    caption: str | None
    classification: FigureType | None
    confidence: float | None
    description: str | None
    vision_model: str | None
