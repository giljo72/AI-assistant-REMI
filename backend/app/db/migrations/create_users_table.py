"""
Migration script to add authentication tables:
- users
- project_members (many-to-many association)

Also updates projects table to add owner_id foreign key.

Run this script to add authentication support to the database.
"""

import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import SessionLocal, engine
from app.db.models import User, ProjectMember

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Add authentication tables to existing database."""
    db = SessionLocal()
    
    try:
        # Create users table
        User.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created users table")
        
        # Create project_members association table
        ProjectMember.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created project_members table")
        
        # Add owner_id column to projects table if it doesn't exist
        # This is a migration for existing projects table
        try:
            db.execute(text("ALTER TABLE projects ADD COLUMN owner_id VARCHAR"))
            logger.info("Added owner_id column to projects table")
        except SQLAlchemyError:
            logger.info("owner_id column already exists in projects table")
        
        # Create foreign key constraint if it doesn't exist
        try:
            db.execute(text("""
                ALTER TABLE projects 
                ADD CONSTRAINT fk_projects_owner_id 
                FOREIGN KEY (owner_id) REFERENCES users(id)
            """))
            logger.info("Added foreign key constraint for projects.owner_id")
        except SQLAlchemyError:
            logger.info("Foreign key constraint already exists")
        
        db.commit()
        logger.info("Migration completed successfully")
        
    except SQLAlchemyError as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()