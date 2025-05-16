#!/usr/bin/env python3
"""
Script to check project IDs in the database.
"""

import os
import sys
import logging
from sqlalchemy import text

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Check the projects in the database."""
    try:
        # Import database components
        from backend.app.db.database import SessionLocal, engine
        
        logger.info("Connecting to database...")
        db = SessionLocal()
        
        # Use raw SQL to query projects to avoid model relationship issues
        result = db.execute(text("SELECT id, name FROM projects"))
        projects = result.fetchall()
        
        logger.info(f"Found {len(projects)} projects in the database:")
        for project in projects:
            project_id, project_name = project
            logger.info(f"- ID: {project_id}, Name: {project_name}")
            
        db.close()
        
    except Exception as e:
        logger.error(f"Error checking projects: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()