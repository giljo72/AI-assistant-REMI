"""
Migration to update Coding Assistant prompt to be editable (is_default=False)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from sqlalchemy import update
from app.db.database import SessionLocal
from app.db.models.system_prompt import SystemPrompt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_coding_assistant():
    """Update Coding Assistant prompt to be editable"""
    db = SessionLocal()
    try:
        # Find the Coding Assistant prompt
        coding_assistant = db.query(SystemPrompt).filter(
            SystemPrompt.name == "Coding Assistant"
        ).first()
        
        if coding_assistant:
            if coding_assistant.is_default:
                coding_assistant.is_default = False
                db.commit()
                logger.info("Updated Coding Assistant prompt to be editable (is_default=False)")
            else:
                logger.info("Coding Assistant prompt is already editable")
        else:
            logger.info("Coding Assistant prompt not found - will be created as editable when seeded")
        
    except Exception as e:
        logger.error(f"Error updating Coding Assistant prompt: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_coding_assistant()
    print("Migration completed successfully!")