from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime

from backend.database import Base


class ResearchNotes(Base):
    __tablename__ = "research_notes"

    id = Column(String, primary_key=True)
    a_id = Column(String)
    question = Column(String)
    answer = Column(String)
    referenced_pages = Column(String)
    model = Column(String)
    validated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = {"schema": "public"}
