# Multi-Agent Research Tool with Langraph and Airflow

## Links

- [Codelab Documentation](https://codelabs-preview.appspot.com/?file_id=1t6ou-QbbPWOR-Mek-LS3PN6pOFQiU-TcNmU0s33pc3c#0)
- [Deployed Streamlit Application](http://54.166.164.60:8501)
- [Deployed FastAPI Backend](http://54.166.164.60:8000/docs)
- [Demo Video](video/video.mov)

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
   git clone https://github.com/BigDataIA-Fall2024-TeamA2/Assignment4
   ```

2. Install dependencies:
   ```
   poetry install --dev
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


## Attestation
WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK

Contribution:

    a. Gopi Krishna Gorle: 33%
    b. Pranali Chipkar: 33%
    c. Mubin Modi: 33%


## Project Structure

```
.
├── README.md
├── app.py
├── architecture
├── 1_Z1NtI1D-YEGBJfb7bW4MIA.png
├── assignment_4_architecture.png
├── docling.jpg
├── generate_diagrams.py
├── pinecone-1.png
└── streamlit-logo-primary-colormark-darktext.png
├── backend
├── __init__.py
├── config.py
├── database
├── __init__.py
├── articles.py
└── users.py
├── logging.conf
├── main.py
├── research_agent
├── __init__.py
├── edges.py
├── generate_chain.py
├── grader.py
├── graph.py
├── nodes.py
└── vector_store.py
├── schemas
├── __init__.py
├── articles.py
├── auth.py
├── chat.py
└── users.py
├── server.py
├── services
├── __init__.py
├── articles.py
├── auth.py
├── auth_bearer.py
├── chat.py
└── users.py
├── utils.py
└── views
    ├── __init__.py
    ├── articles.py
    ├── auth.py
    ├── chat.py
    └── users.py
├── backend.Dockerfile
├── config
├── dags
├── articles.py
├── downloaded_pdfs
├── 10-years-after-global-financial-crisis.pdf
├── 2023-international-valuation-guide-to-cost-of-capital.pdf
└── Horan-ESG_RF_Brief_2022_Online.pdf
├── pdf_download.py
├── pdf_processor_indexer.py
└── pipeline.py
├── docker-compose-app.yml
├── docker-compose.yaml
├── frontend
├── __init__.py
├── config.py
├── pages
├── __init__.py
├── chat.py
├── list_docs.py
├── user_creation.py
└── user_login.py
└── utils
    ├── __init__.py
    ├── api_utils.py
    ├── auth.py
    └── chat.py
├── frontend.Dockerfile
├── graph.png
├── poetry.lock
└── pyproject.toml

```
