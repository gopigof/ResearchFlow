import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from pathlib import Path
from articles import insert_source_article

class S3Downloader:
    def __init__(self, local_directory):
        # Load environment variables
        load_dotenv()
        
        # Get credentials from environment variables
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region = os.getenv('AWS_REGION')
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        self.local_directory = local_directory
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region
        )
        
        # Create local directory if it doesn't exist
        Path(self.local_directory).mkdir(parents=True, exist_ok=True)

    def list_pdf_files(self):
        """List all PDF files in the bucket"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=10
            )
            
            if 'Contents' not in response:
                print(f"No files found in bucket {self.bucket_name}")
                return []
            
            pdf_files = [
                obj['Key'] for obj in response['Contents']
                if obj['Key'].lower().endswith('.pdf')
            ]
            
            if not pdf_files:
                print(f"No PDF files found in bucket {self.bucket_name}")
            
            return pdf_files
            
        except ClientError as e:
            print(f"Error listing files from S3: {str(e)}")
            raise

    def download_pdfs(self, limit=1):
        """
        Download up to 3 PDF files from the S3 bucket and store their info in the database
        
        Args:
            limit (int): Maximum number of PDFs to download (default 1)
        """
        try:
            # Get list of PDF files
            pdf_files = self.list_pdf_files()[:limit]
            
            if not pdf_files:
                return []
            
            downloaded_files = []
            
            # Download each PDF file
            for pdf_file in pdf_files:
                local_file_path = os.path.join(self.local_directory, os.path.basename(pdf_file))
                print(f"Downloading {pdf_file} to {local_file_path}")
                
                self.s3_client.download_file(
                    self.bucket_name,
                    pdf_file,
                    local_file_path
                )
                
                # Generate S3 URL for the source PDF
                source_s3_url = f"s3://{self.bucket_name}/{pdf_file}"
                
                # Insert or update source PDF information
                filename = os.path.basename(pdf_file)
                insert_source_article(filename, source_s3_url)
                
                downloaded_files.append({
                    'filename': filename,
                    'local_path': local_file_path
                })
                print(f"Successfully downloaded {pdf_file}")
            
            return downloaded_files
            
        except ClientError as e:
            print(f"Error downloading files from S3: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise

def main_pdf_downloader():
    # Set local directory for downloaded files
    local_directory = "/tmp/downloaded_pdfs"
    
    try:
        # Initialize downloader with local directory
        downloader = S3Downloader(local_directory=local_directory)
        
        # Download PDFs
        downloaded_files = downloader.download_pdfs()
        
        if downloaded_files:
            print("\nDownloaded files:")
            for file in downloaded_files:
                print(f"- {file['filename']} -> {file['local_path']}")
            return downloaded_files
        else:
            print("No files were downloaded")
            return []
            
    except Exception as e:
        print(f"Failed to download files: {str(e)}")
        return []

if __name__ == "__main__":
    main_pdf_downloader()