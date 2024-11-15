
from backend.research_agent import agent_workflow

async def process_qa_query(
    article_id: str, prompt: str, model: str, user_id: int
):
    """Process a Q/A query and store the result"""
    response = agent_workflow.invoke({"prompt": prompt})

    print(response)

    # qa_history = QAHistory(
    #     id=uuid.uuid4().hex,
    #     a_id=article_id,
    #     question=prompt,
    #     answer=response.response,
    #     referenced_pages=json.dumps([src.model_dump() for src in response.sources]),
    #     user_id=user_id,
    #     model=model,
    # )
    #
    # with db_session() as session:
    #     session.add(qa_history)
    #     session.commit()

    return response["generation"]
