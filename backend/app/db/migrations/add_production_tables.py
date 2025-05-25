"""
Migration script to add production-ready tables:
- personal_profiles
- user_preferences  
- message_contexts

Run this script to update existing databases with new tables.
"""

import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import SessionLocal, engine
from app.db.models import PersonalProfile, UserPreferences, MessageContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Add new production tables to existing database."""
    db = SessionLocal()
    
    try:
        # Create new tables
        PersonalProfile.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created personal_profiles table")
        
        UserPreferences.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created user_preferences table")
        
        MessageContext.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created message_contexts table")
        
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