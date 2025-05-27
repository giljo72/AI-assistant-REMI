#!/usr/bin/env python
"""
Migration to change vector dimensions from 768 to 1024 for NIM embeddings.
This will drop and recreate the embedding column with the new dimensions.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from app.db.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_to_nim_embeddings():
    """Change vector dimensions from 768 to 1024"""
    
    with engine.connect() as conn:
        try:
            # Start transaction
            trans = conn.begin()
            
            logger.info("Starting migration to NIM embeddings (1024 dimensions)...")
            
            # Drop the old embedding column
            logger.info("Dropping old embedding column (768 dimensions)...")
            conn.execute(text("ALTER TABLE document_chunks DROP COLUMN IF EXISTS embedding"))
            
            # Add new embedding column with 1024 dimensions
            logger.info("Creating new embedding column (1024 dimensions)...")
            conn.execute(text("ALTER TABLE document_chunks ADD COLUMN embedding vector(1024)"))
            
            # Clear the processed flag on all documents so they'll be re-embedded
            logger.info("Resetting document processing flags...")
            conn.execute(text("UPDATE documents SET is_processed = false"))
            
            # Clear processing status file
            import json
            status_file = "/mnt/f/assistant/backend/data/processing_status.json"
            if os.path.exists(status_file):
                with open(status_file, 'w') as f:
                    json.dump({}, f)
                logger.info("Cleared processing status file")
            
            # Commit transaction
            trans.commit()
            
            logger.info("✅ Migration completed successfully!")
            logger.info("   - Vector dimensions changed from 768 to 1024")
            logger.info("   - All documents marked for re-processing")
            logger.info("   - Ready for NIM embeddings")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            trans.rollback()
            raise

if __name__ == "__main__":
    response = input("This will delete all existing embeddings and prepare for NIM. Continue? (y/n): ")
    if response.lower() == 'y':
        migrate_to_nim_embeddings()
    else:
        print("Migration cancelled.")