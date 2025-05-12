# scripts/reset_database.py
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import logging
import shutil

# Add parent directory to path to import project modules
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Set up logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = project_root / "config" / ".env"
load_dotenv(env_path)

def reset_database():
    """Reset the database by deleting all records and clearing file directories"""
    # Get connection parameters from environment
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', 5432)
    db_name = os.getenv('POSTGRES_DB', 'ai_assistant')
    
    if not password:
        password = input("Enter PostgreSQL password: ")
    
    try:
        print("\n=== AI Assistant Database Reset ===")
        print("This will delete ALL data from the database and file storage directories.")
        confirmation = input("Are you sure you want to proceed? (yes/no): ")
        
        if confirmation.lower() != 'yes':
            print("Reset aborted.")
            return False
        
        print("\nConnecting to PostgreSQL server...")
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=db_name
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Delete records from all tables in the correct order to handle dependencies
        print("Deleting all records from database tables...")
        
        # 1. First delete all message records
        cursor.execute("DELETE FROM messages")
        message_count = cursor.rowcount
        print(f"Deleted {message_count} messages")
        
        # 2. Delete all chat records
        cursor.execute("DELETE FROM chats")
        chat_count = cursor.rowcount
        print(f"Deleted {chat_count} chats")
        
        # 3. Delete document_projects associations
        cursor.execute("DELETE FROM document_projects")
        doc_project_count = cursor.rowcount
        print(f"Deleted {doc_project_count} document-project associations")
        
        # 4. Delete document_embeddings
        cursor.execute("DELETE FROM document_embeddings")
        embedding_count = cursor.rowcount
        print(f"Deleted {embedding_count} document embeddings")
        
        # 5. Delete documents
        cursor.execute("DELETE FROM documents")
        document_count = cursor.rowcount
        print(f"Deleted {document_count} documents")
        
        # 6. Delete projects
        cursor.execute("DELETE FROM projects")
        project_count = cursor.rowcount
        print(f"Deleted {project_count} projects")
        
        # 7. Delete logs
        cursor.execute("DELETE FROM logs")
        log_count = cursor.rowcount
        print(f"Deleted {log_count} log entries")
        
        # 8. Delete web_search_cache
        try:
            cursor.execute("DELETE FROM web_search_cache")
            cache_count = cursor.rowcount
            print(f"Deleted {cache_count} web search cache entries")
        except:
            print("No web_search_cache table found, skipping")
        
        # Commit the transaction
        conn.commit()
        print("Database records deleted successfully")
        
        # Reset the autoincrement counters for all tables
        reset_tables = ["messages", "chats", "document_projects", "document_embeddings", 
                        "documents", "projects", "logs", "web_search_cache"]
        
        for table in reset_tables:
            try:
                cursor.execute(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1")
                print(f"Reset ID sequence for {table} table")
            except Exception as e:
                print(f"Could not reset sequence for {table}: {e}")
        
        # Close database connection
        cursor.close()
        conn.close()
        
        # Now clean up file storage directories
        data_path = project_root / "data"
        upload_path = data_path / "uploads"
        processed_path = data_path / "processed"
        
        # Clean uploads directory
        print("\nCleaning upload directory...")
        try:
            if upload_path.exists():
                for file in upload_path.iterdir():
                    if file.is_file():
                        file.unlink()
                        print(f"Deleted file: {file}")
            print("Upload directory cleaned")
        except Exception as e:
            print(f"Error cleaning upload directory: {e}")
        
        # Clean processed directory
        print("\nCleaning processed directory...")
        try:
            if processed_path.exists():
                for file in processed_path.iterdir():
                    if file.is_file():
                        file.unlink()
                        print(f"Deleted file: {file}")
            print("Processed directory cleaned")
        except Exception as e:
            print(f"Error cleaning processed directory: {e}")
        
        # Create a default project
        print("\nCreating a default project...")
        try:
            conn = psycopg2.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=db_name
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO projects (name, custom_prompt)
            VALUES (%s, %s)
            RETURNING id
            """, ("Main Project", "You are a helpful AI assistant. Provide detailed and accurate information."))
            
            project_id = cursor.fetchone()[0]
            
            # Create a default chat
            cursor.execute("""
            INSERT INTO chats (name, project_id)
            VALUES (%s, %s)
            """, ("General Chat", project_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            print("Default project and chat created successfully")
        except Exception as e:
            print(f"Error creating default project: {e}")
        
        print("\n✅ Database reset completed successfully!")
        print("\nYou can now restart the application and upload new files.")
        return True
    
    except Exception as e:
        print(f"\n❌ Error resetting database: {e}")
        return False

if __name__ == "__main__":
    reset_database()