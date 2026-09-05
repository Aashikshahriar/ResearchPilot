import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExperimentCreate(BaseModel):
    name: str
    model: str | None = None
    dataset: str | None = None
    learning_rate: float | None = None
    batch_size: int | None = None
    epochs: int | None = None
    notes: str | None = None


class ExperimentUpdate(BaseModel):
    name: str | None = None
    model: str | None = None
    dataset: str | None = None
    learning_rate: float | None = None
    batch_size: int | None = None
    epochs: int | None = None
    notes: str | None = None


class MetricOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    value: float
    step: int | None
    created_at: datetime


class MetricCreate(BaseModel):
    name: str
    value: float
    step: int | None = None


class ExperimentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    model: str | None
    dataset: str | None
    learning_rate: float | None
    batch_size: int | None
    epochs: int | None
    notes: str | None
    created_at: datetime


class ExperimentDetailOut(ExperimentOut):
    metrics: list[MetricOut] = []
