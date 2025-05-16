#!/usr/bin/env python3
"""
Script to get current project IDs for use in the frontend.
"""

import os
import sys
import logging
from sqlalchemy import text
import json

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Get current project IDs for frontend use."""
    try:
        # Import database components
        from backend.app.db.database import SessionLocal, engine
        
        logger.info("Connecting to database...")
        db = SessionLocal()
        
        # Query all projects
        result = db.execute(text("SELECT id, name FROM projects ORDER BY created_at"))
        projects = result.fetchall()
        
        logger.info(f"Found {len(projects)} projects in the database:")
        
        # Format for frontend use
        frontend_projects = []
        for i, (project_id, name) in enumerate(projects, 1):
            logger.info(f"{i}. ID: {project_id}, Name: {name}")
            frontend_projects.append({
                "id": project_id,
                "name": name
            })
        
        # Write to a JSON file for frontend reference
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "frontend", "src", "data", "projects.json")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(frontend_projects, f, indent=2)
        
        logger.info(f"Project data written to {output_path}")
        logger.info("Use this data to update your frontend App.tsx mockProjects array")
        
        # Also print the code to use
        logger.info("\nCode to use in App.tsx:")
        logger.info("const mockProjects = [")
        for project in frontend_projects:
            logger.info(f"  {{ id: '{project['id']}', name: '{project['name']}' }},")
        logger.info("];")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error getting project IDs: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()