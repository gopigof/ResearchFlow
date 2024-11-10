# articles/models.py
from sqlalchemy import Column, String, DateTime, Computed

from backend.database import Base


class ArticleModel(Base):
    __tablename__ = "articles"

    a_id = Column("a_id", String, primary_key=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(String(1000), nullable=False)
    publication_date = Column(DateTime, nullable=False)
    authors = Column(String(500), nullable=False)
    pdf_url = Column(String(500), nullable=False)
    image_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, Computed("CURRENT_TIMESTAMP()"), nullable=False)
    updated_at = Column(DateTime, Computed("CURRENT_TIMESTAMP()"), nullable=False)

    __table_args__ = {"schema": "public"}
