Here's a README.md format based on the provided assignment details:

# Multi-Agent Research Tool with Langraph and Airflow

## Links

- [Deployed Application](https://your-app-url.com)
- [Backend Services](https://your-backend-url.com)
- [Demo Video](https://your-video-url.com)
- [Codelab Documentation](https://your-codelab-url.com)

## Objective

This project aims to build an end-to-end research tool using an Airflow pipeline to process documents, store and search vectors, and create a multi-agent research interface.

## Features

- Document parsing and vector storage pipeline
- Multi-agent system for document-based research
- User interaction interface for conducting research
- Export functionality for research findings



## Requirements

### Part 1: Document Parsing, Vector Storage, and Pipeline Setup

1. Airflow Pipeline
   - Use Docling for parsing documents
   - Configure Docling to process the provided dataset
   - Extract text and export structured information

2. Vector Storage with Pinecone
   - Store parsed document vectors in Pinecone for fast and scalable similarity search

3. Pipeline Automation
   - Build an Airflow pipeline integrating Docling and Pinecone
   - Automate the document parsing and vector storage process

### Part 2: Research Agent with Pinecone and Langraph

1. Agent Setup
   - Use Pinecone for vector storage and retrieval
   - Use Langraph to create a multi-agent system for document-based research
   - Implement the following agents:
     - Document Selection Agent
     - Arxiv Agent
     - Web Search Agent
     - RAG (Retrieval-Augmented Generation) Agent

### Part 3: Research Interface and Q/A Interaction

1. User Interaction Interface
   - Streamlit to create a user interface
   - Allow users to ask 5-6 questions per document
   - Save results of each research session

2. Export Results
   - Generate a professional PDF report of research findings
   - Structure findings in a Codelabs format for instructional clarity and future reference

## Setup and Installation

1. Clone the repository:
   ```
   git clone repo link
   ```

2. Install dependencies:
   ```
   poetry install
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file with your configuration details.

4. Start the Airflow services:
   ```
   docker-compose up -d
   ```

5. Access the Airflow UI at `http://localhost:8080` to monitor and manage the pipeline.

6. Run the frontend application:
   ```
   streamlit run frontend/app.py
   ```

## Usage

1. Access the user interface through the provided URL.
2. Select a document for research.
3. Use the multi-agent system to conduct research and ask questions.
4. Export your research findings as a PDF report or in Codelabs format.

## Documentation

For detailed instructions on setup, usage, and accessing the deployed applications, please refer to our comprehensive [User Guide](docs/user_guide.md).

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- Docling for document parsing
- Pinecone for vector storage and retrieval
- Langraph for multi-agent system implementation
- Airflow for pipeline automation


## Project Structure

```
.
├── README.md
├── airflow/
│   ├── dags/
│   │   ├── document_parsing.py
│   │   └── vector_storage.py
│   └── Dockerfile
├── agents/
│   ├── document_selection.py
│   ├── arxiv_agent.py
│   ├── web_search_agent.py
│   └── rag_agent.py
├── frontend/
│   ├── app.py
│   └── pages/
├── backend/
│   ├── api/
│   └── services/
├── utils/
│   ├── docling_utils.py
│   └── pinecone_utils.py
├── docker-compose.yml
└── requirements.txt
```
