#!/usr/bin/env python3
"""
Script to update the init_db.py check to prevent duplicate projects.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Update init_db.py to check for existing projects."""
    try:
        # Change to the project root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        init_db_path = os.path.join(root_dir, "backend", "app", "db", "init_db.py")
        
        logger.info(f"Reading {init_db_path}...")
        with open(init_db_path, 'r') as f:
            content = f.read()
        
        # Backup the file
        backup_path = init_db_path + '.bak'
        logger.info(f"Creating backup at {backup_path}...")
        with open(backup_path, 'w') as f:
            f.write(content)
        
        # Update the check for existing projects
        logger.info("Updating the check for existing projects...")
        updated_content = content.replace(
            "existing_projects = []  # Force initialization",
            "existing_projects = project_repository.get_multi(db, limit=1)"
        )
        
        if updated_content == content:
            logger.info("The check was already updated. No changes needed.")
            return
        
        # Write the updated file
        logger.info("Writing updated file...")
        with open(init_db_path, 'w') as f:
            f.write(updated_content)
        
        logger.info("init_db.py updated successfully!")
        logger.info("Now when you start the application, it won't create duplicate projects.")
        
    except Exception as e:
        logger.error(f"Error updating init_db.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()