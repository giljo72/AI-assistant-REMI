#!/usr/bin/env python3
"""
Database reset script for AI Assistant.
This script drops all tables and recreates a clean database.
"""

import os
import sys
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to reset the database."""
    try:
        # Import database components
        from backend.app.db.database import Base, engine, SessionLocal
        from sqlalchemy import text, inspect
        
        logger.info("Connecting to database...")
        db = SessionLocal()
        
        # Drop all tables
        logger.info("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Tables dropped successfully")
        
        # Recreate tables
        logger.info("Recreating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables recreated successfully")
        
        # Reset pgvector extension
        try:
            logger.info("Resetting pgvector extension...")
            db.execute(text("DROP EXTENSION IF EXISTS vector;"))
            db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            db.commit()
            logger.info("pgvector extension reset successfully")
        except Exception as e:
            logger.warning(f"pgvector reset error: {e}")
            db.rollback()
        
        # Modify the repository check in init_db.py to force initialization
        logger.info("Modifying init_db check to force reinitialization...")
        try:
            # Create a temporary version of init_db.py that always initializes
            init_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                       "backend", "app", "db", "init_db.py")
            with open(init_db_path, 'r') as f:
                content = f.read()
            
            # Backup the original file
            with open(init_db_path + '.bak', 'w') as f:
                f.write(content)
            
            # Modify the check for existing projects to force initialization
            # Original: existing_projects = project_repository.get_multi(db, limit=1)
            # Modified: existing_projects = []
            modified_content = content.replace(
                "existing_projects = project_repository.get_multi(db, limit=1)", 
                "existing_projects = []  # Force initialization"
            )
            
            with open(init_db_path, 'w') as f:
                f.write(modified_content)
                
            logger.info("init_db.py modified to force initialization")
        except Exception as e:
            logger.warning(f"Failed to modify init_db.py: {e}")
            logger.warning("You may need to manually modify backend/app/db/init_db.py")
            logger.warning("Change 'existing_projects = project_repository.get_multi(db, limit=1)' to 'existing_projects = []'")
        
        db.close()
        logger.info("Database reset completed successfully!")
        logger.info("Now run 'scripts/setup_database.py' to initialize with sample data.")
        logger.info("After setup completes, restore the original init_db.py if it was modified.")
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()