# schemas/chat.py
from datetime import datetime
from typing import List

from pydantic import BaseModel


class QARequest(BaseModel):
    question: str
    model: str


class QAResponse(BaseModel):
    answer: str
    confidence_score: float
    referenced_pages: List[int]
    media_references: List[str]


class ChatHistoryResponse(BaseModel):
    question: str
    answer: str
    created_at: datetime
    validated: bool


class ReportGenerationRequest(BaseModel):
    question: str
    model: str


class ReportResponse(BaseModel):
    report_id: int
    content: str
    media_references: List[str]
    created_at: datetime
    validated: bool
    indexed: bool


class IndexReportResponse(BaseModel):
    status: str
    message: str
