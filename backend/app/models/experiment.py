import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, uuid_pk


class Experiment(Base, TimestampMixin):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = uuid_pk()
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    name: Mapped[str] = mapped_column(String(500))
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dataset: Mapped[str | None] = mapped_column(String(255), nullable=True)
    learning_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    batch_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    epochs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    owner = relationship("User", back_populates="experiments")
    metrics = relationship("ExperimentMetric", back_populates="experiment", cascade="all, delete-orphan")


class ExperimentMetric(Base, TimestampMixin):
    __tablename__ = "experiment_metrics"

    id: Mapped[uuid.UUID] = uuid_pk()
    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"), index=True)

    name: Mapped[str] = mapped_column(String(255))
    value: Mapped[float] = mapped_column(Float)
    step: Mapped[int | None] = mapped_column(Integer, nullable=True)

    experiment = relationship("Experiment", back_populates="metrics")
