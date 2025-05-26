#!/usr/bin/env python3
"""
Regenerate embeddings for all documents using the real embedding service.
This replaces mock embeddings with actual sentence-transformer embeddings.
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.models.document import Document, DocumentChunk
from app.services.embedding_service import get_embedding_service
from app.rag.vector_store import get_vector_store
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def regenerate_embeddings():
    """Regenerate embeddings for all document chunks."""
    db = SessionLocal()
    
    try:
        print("Starting embedding regeneration...")
        print("This will replace all mock embeddings with real sentence-transformer embeddings.")
        print()
        
        # Get counts
        total_chunks = db.query(DocumentChunk).count()
        # Can't use LIKE on vector column, and we know they're all NULL anyway
        null_chunks = db.query(DocumentChunk).filter(
            DocumentChunk.embedding == None
        ).count()
        
        print(f"Total chunks: {total_chunks}")
        print(f"Null embeddings: {null_chunks}")
        print()
        
        if total_chunks == 0:
            print("No chunks found. Please upload and process some documents first.")
            return
        
        response = input("Do you want to regenerate embeddings? (y/n): ")
        if response.lower() != 'y':
            print("Regeneration cancelled.")
            return
        
        # Initialize services
        print("\nInitializing embedding service...")
        embedding_service = get_embedding_service()
        await embedding_service.initialize()
        vector_store = get_vector_store(db, embedding_service)
        
        print("Embedding service initialized successfully.")
        print(f"Model: {embedding_service.model_name}")
        print(f"Dimension: {embedding_service.dimension}")
        print(f"Device: {embedding_service.device}")
        print()
        
        # Process chunks in batches
        batch_size = 50
        processed = 0
        failed = 0
        
        # Get all chunks that need embeddings (all NULL ones)
        chunks_to_process = db.query(DocumentChunk).filter(
            DocumentChunk.embedding == None
        ).all()
        
        total_to_process = len(chunks_to_process)
        print(f"Processing {total_to_process} chunks...")
        
        # Process in batches
        for i in range(0, total_to_process, batch_size):
            batch = chunks_to_process[i:i+batch_size]
            texts = [chunk.content for chunk in batch]
            
            try:
                # Generate embeddings for the batch
                embeddings = await embedding_service.embed_batch(texts)
                
                # Update each chunk with its embedding
                for chunk, embedding in zip(batch, embeddings):
                    try:
                        # Update the chunk's embedding directly
                        chunk.embedding = embedding  # pgvector handles the conversion
                        db.add(chunk)
                        processed += 1
                    except Exception as e:
                        logger.error(f"Failed to update chunk {chunk.id}: {e}")
                        failed += 1
                
                # Commit the batch
                db.commit()
                
                # Progress update
                print(f"Progress: {processed + failed}/{total_to_process} chunks processed")
                
            except Exception as e:
                logger.error(f"Failed to process batch: {e}")
                db.rollback()
                failed += len(batch)
        
        print(f"\nRegeneration completed!")
        print(f"Successfully processed: {processed} chunks")
        print(f"Failed: {failed} chunks")
        
        # Verify the results
        print("\nVerifying embeddings...")
        
        # Check for null embeddings
        remaining_null = db.query(DocumentChunk).filter(
            DocumentChunk.embedding == None
        ).count()
        
        print(f"Remaining null embeddings: {remaining_null}")
        
        if remaining_null == 0:
            print("\n✓ All embeddings successfully regenerated!")
        else:
            print("\n⚠ Some embeddings could not be regenerated. Check the logs for details.")
        
    except Exception as e:
        print(f"\n✗ Error during regeneration: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(regenerate_embeddings())