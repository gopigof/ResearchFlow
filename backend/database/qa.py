from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from backend.database import Base


class QAHistory(Base):
    __tablename__ = "qa_history"

    id = Column(String, primary_key=True)
    a_id = Column(String)
    question = Column(String)
    answer = Column(String)
    referenced_pages = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer)
    model = Column(String)

    __table_args__ = {"schema": "public"}
