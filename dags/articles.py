import os
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get PostgreSQL connection parameters from environment variables
db_host = os.getenv("POSTGRES_HOSTNAME")
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_port = os.getenv("POSTGRES_PORT")

def convert_date(date_string):
    """Convert date string to PostgreSQL-compatible format"""
    try:
        date_object = datetime.strptime(date_string, "%y")
        return date_object.strftime("%Y-%m-%d")
    except ValueError:
        return None

def insert_source_article(filename, source_url):
    """Insert initial article record with source PDF URL"""
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )

    cursor = conn.cursor()
    success = False

    try:
        # Create table if it doesn't exist with the new schema
        create_table_query = """
        CREATE TABLE IF NOT EXISTS articles (
            filename TEXT PRIMARY KEY,
            sourcepdf_url TEXT,
            processeds3_url TEXT,
            created_date DATE,
            a_id TEXT
        );
        """
        cursor.execute(create_table_query)

        # Insert article with source PDF URL
        insert_query = """
        INSERT INTO articles (filename, sourcepdf_url)
        VALUES (%s, %s)
        ON CONFLICT (filename) 
        DO UPDATE SET sourcepdf_url = EXCLUDED.sourcepdf_url;
        """
        
        cursor.execute(insert_query, (filename, source_url))
        conn.commit()
        success = True
        
    except Exception as e:
        print(f"An error occurred inserting source article: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        
    return success

def update_processed_article(filename, processed_data):
    """Update article record with processed data based on filename"""
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )

    cursor = conn.cursor()
    success = False

    try:
        update_query = """
        UPDATE articles 
        SET processeds3_url = %s,
            a_id = %s,
            created_date = %s
        WHERE filename = %s
        """
        
        date_format = "%Y-%m-%d"
        created_date = datetime.strptime(processed_data.get("created_date"), date_format )
        
        cursor.execute(
            update_query, 
            (
                processed_data.get("processeds3_url"),
                processed_data.get("a_id"),
                created_date,
                filename
            )
        )
        conn.commit()
        success = True
        
    except Exception as e:
        print(f"An error occurred updating processed article: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        
    return success

def get_all_articles():
    """Retrieve all articles from the database"""
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )

    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT filename, sourcepdf_url, processeds3_url, a_id, created_date FROM articles")
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()