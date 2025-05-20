#!/usr/bin/env python3
"""
Script to create the database directly using psycopg2
"""

import logging
import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Create the database and pgvector extension"""
    try:
        # Connect to the default postgres database
        db_user = "postgres"
        db_password = "4010"
        db_name = "ai_assistant"
        
        # Connect to postgres database first
        logger.info("Connecting to PostgreSQL...")
        
        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host="localhost",
            database="postgres"
        )
        
        # Set isolation level to autocommit
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if the database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone() is not None
        
        # If database exists, drop it
        if exists:
            logger.info(f"Database {db_name} exists, dropping it...")
            # Terminate all connections to the database
            cursor.execute(
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}'"
            )
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            logger.info(f"Database {db_name} dropped")
        
        # Create the database
        logger.info(f"Creating database {db_name}...")
        cursor.execute(f"CREATE DATABASE {db_name}")
        logger.info(f"Database {db_name} created successfully")
        
        # Close the connection to postgres
        cursor.close()
        conn.close()
        
        # Connect to the new database to create the extension
        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host="localhost",
            database=db_name
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            logger.info("pgvector extension created successfully")
        except Exception as e:
            logger.warning(f"Could not create pgvector extension: {e}")
            logger.warning("Vector search functionality may not be available")
            logger.warning("Please install pgvector manually: https://github.com/pgvector/pgvector")
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Create .env file with database connection details
        env_content = f"""
DATABASE_URL=postgresql://{db_user}:{db_password}@localhost/{db_name}
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3
EMBEDDINGS_MODEL=all-MiniLM-L6-v2
UPLOAD_FOLDER=./data/uploads
PROCESSED_FOLDER=./data/processed
LOG_LEVEL=INFO
PGVECTOR_AVAILABLE=true
"""
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(root_dir, "backend", ".env")
        with open(env_path, 'w') as f:
            f.write(env_content.strip())
        logger.info("Created .env file with database connection details")
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)