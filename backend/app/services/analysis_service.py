import json
import uuid

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.analysis import Analysis, AnalysisType
from app.models.paper import Paper
from app.services.inference_logger import log_inference
from app.services.llm import get_llm_provider

COMPARISON_SCHEMA = {
    "type": "object",
    "properties": {
        "research_problem": {"type": "string"},
        "methodology": {"type": "string"},
        "datasets": {"type": "string"},
        "models": {"type": "string"},
        "results": {"type": "string"},
        "strengths": {"type": "string"},
        "limitations": {"type": "string"},
        "key_differences": {"type": "string"},
    },
    "required": [
        "research_problem", "methodology", "datasets", "models",
        "results", "strengths", "limitations", "key_differences",
    ],
    "additionalProperties": False,
}

COMPARE_SYSTEM_PROMPT = """You are a research analyst comparing academic papers. Using ONLY the provided \
abstracts and summaries, produce a structured comparison. If information for a field is not available in \
the provided text, state "Not specified in available text" for that field rather than inventing details."""


def compare_papers(db: Session, paper_ids: list[uuid.UUID]) -> Analysis:
    papers = [db.get(Paper, pid) for pid in paper_ids]
    missing = [str(pid) for pid, p in zip(paper_ids, papers) if p is None]
    if missing:
        raise NotFoundError("PAPER_NOT_FOUND", f"Papers not found: {', '.join(missing)}")

    llm = get_llm_provider()
    context = "\n\n".join(
        f"PAPER {i + 1}: {p.title}\nAuthors: {', '.join(p.authors or [])}\n"
        f"Abstract: {p.abstract or 'N/A'}\nSummary: {p.ai_summary or 'N/A'}"
        for i, p in enumerate(papers)
    )

    with log_inference(db, operation="compare", provider=llm.name, model=getattr(llm, "chat_model", llm.name)) as record:
        result = llm.generate_structured(COMPARE_SYSTEM_PROMPT, context, COMPARISON_SCHEMA)
        record["prompt_tokens"] = result.prompt_tokens
        record["completion_tokens"] = result.completion_tokens

    analysis = Analysis(
        paper_id=None,
        analysis_type=AnalysisType.comparison,
        content=json.dumps(result.data),
        related_paper_ids=paper_ids,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
