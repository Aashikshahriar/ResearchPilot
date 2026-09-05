import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, uuid_pk


class FigureType(str, enum.Enum):
    architecture_diagram = "architecture_diagram"
    flowchart = "flowchart"
    graph_plot = "graph_plot"
    table = "table"
    microscopy_image = "microscopy_image"
    mathematical_figure = "mathematical_figure"
    other = "other"


class Figure(Base, TimestampMixin):
    __tablename__ = "figures"

    id: Mapped[uuid.UUID] = uuid_pk()
    paper_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), index=True)

    page_number: Mapped[int] = mapped_column(Integer)
    image_path: Mapped[str] = mapped_column(String(1000))
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)

    classification: Mapped[FigureType | None] = mapped_column(Enum(FigureType, name="figure_type"), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    vision_model: Mapped[str | None] = mapped_column(String(255), nullable=True)

    paper = relationship("Paper", back_populates="figures")
