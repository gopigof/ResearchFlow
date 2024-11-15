import os
import json
from datetime import datetime
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.readers.docling import DoclingReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from articles import update_processed_article

class DocumentProcessor:
    def __init__(self):
        """
        Initialize the DocumentProcessor with necessary configurations and clients
        """
        print("started initialising document processor")
        # Load environment variables
        load_dotenv()
        
        # Initialize configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.pinecone_environment = os.getenv('PINECONE_ENVIRONMENT')
        self.pinecone_index_name = os.getenv('PINECONE_INDEX_NAME')
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_s3_bucket = os.getenv('AWS_S3_BUCKET')

        # Set OpenAI API key
        os.environ['OPENAI_API_KEY'] = self.openai_api_key

        # Initialize clients and services
        self._init_s3_client()
        self._init_pinecone()
        self._init_embedding_model()
        
        # Initialize readers
        self.docling_reader = DoclingReader()
        print("Completed")

    def _init_s3_client(self):
        """Initialize S3 client"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key
        )

    def _init_pinecone(self):
        """Initialize Pinecone client and index"""
        self.pinecone = Pinecone(api_key=self.pinecone_api_key)
        self.pinecone_index = self.pinecone.Index(self.pinecone_index_name)

    def _init_embedding_model(self):
        """Initialize OpenAI embedding model"""
        self.embed_model = OpenAIEmbedding(
            model_name="text-embedding-3-small",
            embed_batch_size=10
        )

    def save_to_s3(self, content, filename):
        """
        Save content to S3 bucket
        
        Args:
            content (str): Content to save
            filename (str): Filename/key for S3 object
            
        Returns:
            str: S3 URL of saved object
        """
        try:
            self.s3_client.put_object(
                Bucket=self.aws_s3_bucket,
                Key=filename,
                Body=content,
                ContentType='text/markdown'
            )
            return f"s3://{self.aws_s3_bucket}/{filename}"
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            raise

    def process_documents(self, directory_path):
        """
        Process PDFs, store as markdown in S3, and index in Pinecone
        
        Args:
            directory_path (str): Path to directory containing PDF documents
            
        Returns:
            VectorStoreIndex: Created vector index
        """
        print(f"Processing started for {directory_path}")
        # Load and process documents
        documents = SimpleDirectoryReader(
            directory_path,
            file_extractor={
                ".pdf": self.docling_reader
            }
        ).load_data()

        print(f"Loaded {len(documents)} documents")

        # Store documents in S3 and collect their metadata
        processed_docs = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for idx, doc in enumerate(documents):
            # Get original PDF filename
            original_filename = doc.metadata.get('file_name')
            
            # Convert document content to markdown
            markdown_content = f"""# {original_filename}

{doc.text}

## Metadata
```json
{json.dumps(doc.metadata, indent=2)}
```
"""
            
            # Generate S3 key (filename)
            s3_key = f"pdf_extracts/{timestamp}/{original_filename}.md"
            
            # Save to S3
            processed_s3_url = self.save_to_s3(markdown_content, s3_key)
            
            # Update document metadata with S3 location
            doc.metadata['processed_s3_url'] = processed_s3_url
            processed_docs.append(doc)

            
            # Prepare update data
            update_data = {
                "processeds3_url": processed_s3_url,
                "a_id": doc.doc_id,
                "created_date": doc.metadata.get('creation_date')
            }
            
            # Update the article record
            update_processed_article(original_filename, update_data)
            print(f"Updated article record for {original_filename}")

        print(f"Saved {len(processed_docs)} documents to S3")
        print(self.pinecone_api_key, self.pinecone_environment, self.pinecone_environment)
        # Create Pinecone vector store
        vector_store = PineconeVectorStore(pinecone_index=self.pinecone_index,api_key = self.pinecone_api_key, environment=self.pinecone_environment)

        # Create storage context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Create index from documents
        vector_index = VectorStoreIndex.from_documents(
            processed_docs,
            storage_context=storage_context,
            embed_model=self.embed_model
        )

        print("Documents have been indexed and stored in Pinecone")

def main_doc_processor():
    # Set up the directory path
    directory_path = "/tmp/downloaded_pdfs"
    
    try:
        # Initialize processor
        processor = DocumentProcessor()
        
        # Process documents and create index
        processor.process_documents(directory_path)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main_doc_processor()