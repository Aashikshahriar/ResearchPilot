import uuid

from app.models.chunk import PaperChunk
from app.models.paper import Paper, ProcessingStatus
from app.models.section import PaperSection
from app.models.user import User
from app.services.rag_service import answer_question
from app.core.security import hash_password


def _make_paper_with_chunks(db_session):
    user = User(email=f"rag-{uuid.uuid4().hex[:6]}@example.com", hashed_password=hash_password("SecurePass123"))
    db_session.add(user)
    db_session.flush()

    paper = Paper(
        owner_id=user.id, filename="p.pdf", file_path="/tmp/p.pdf", status=ProcessingStatus.ready, title="Test Paper"
    )
    db_session.add(paper)
    db_session.flush()

    section = PaperSection(paper_id=paper.id, title="Methodology", content="methods content", order_index=0)
    db_session.add(section)
    db_session.flush()

    from app.services.llm.mock_provider import MockLLMProvider

    provider = MockLLMProvider(embedding_dim=1536)

    relevant_text = "Differential privacy adds calibrated noise to protect individual records during training."
    irrelevant_text = "The weather in the mountains was cold and the hikers wore heavy coats."

    for i, content in enumerate([relevant_text, irrelevant_text]):
        vector = provider.embed([content]).vectors[0]
        db_session.add(
            PaperChunk(paper_id=paper.id, section_id=section.id, content=content, chunk_index=i, embedding=vector)
        )
    db_session.commit()
    return user, paper


def test_answer_question_grounds_answer_in_relevant_chunk(db_session):
    user, paper = _make_paper_with_chunks(db_session)

    conversation, message, citations = answer_question(
        db_session,
        paper_id=paper.id,
        user_id=user.id,
        question="How does the paper protect individual privacy during training?",
        conversation_id=None,
    )

    assert conversation.paper_id == paper.id
    assert "differential" in message.content.lower() or "privacy" in message.content.lower()
    assert len(citations) > 0
    assert citations[0]["section_title"] == "Methodology"


def test_answer_question_reuses_existing_conversation(db_session):
    user, paper = _make_paper_with_chunks(db_session)

    conversation, _, _ = answer_question(
        db_session, paper_id=paper.id, user_id=user.id, question="What method is used?", conversation_id=None
    )
    conversation_2, _, _ = answer_question(
        db_session,
        paper_id=paper.id,
        user_id=user.id,
        question="Follow-up question",
        conversation_id=conversation.id,
    )

    assert conversation_2.id == conversation.id
    assert len(conversation_2.messages) == 4  # 2 user + 2 assistant messages
