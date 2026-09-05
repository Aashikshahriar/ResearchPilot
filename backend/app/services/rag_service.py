import json
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import PaperChunk
from app.models.conversation import Conversation, Message, MessageRole
from app.services.inference_logger import log_inference
from app.services.llm import get_llm_provider

RAG_SYSTEM_PROMPT = """You are ResearchPilot's paper assistant. You answer questions strictly using \
the provided excerpts from a single academic paper.

Rules:
- Only use information present in the CONTEXT below. Do not invent facts, numbers, or citations.
- If the context does not contain the answer, say so explicitly rather than guessing.
- When you state a claim from the paper, note which section it came from, e.g. "(Section: Methodology)".
- Clearly distinguish paper claims from your own interpretation by prefacing interpretation with \
"Interpretation:".
- Be concise and technical; this is for a researcher, not a general audience."""

TOP_K = 5


def _cosine_topk(query_vector: list[float], chunks: list[PaperChunk], k: int) -> list[tuple[PaperChunk, float]]:
    def cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(y * y for y in b) ** 0.5
        return dot / (na * nb) if na and nb else 0.0

    scored = [(c, cosine(query_vector, c.embedding)) for c in chunks if c.embedding]
    scored.sort(key=lambda t: -t[1])
    return scored[:k]


def retrieve_relevant_chunks(db: Session, paper_id: uuid.UUID, question: str, k: int = TOP_K) -> list[tuple[PaperChunk, float]]:
    llm = get_llm_provider()
    query_embedding = llm.embed([question]).vectors[0]

    chunks = db.scalars(select(PaperChunk).where(PaperChunk.paper_id == paper_id)).all()

    # Prefer the database-native vector similarity search (pgvector) when
    # available; fall back to in-Python cosine similarity for providers
    # whose embeddings aren't stored with a matching dimension yet.
    try:
        from pgvector.sqlalchemy import Vector  # noqa: F401

        stmt = (
            select(PaperChunk)
            .where(PaperChunk.paper_id == paper_id, PaperChunk.embedding.is_not(None))
            .order_by(PaperChunk.embedding.cosine_distance(query_embedding))
            .limit(k)
        )
        results = db.scalars(stmt).all()
        if results:
            return [(c, 1.0) for c in results]
    except Exception:
        pass

    return _cosine_topk(query_embedding, chunks, k)


def answer_question(
    db: Session,
    *,
    paper_id: uuid.UUID,
    user_id: uuid.UUID,
    question: str,
    conversation_id: uuid.UUID | None,
) -> tuple[Conversation, Message, list[dict]]:
    llm = get_llm_provider()
    top_chunks = retrieve_relevant_chunks(db, paper_id, question)

    context_blocks = []
    citations = []
    for chunk, _score in top_chunks:
        section_title = chunk.section.title if chunk.section else "Unknown Section"
        context_blocks.append(f"[Section: {section_title}]\n{chunk.content}")
        citations.append(
            {
                "section_title": section_title,
                "chunk_id": str(chunk.id),
                "excerpt": chunk.content[:280],
            }
        )

    context_text = "\n\n---\n\n".join(context_blocks) if context_blocks else "(no indexed content available)"
    user_prompt = f"CONTEXT:\n{context_text}\n\nQUESTION:\n{question}"

    with log_inference(db, operation="chat", provider=llm.name, model=getattr(llm, "chat_model", llm.name), user_id=user_id) as record:
        result = llm.generate(RAG_SYSTEM_PROMPT, user_prompt)
        record["prompt_tokens"] = result.prompt_tokens
        record["completion_tokens"] = result.completion_tokens

    if conversation_id:
        conversation = db.get(Conversation, conversation_id)
    else:
        conversation = None
    if conversation is None:
        conversation = Conversation(paper_id=paper_id, user_id=user_id, title=question[:200])
        db.add(conversation)
        db.flush()

    db.add(Message(conversation_id=conversation.id, role=MessageRole.user, content=question))
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.assistant,
        content=result.text,
        citations=json.dumps(citations),
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return conversation, assistant_message, citations
