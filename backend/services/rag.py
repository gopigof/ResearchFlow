import base64
from functools import lru_cache
from typing import List, Any

from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.milvus import MilvusVectorStore
from pydantic import BaseModel, Field

from backend.config import settings

CHAT_ENGINE_CACHE = {}
CHAT_LLM_SYSTEM_PROMPT = """You are a multimodal assistant designed to efficiently answer user queries by retrieving relevant document excerpts. Only return the most relevant information instead of full documents, and combine text and image data for a comprehensive response."""


@lru_cache
def get_index(collection_name: str) -> VectorStoreIndex:
    vector_store = MilvusVectorStore(
        uri=settings.MILVUS_CLOUD_URI,
        token=settings.MILVUS_API_KEY,
        collection_name=collection_name,
        dim=1536
    )
    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-small", embed_batch_size=100
    )
    return VectorStoreIndex.from_vector_store(vector_store=vector_store)


@lru_cache(maxsize=128)
def get_chat_engine(user_id: int, article_id: str, model: str = "gpt-4o"):
    index = get_index(settings.MILVUS_DOCUMENTS_COLLECTION)
    _llm = OpenAI(
        model=model,
        system_prompt="You are a multimodal assistant designed to efficiently answer user queries by retrieving relevant document excerpts. Only return the most relevant information instead of full documents, and combine text and image data for a comprehensive response.",
    )
    return index.as_chat_engine(similarity_top_k=10, llm=_llm, response_mode="compact")


@lru_cache(maxsize=128)
def get_report_engine(user_id: int, article_id: str, model: str = "gpt-4o"):
    index = get_index(settings.MILVUS_DOCUMENTS_COLLECTION)
    _llm = OpenAI(
        model=model,
        system_prompt="""\
You are a report generation assistant tasked with producing a well-formatted context given parsed context.

You will be given context from one or more reports that take the form of parsed text.

You are responsible for producing a report with interleaving text and images - in the format of interleaving text and "image" blocks.
Since you cannot directly produce an image, the image block takes in a file path - you should write in the file path of the image instead.

How do you know which image to generate? Each context chunk will contain metadata including an image render of the source chunk, given as a file path. 
Include ONLY the images from the chunks that have heavy visual elements (you can get a hint of this if the parsed text contains a lot of tables).
You MUST include at least one image block in the output.

You MUST output your response as a tool call in order to adhere to the required output format. Do NOT give back normal text.

"""    )
    formatted_llm = _llm.as_structured_llm(output_cls=ReportOutput)
    return index.as_chat_engine(similarity_top_k=10, llm=formatted_llm, response_mode="compact")


class TextBlock(BaseModel):
    """Text block."""

    text: str = Field(..., description="The text for this block.")


class ImageBlock(BaseModel):
    """Image block."""

    file_path: str = Field(..., description="File path to the image.")
    title: str = Field(..., description="Title of the image.")


class ImageData(BaseModel):
    title: str
    image_base64: str


class ReportOutput(BaseModel):
    """Data model for a report.

    Can contain a mix of text and image blocks. MUST contain at least one image block.

    """

    blocks: List[Any] = Field(
        ..., description="A list of text and image blocks."
    )

    def render(self):
        """Format the response for rendering on streamlit."""
        blocks = {
            "text": "",
            "images": {}
        }
        for idx, b in enumerate(self.blocks):
            if isinstance(b, TextBlock):
                blocks["text"] += b.text + "\n"
            else:
                img_id = f"img{idx}"
                blocks["text"] += img_id + "\n"
                with open(b.file_path, "rb") as f:
                    blocks["images"][img_id] = ImageData(
                        title=b.title,
                        image_base64=base64.b64encode(f.read()).decode('utf-8'),
                    )
