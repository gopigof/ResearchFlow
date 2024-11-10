# articles/schemas.py
from datetime import datetime

from pydantic import BaseModel


class ArticleBase(BaseModel):
    title: str
    description: str
    publication_date: datetime
    authors: str
    pdf_url: str
    image_url: str


class ArticleCreate(ArticleBase):
    pass


class ArticleResponse(ArticleBase):
    a_id: str


class ArticleSummaryRequest(BaseModel):
    article_id: int


class ArticleSummaryResponse(BaseModel):
    article_id: str
    title: str
    summary: str
