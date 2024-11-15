from diagrams import Cluster, Diagram, Edge
from diagrams.programming.language import Python
from diagrams.onprem.workflow import Airflow
from diagrams.programming.framework import Fastapi
from diagrams.custom import Custom
from diagrams.programming.flowchart import Action
from diagrams.aws.storage import S3
from diagrams.generic.storage import Storage  # Importing generic storage for CFA PDFs
from diagrams.onprem.database import PostgreSQL

# Custom icons
class DoclingIcon(Custom):
    def __init__(self, label):
        super().__init__(label=label, icon_path="/Users/pranalichipkar/Documents/Pranali/BigData-Assignments/Assignment4/architecture/docling.jpg")

class LangraphIcon(Custom):
    def __init__(self, label):
        super().__init__(label=label, icon_path="/Users/pranalichipkar/Documents/Pranali/BigData-Assignments/Assignment4/architecture/langraph.jpg")

class StreamlitIcon(Custom):
    def __init__(self, label):
        super().__init__(label=label, icon_path="/Users/pranalichipkar/Documents/Pranali/BigData-Assignments/Assignment4/architecture/streamlit-logo-primary-colormark-darktext.png")

class PineconeIcon(Custom):
    def __init__(self, label):
        super().__init__(label=label, icon_path="/Users/pranalichipkar/Documents/Pranali/BigData-Assignments/Assignment4/architecture/pinecone-1.png")

def generate_assignment4_architecture():
    with Diagram("Assignment 4 Architecture", show=False, direction="LR"):
        with Cluster("Part 1: Document Processing & Vector Storage"):
            airflow = Airflow("Airflow Pipeline")
            
           
            cfa_storage = Storage("CFA PDFs")  # Using a generic storage icon for CFA PDFs
            docling = DoclingIcon("Docling")
                
            with Cluster("Storage"):
                    pinecone = PineconeIcon("Pinecone")
                    postgres = PostgreSQL("PostgreSQL")
                    s3 = S3("S3")
                
            cfa_storage >> docling >> Edge(color="blue") >> [pinecone, postgres, s3]
            
            # Connect Airflow to all components in Part 1
            airflow >> Edge(color="firebrick", style="dotted") >> cfa_storage
            airflow >> Edge(color="firebrick", style="dotted") >> docling
            airflow >> Edge(color="firebrick", style="dotted") >> pinecone
            airflow >> Edge(color="firebrick", style="dotted") >> postgres
            airflow >> Edge(color="firebrick", style="dotted") >> s3

        with Cluster("Part 2: Research Agent"):
            langraph = LangraphIcon("Langraph")
            
            with Cluster("Multi-Agent System"):
                document_agent = Python("Document Selection")
                arxiv_agent = Python("Arxiv Agent")
                web_search_agent = Python("Web Search Agent")
                rag_agent = Python("RAG Agent")
            
            langraph >> [document_agent, arxiv_agent, web_search_agent, rag_agent]
            pinecone >> rag_agent

        fastapi_backend = Fastapi("FastAPI Backend")

        with Cluster("Part 3: Research Interface"):
            interface = StreamlitIcon("Streamlit UI")
            
            with Cluster("User Interaction"):
                qa_interaction = Action("Q/A Interaction")
                export_pdf = Action("Export PDF Report")
                export_codelabs = Action("Export Codelabs")
            
            interface >> [qa_interaction, export_pdf, export_codelabs]

        # Connect the parts
        pinecone >> langraph
        langraph >> fastapi_backend
        fastapi_backend >> interface
        interface >> Edge(color="darkgreen") >> fastapi_backend

if __name__ == "__main__":
    generate_assignment4_architecture()