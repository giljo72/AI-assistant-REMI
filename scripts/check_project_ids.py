#!/usr/bin/env python3
"""
Script to check project IDs in the database and output code for frontend.
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
    """Check project IDs and suggest frontend updates."""
    try:
        # Import database components
        from backend.app.db.database import SessionLocal
        
        logger.info("Connecting to database...")
        db = SessionLocal()
        
        # Query all projects
        result = db.execute(text("SELECT id, name FROM projects ORDER BY created_at"))
        projects = result.fetchall()
        
        logger.info(f"Found {len(projects)} projects in the database:")
        for project_id, project_name in projects:
            logger.info(f"- ID: {project_id}, Name: {project_name}")
            
        # Generate code for frontend update
        logger.info("\nTo make the frontend work, update App.tsx mockProjects array to:")
        logger.info("const mockProjects = [")
        for project_id, project_name in projects:
            logger.info(f"  {{ id: '{project_id}', name: '{project_name}' }},")
        logger.info("];")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error checking project IDs: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()