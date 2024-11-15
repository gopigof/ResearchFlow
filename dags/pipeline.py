from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from pdf_download import main_pdf_downloader
from pdf_processor_indexer import main_doc_processor

# Download directory
download_dir = "/tmp/downloaded_pdfs"

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now(),
    'retries': 1,
}

with DAG('pdf_processing_pipeline', default_args=default_args) as dag:
    
    download_task = PythonOperator(
        task_id='download_pdfs',
        python_callable=main_pdf_downloader,
        dag=dag,
    )
    
    process_task = PythonOperator(
        task_id='process_pdfs',
        python_callable=main_doc_processor,
        dag=dag,
    )

    download_task >> process_task  # Set task dependencies