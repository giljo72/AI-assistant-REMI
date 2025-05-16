#!/usr/bin/env python3
"""
Script to completely recreate the database from scratch.
"""

import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Delete and recreate the PostgreSQL database."""
    try:
        # Change to the project root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(root_dir)
        
        # Ask for PostgreSQL credentials
        db_name = "ai_assistant"  # Default database name
        db_user = input("Enter PostgreSQL username (default: postgres): ") or "postgres"
        db_password = input("Enter PostgreSQL password: ")
        
        # Drop the database if it exists
        logger.info(f"Dropping database {db_name} if it exists...")
        try:
            subprocess.run(
                ["psql", "-U", db_user, "-c", f"DROP DATABASE IF EXISTS {db_name};"],
                check=True,
                capture_output=True,
                text=True,
                env=dict(os.environ, PGPASSWORD=db_password)
            )
            logger.info(f"Database {db_name} dropped successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error dropping database: {e}")
            if e.stderr:
                logger.error(f"Error details: {e.stderr}")
            return
        
        # Create a new database
        logger.info(f"Creating new database {db_name}...")
        try:
            subprocess.run(
                ["psql", "-U", db_user, "-c", f"CREATE DATABASE {db_name};"],
                check=True,
                capture_output=True,
                text=True,
                env=dict(os.environ, PGPASSWORD=db_password)
            )
            logger.info(f"Database {db_name} created successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating database: {e}")
            if e.stderr:
                logger.error(f"Error details: {e.stderr}")
            return
        
        # Create pgvector extension
        logger.info("Creating pgvector extension...")
        try:
            subprocess.run(
                ["psql", "-U", db_user, "-d", db_name, "-c", "CREATE EXTENSION IF NOT EXISTS vector;"],
                check=True,
                capture_output=True,
                text=True,
                env=dict(os.environ, PGPASSWORD=db_password)
            )
            logger.info("pgvector extension created successfully")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Error creating pgvector extension: {e}")
            if e.stderr:
                logger.warning(f"Error details: {e.stderr}")
            logger.warning("Vector search functionality may not be available")
        
        # Modify init_db.py to force initialization
        logger.info("Modifying init_db.py to force initialization...")
        init_db_path = os.path.join(root_dir, "backend", "app", "db", "init_db.py")
        
        with open(init_db_path, 'r') as f:
            content = f.read()
        
        # Backup the original file
        with open(init_db_path + '.bak', 'w') as f:
            f.write(content)
        
        # Make sure the check always passes
        modified_content = content.replace(
            "existing_projects = project_repository.get_multi(db, limit=1)", 
            "existing_projects = []  # Force initialization"
        )
        
        with open(init_db_path, 'w') as f:
            f.write(modified_content)
        
        logger.info("init_db.py modified to force initialization")
        
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
        env_path = os.path.join(root_dir, "backend", ".env")
        with open(env_path, 'w') as f:
            f.write(env_content.strip())
        logger.info("Created .env file with database connection details")
        
        logger.info("\nDatabase recreated successfully!")
        logger.info("Next steps:")
        logger.info("1. Run 'python scripts/setup_database.py' to initialize the database with sample data")
        logger.info("2. Start your application with 'start_services.bat'")
        
    except Exception as e:
        logger.error(f"Error recreating database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()