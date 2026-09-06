import logging
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models.chunk import PaperChunk
from app.models.figure import Figure, FigureType
from app.models.paper import Paper, ProcessingStatus
from app.models.section import PaperSection
from app.services.document_processor import PDFDocumentProcessor, chunk_text
from app.services.inference_logger import log_inference
from app.services.llm import get_llm_provider
from app.services.vision import get_vision_provider

logger = logging.getLogger(__name__)
settings = get_settings()


def process_paper_job(paper_id: uuid.UUID) -> None:
    """Runs the full ingestion pipeline for a paper. Designed to run in a
    background task/worker so the upload request returns immediately."""

    db: Session = SessionLocal()
    try:
        paper = db.get(Paper, paper_id)
        if paper is None:
            return

        paper.status = ProcessingStatus.processing
        paper.processing_error = None
        db.commit()

        try:
            _run_pipeline(db, paper)
            paper.status = ProcessingStatus.ready
            db.commit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Paper processing failed for %s", paper_id)
            paper.status = ProcessingStatus.failed
            paper.processing_error = str(exc)[:2000]
            db.commit()
    finally:
        db.close()


def _run_pipeline(db: Session, paper: Paper) -> None:
    processor = PDFDocumentProcessor()
    extracted = processor.process(paper.file_path)

    paper.title = extracted.title or paper.filename
    paper.authors = extracted.authors
    paper.abstract = extracted.abstract
    paper.page_count = extracted.page_count
    db.flush()

    figures_dir = Path(settings.storage_dir) / "figures" / str(paper.id)
    figures_dir.mkdir(parents=True, exist_ok=True)

    section_models: list[PaperSection] = []
    for section in extracted.sections:
        model = PaperSection(
            paper_id=paper.id,
            title=section.title,
            content=section.content,
            order_index=section.order_index,
            page_start=section.page_start,
            page_end=section.page_end,
        )
        db.add(model)
        section_models.append(model)
    db.flush()

    _generate_chunks_and_embeddings(db, paper, section_models)
    _extract_and_classify_figures(db, paper, extracted.figures, figures_dir)
    generate_summary(db, paper, extracted.raw_text)


def _generate_chunks_and_embeddings(db: Session, paper: Paper, sections: list[PaperSection]) -> None:
    llm = get_llm_provider()
    chunk_index = 0

    for section in sections:
        pieces = chunk_text(section.content)
        if not pieces:
            continue
        with log_inference(db, operation="embed", provider=llm.name, model=getattr(llm, "embedding_model", llm.name)) as record:
            embeddings = llm.embed(pieces)
            record["prompt_tokens"] = sum(len(p.split()) for p in pieces)
            record["model"] = embeddings.model

        for text, vector in zip(pieces, embeddings.vectors):
            db.add(
                PaperChunk(
                    paper_id=paper.id,
                    section_id=section.id,
                    content=text,
                    chunk_index=chunk_index,
                    token_count=len(text.split()),
                    embedding=vector,
                )
            )
            chunk_index += 1
    db.flush()


def _extract_and_classify_figures(db: Session, paper: Paper, figures, figures_dir: Path) -> None:
    vision = get_vision_provider()

    for idx, fig in enumerate(figures):
        image_filename = f"figure_{idx + 1}.{fig.image_ext}"
        image_path = figures_dir / image_filename
        image_path.write_bytes(fig.image_bytes)

        try:
            with log_inference(db, operation="figure_classify", provider=vision.name, model=vision.name) as record:
                classification = vision.classify(str(image_path))
                record["confidence"] = classification.confidence
            description = vision.describe(str(image_path), classification.label, fig.caption)

            db.add(
                Figure(
                    paper_id=paper.id,
                    page_number=fig.page_number,
                    image_path=str(image_path),
                    caption=fig.caption,
                    classification=FigureType(classification.label),
                    confidence=classification.confidence,
                    description=description,
                    vision_model=vision.name,
                )
            )
        except Exception:
            logger.exception("Figure classification failed for paper %s figure %s", paper.id, idx)
    db.flush()


def generate_summary(db: Session, paper: Paper, raw_text: str) -> None:
    llm = get_llm_provider()
    system_prompt = (
        "You are an expert research assistant. Summarize the academic paper below in 4-6 sentences, "
        "covering the research problem, method, and key findings. Be factual and only use the provided text."
    )
    truncated = raw_text[:12000]
    with log_inference(db, operation="summarize", provider=llm.name, model=getattr(llm, "chat_model", llm.name)) as record:
        result = llm.generate(system_prompt, truncated)
        record["prompt_tokens"] = result.prompt_tokens
        record["completion_tokens"] = result.completion_tokens
        record["model"] = result.model
    paper.ai_summary = result.text
    db.flush()
