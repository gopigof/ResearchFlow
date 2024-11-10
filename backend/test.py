# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA
from llama_index.vector_stores.milvus import MilvusVectorStore

from backend.config import settings
from dags.data_indexer.document_processors import load_data_from_directory


class DocumentSummarizer:
    def __init__(self):
        self.initialize_settings()

    def initialize_settings(self):
        """Initialize LlamaIndex settings with NVIDIA models"""
        Settings.embed_model = NVIDIAEmbedding(
            model="nvidia/nv-embedqa-e5-v5", truncate="END"
        )
        Settings.llm = NVIDIA(
            model="mistralai/mistral-7b-instruct-v0.3",
            nvidia_api_key=settings.NVIDIA_API_KEY,
        )
        Settings.text_splitter = SentenceSplitter(chunk_size=600)

    def create_index(self, documents):
        vector_store = MilvusVectorStore(
            uri=settings.MILVUS_CLOUD_URI, token=settings.MILVUS_API_KEY, dim=1024
        )
        # vector_store = MilvusVectorStore(uri="./milvus_demo.db", dim=1024, overwrite=True) #For CPU only vector store
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        return VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )

    def generate_summary(self, index, doc_length="medium"):
        """Generate a summary of the documents"""
        length_prompts = {
            "short": "Provide a brief 2-3 sentence summary of the main points in the document.",
            "medium": "Provide a comprehensive paragraph summarizing the key points and main ideas in the document.",
            "long": "Provide a detailed summary of the document, including main points, key details, and important conclusions.",
        }

        prompt = length_prompts.get(doc_length, length_prompts["short"])
        query_engine = index.as_query_engine(similarity_top_k=1)
        print(query_engine)
        response = query_engine.query(prompt)
        print(response.response)
        return response.response

    def summarize_directory(self, directory_path, summary_length="medium"):
        """Process a directory of documents and generate a summary"""
        print(f"Processing documents from directory: {directory_path}")
        documents = load_data_from_directory(directory_path)
        print(f"Found {len(documents)} documents")

        print("Creating document index...")
        index = self.create_index(documents)

        print("Generating summary...")
        summary = self.generate_summary(index, summary_length)

        return summary


def main():
    # Initialize the summarizer
    summarizer = DocumentSummarizer()

    # List of directories to process
    document_directories = [
        "/Users/pranalichipkar/Documents/Pranali/BigData-Assignments/Assignment3/backend/data/"
    ]

    # Process each directory
    for directory in document_directories:
        print(f"\nProcessing directory: {directory}")
        try:
            summary = summarizer.summarize_directory(
                directory_path=directory,
                summary_length="medium",  # Options: "short", "medium", "long"
            )
            print("\nSummary:")
            print("=" * 80)
            print(summary)
            print("=" * 80)
        except Exception as e:
            print(f"Error processing directory {directory}: {str(e)}")


if __name__ == "__main__":
    main()
