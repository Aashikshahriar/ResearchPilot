import enum
import uuid

from sqlalchemy import ARRAY, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, uuid_pk


class AnalysisType(str, enum.Enum):
    summary = "summary"
    comparison = "comparison"
    metadata_extraction = "metadata_extraction"


class Analysis(Base, TimestampMixin):
    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = uuid_pk()
    paper_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), nullable=True, index=True
    )
    analysis_type: Mapped[AnalysisType] = mapped_column(Enum(AnalysisType, name="analysis_type"))
    content: Mapped[str] = mapped_column(Text)  # JSON-encoded structured result
    related_paper_ids: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)

    paper = relationship("Paper", back_populates="analyses")
