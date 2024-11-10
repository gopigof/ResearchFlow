import logging
from typing import Optional, List

from sqlalchemy import select

from backend.database import db_session
from backend.database.articles import ArticleModel
from backend.services.summary_generation import DocumentSummarizer

logger = logging.getLogger(__name__)


async def _get_article(article_id: str) -> Optional[ArticleModel]:
    try:
        with db_session() as session:
            stmt = select(ArticleModel).where(ArticleModel.a_id == article_id)
            result = session.execute(stmt)
            article = result.scalar_one_or_none()
            if article:
                session.refresh(article)
            return article
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {str(e)}", exc_info=True)
        return None


async def _get_all_articles() -> List[ArticleModel]:
    try:
        with db_session() as session:
            stmt = select(ArticleModel)
            result = session.execute(stmt)
            articles = result.scalars().all()
            return list(articles)
    except Exception as e:
        logger.error(f"Error fetching all articles: {str(e)}", exc_info=True)
        return []


async def _generate_summary(article_id: str) -> Optional[str]:
    # This is a placeholder for the NVIDIA service integration
    # You would implement the actual NVIDIA service call here
    try:
        with db_session() as session:
            article = await _get_article(article_id)
            if not article:
                return None

            # Here you would call the NVIDIA service
            # For now, we'll return a mock summary
            summarizer = DocumentSummarizer()

            # Process each directory
            print(f"\nProcessing article: {article}")

            # pdf_path = fetch_pdf_from_s3(article.pdf_url)
            pdf_path = fetch_file_from_s3(article.pdf_url, None)
            try:
                summary = summarizer.summarize_directory(
                    directory_path=pdf_path,
                    summary_length="medium"  # Options: "short", "medium", "long"
                )
                print(summary)
            except Exception as e:
                print(f"Error processing directory {pdf_path}: {str(e)}")
            
            # Update the article with the new summary
            # article.summary = summary
            # session.commit()
            # session.refresh(article)
            return summary
    except Exception as e:
        logger.error(
            f"Error generating summary for article {article_id}: {str(e)}",
            exc_info=True,
        )
        return None
