from typing import List

from fastapi import APIRouter, status, HTTPException, Depends

from backend.schemas.qa import (
    QARequest,
    ChatHistoryResponse,
    ReportGenerationRequest,
    IndexReportResponse,
)
from backend.services.auth_bearer import get_current_user_id
from backend.services.chat import (
    process_qa_query,
    get_qa_history, generate_research_report, index_report,
)

chat_router = APIRouter(prefix="/chat", tags=["qa-interface"])


@chat_router.post(
    "/{article_id}/qa",
    # response_model=QAResponse,
    # responses={
    #     status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"},
    #     status.HTTP_404_NOT_FOUND: {"description": "Article not found"}
    # }
)
async def question_answer(
    article_id: str, request: QARequest, user_id: int = Depends(get_current_user_id)
):
    """
    Process a Q/A query for a specific article using multi-modal RAG
    """
    return {
        "response": await process_qa_query(
            article_id, request.question, request.model, user_id
        )
    }


@chat_router.get(
    "/{article_id}/history",
    # response_model=List[ChatHistoryResponse]
)
async def get_history(
    article_id: int, user_id: int = Depends(get_current_user_id)
) -> List[ChatHistoryResponse]:
    """
    Retrieve Q/A history for a specific article
    """
    try:
        history = await get_qa_history(article_id, user_id)
        return [ChatHistoryResponse(**h) for h in history]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@chat_router.post(
    "/{article_id}/generate-report",
)
async def create_report(
    article_id: str,
    request: ReportGenerationRequest,
    user_id: int = Depends(get_current_user_id),
):
    """
    Generate a comprehensive research report for an article
    """
    return await generate_research_report(
        article_id,
        request.question,
        request.model,
        user_id,
    )


@chat_router.post(
    "/{article_id}/{report_id}/index",
)
async def validate_and_index_report(
    article_id: int, report_id: int, user_id: int = Depends(get_current_user_id)
) -> IndexReportResponse:
    """
    Validate and index a generated report
    """
    try:
        _status, message = await index_report(article_id, report_id, user_id)
        return IndexReportResponse(status=_status, message=message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
