#!/usr/bin/env python3
"""
Script to fix files stuck in processing state.
This manually sets files to processed=True for development purposes.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.database import DATABASE_URL
from app.db.models.document import Document
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_stuck_files():
    """Fix files that are stuck in processing state."""
    
    # Get database connection
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    
    try:
        # Find files that are not processed and not failed
        stuck_files = session.query(Document).filter(
            Document.is_processed == False,
            Document.is_processing_failed == False
        ).all()
        
        logger.info(f"Found {len(stuck_files)} files stuck in processing")
        
        for document in stuck_files:
            logger.info(f"Processing document: {document.id} - {document.filename}")
            
            # Set as processed with mock values
            document.is_processed = True
            document.chunk_count = 5  # Mock chunk count
            
            # Add mock chunks if none exist
            from app.db.models.document import DocumentChunk
            existing_chunks = session.query(DocumentChunk).filter(
                DocumentChunk.document_id == document.id
            ).count()
            
            if existing_chunks == 0:
                # Create mock chunks
                for i in range(5):
                    chunk = DocumentChunk(
                        document_id=document.id,
                        content=f"Mock chunk {i+1} for document {document.filename}",
                        chunk_index=i,
                        meta_data={"mock": True, "chunk_size": 50},
                        embedding="[0.1, 0.2, 0.3]"  # Mock embedding
                    )
                    session.add(chunk)
                    
                logger.info(f"Added 5 mock chunks for document {document.id}")
        
        # Commit changes
        session.commit()
        logger.info(f"Successfully fixed {len(stuck_files)} stuck files")
        
        # Show current status
        total_files = session.query(Document).count()
        processed_files = session.query(Document).filter(Document.is_processed == True).count()
        failed_files = session.query(Document).filter(Document.is_processing_failed == True).count()
        
        logger.info(f"Current status: {processed_files}/{total_files} processed, {failed_files} failed")
        
    except Exception as e:
        logger.error(f"Error fixing stuck files: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_stuck_files()