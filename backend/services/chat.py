import json
import uuid
from typing import List

from backend.database import db_session
from backend.database.qa import QAHistory
from backend.database.research_notes import ResearchNotes
from backend.schemas.qa import QAResponse
from backend.services.rag import get_chat_engine, get_report_engine


async def process_qa_query(
    article_id: str, prompt: str, model: str, user_id: int
) -> QAResponse:
    """Process a Q/A query and store the result"""
    chat_engine = get_chat_engine(user_id, article_id, model)
    response = chat_engine.chat(prompt)

    qa_history = QAHistory(
        id=uuid.uuid4().hex,
        a_id=article_id,
        question=prompt,
        answer=response.response,
        referenced_pages=json.dumps([src.model_dump() for src in response.sources]),
        user_id=user_id,
        model=model,
    )

    with db_session() as session:
        session.add(qa_history)
        session.commit()

    return response.response


async def get_qa_history(article_id: int, user_id: int) -> List[dict]:
    """Retrieve Q/A history for an article"""
    with db_session() as session:
        history = (
            session.query(QAHistory)
            .filter(QAHistory.article_id == article_id, QAHistory.user_id == user_id)
            .order_by(QAHistory.created_at.desc())
            .all()
        )

        return [
            {
                "question": h.question,
                "answer": h.answer,
                "created_at": h.created_at,
                "validated": h.validated,
                "confidence_score": h.confidence_score,
                "referenced_pages": h.referenced_pages,
                "media_references": h.media_references,
            }
            for h in history
        ]


async def generate_research_report(
    article_id: str,
    prompt: str,
    model: str,
    user_id: int
):
    """Generate a research report from multiple questions"""
    report_engine = get_report_engine(user_id, article_id, model)
    response = report_engine.chat(prompt)
    formatted_response = response.response

    # Store report
    report = ResearchNotes(
        id=uuid.uuid4().hex,
        a_id=article_id,
        question=prompt,
        answer=formatted_response,
        model=model,
        referenced_pages=json.dumps([src.model_dump() for src in response.sources]),
        validated=False,
    )

    with db_session() as session:
        session.add(report)
        session.commit()
        session.refresh(report)
    return {
        "response": formatted_response,
        "report_id": report.id,
    }


async def index_report(
    article_id: str, report_id: int, user_id: int
):
    """Validate and index a report"""
    with db_session() as session:
        report = (
            session.query(ResearchNotes)
            .filter(ResearchNotes.id == report_id)
            .first()
        )

        if not report:
            # Store report
            report = ResearchNotes(
                id=uuid.uuid4().hex,
                a_id=article_id,
                question="",
                answer="",
                model="",
                referenced_pages="",
                validated=False,
            )
            session.add(report)
            session.commit()
            session.refresh(report)

        report.validated = True
        session.commit()

        return "success", "Report validated and indexed"
