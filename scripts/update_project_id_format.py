#!/usr/bin/env python3
"""
Script to update project IDs to match frontend expectations.
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
    """Update project IDs in the database to match frontend expectations."""
    try:
        # Import database components
        from backend.app.db.database import SessionLocal, engine
        
        logger.info("Connecting to database...")
        db = SessionLocal()
        
        # Query all projects
        result = db.execute(text("SELECT id, name FROM projects ORDER BY created_at"))
        projects = result.fetchall()
        
        logger.info(f"Found {len(projects)} projects in the database:")
        
        # First, store the mapping of old_id -> new_id
        id_mapping = {}
        for i, (old_id, name) in enumerate(projects, 1):
            new_id = str(i)
            id_mapping[old_id] = new_id
            logger.info(f"- Before: ID: {old_id}, Name: {name}")
            logger.info(f"  Will update to: ID: {new_id}")
        
        # Create temporary IDs to avoid conflicts during update
        for old_id, new_id in id_mapping.items():
            temp_id = f"temp_{old_id}"
            
            # Update the project ID to a temporary ID first
            try:
                db.execute(
                    text("UPDATE projects SET id = :temp_id WHERE id = :old_id"),
                    {"temp_id": temp_id, "old_id": old_id}
                )
                logger.info(f"Updated project {old_id} to temporary ID: {temp_id}")
                
                # Update related records to the temporary ID
                for table_name in ["user_prompts", "chats", "project_documents"]:
                    try:
                        db.execute(
                            text(f"UPDATE {table_name} SET project_id = :temp_id WHERE project_id = :old_id"),
                            {"temp_id": temp_id, "old_id": old_id}
                        )
                        logger.info(f"Updated related records in {table_name}")
                    except Exception as e:
                        logger.warning(f"Failed to update {table_name}: {e}")
                
            except Exception as e:
                logger.error(f"Failed to update project to temporary ID: {e}")
                db.rollback()
                return
        
        # Commit the temporary ID changes
        db.commit()
        
        # Now update from temporary IDs to the final numeric IDs
        for old_id, new_id in id_mapping.items():
            temp_id = f"temp_{old_id}"
            
            try:
                # Update from temporary ID to final numeric ID
                db.execute(
                    text("UPDATE projects SET id = :new_id WHERE id = :temp_id"),
                    {"new_id": new_id, "temp_id": temp_id}
                )
                logger.info(f"Updated project from temporary ID to final ID: {new_id}")
                
                # Update related records to the final numeric ID
                for table_name in ["user_prompts", "chats", "project_documents"]:
                    try:
                        db.execute(
                            text(f"UPDATE {table_name} SET project_id = :new_id WHERE project_id = :temp_id"),
                            {"new_id": new_id, "temp_id": temp_id}
                        )
                        logger.info(f"Updated related records in {table_name} to final ID")
                    except Exception as e:
                        logger.warning(f"Failed to update {table_name} to final ID: {e}")
                
            except Exception as e:
                logger.error(f"Failed to update project to final ID: {e}")
                db.rollback()
                return
        
        # Commit the final changes
        db.commit()
        
        # Verify the changes
        logger.info("\nVerifying updated projects:")
        result = db.execute(text("SELECT id, name FROM projects ORDER BY id"))
        updated_projects = result.fetchall()
        
        for project_id, project_name in updated_projects:
            logger.info(f"- After: ID: {project_id}, Name: {project_name}")
            
        db.close()
        logger.info("\nProject IDs updated successfully!")
        
    except Exception as e:
        logger.error(f"Error updating project IDs: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()