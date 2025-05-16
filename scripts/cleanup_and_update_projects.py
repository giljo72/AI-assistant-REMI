#!/usr/bin/env python3
"""
Script to clean up duplicate projects and update project IDs to match frontend expectations.
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
    """Clean up duplicate projects and update IDs to match frontend expectations."""
    try:
        # Import database components
        from backend.app.db.database import SessionLocal, engine
        
        logger.info("Connecting to database...")
        db = SessionLocal()
        
        # Query all projects
        result = db.execute(text("SELECT id, name, created_at FROM projects ORDER BY name, created_at"))
        projects = result.fetchall()
        
        logger.info(f"Found {len(projects)} projects in the database:")
        for i, (project_id, name, created_at) in enumerate(projects):
            logger.info(f"{i+1}. ID: {project_id}, Name: {name}, Created: {created_at}")
        
        # Group by name to find duplicates
        projects_by_name = {}
        for project_id, name, created_at in projects:
            if name not in projects_by_name:
                projects_by_name[name] = []
            projects_by_name[name].append((project_id, created_at))
        
        # For each name, keep only the newest project and delete others
        logger.info("\nCleaning up duplicate projects...")
        kept_projects = []
        for name, project_entries in projects_by_name.items():
            # Sort by created_at in descending order (newest first)
            sorted_entries = sorted(project_entries, key=lambda x: x[1], reverse=True)
            
            # Keep the newest
            kept_id, kept_date = sorted_entries[0]
            kept_projects.append((kept_id, name))
            logger.info(f"Keeping project '{name}' with ID: {kept_id}, Created: {kept_date}")
            
            # Delete the rest
            for delete_id, delete_date in sorted_entries[1:]:
                logger.info(f"Deleting duplicate project '{name}' with ID: {delete_id}, Created: {delete_date}")
                try:
                    # Delete dependencies first (if any)
                    for table_name in ["user_prompts", "chats", "project_documents"]:
                        try:
                            db.execute(
                                text(f"DELETE FROM {table_name} WHERE project_id = :project_id"),
                                {"project_id": delete_id}
                            )
                        except Exception as e:
                            logger.warning(f"Failed to delete related records in {table_name}: {e}")
                    
                    # Delete the project
                    db.execute(
                        text("DELETE FROM projects WHERE id = :project_id"),
                        {"project_id": delete_id}
                    )
                except Exception as e:
                    logger.error(f"Failed to delete project {delete_id}: {e}")
        
        # Commit the deletion of duplicates
        db.commit()
        
        # Now update the IDs of the kept projects to match frontend expectations
        logger.info("\nUpdating project IDs...")
        
        # Create a mapping from old IDs to new numeric IDs
        id_mapping = {}
        for i, (old_id, name) in enumerate(kept_projects, 1):
            new_id = str(i)
            id_mapping[old_id] = new_id
        
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
        logger.info("\nProject cleanup and ID update completed successfully!")
        
    except Exception as e:
        logger.error(f"Error updating project IDs: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()