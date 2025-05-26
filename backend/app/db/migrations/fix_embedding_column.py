"""
Migration to convert embedding column from Text to pgvector Vector type.
This fixes the issue where embeddings were stored as JSON strings instead of
proper vector embeddings, preventing similarity search from working.
"""

import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def run_migration(db: Session) -> bool:
    """
    Convert embedding column from Text to Vector type for pgvector support.
    """
    try:
        logger.info("Starting migration: Converting embedding column to pgvector Vector type")
        
        # First, ensure pgvector extension is enabled
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        db.commit()
        logger.info("pgvector extension verified")
        
        # Check if the embedding column exists and its current type
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'document_chunks' 
            AND column_name = 'embedding';
        """)).fetchone()
        
        if not result:
            logger.error("embedding column not found in document_chunks table")
            return False
            
        current_type = result.data_type
        logger.info(f"Current embedding column type: {current_type}")
        
        if current_type == 'text':
            # Create a temporary column for the vector data
            logger.info("Creating temporary vector column")
            db.execute(text("""
                ALTER TABLE document_chunks 
                ADD COLUMN IF NOT EXISTS embedding_vector vector(768);
            """))
            db.commit()
            
            # Convert existing JSON embeddings to vector format
            logger.info("Converting existing embeddings to vector format")
            
            # First, let's check if there are any embeddings to convert
            count_result = db.execute(text("""
                SELECT COUNT(*) as count 
                FROM document_chunks 
                WHERE embedding IS NOT NULL AND embedding != '';
            """)).fetchone()
            
            if count_result and count_result.count > 0:
                logger.info(f"Found {count_result.count} embeddings to convert")
                
                # Convert embeddings in batches to avoid memory issues
                batch_size = 100
                offset = 0
                
                while True:
                    # Get a batch of chunks with embeddings
                    chunks = db.execute(text(f"""
                        SELECT id, embedding 
                        FROM document_chunks 
                        WHERE embedding IS NOT NULL 
                        AND embedding != ''
                        ORDER BY id
                        LIMIT {batch_size} OFFSET {offset};
                    """)).fetchall()
                    
                    if not chunks:
                        break
                    
                    # Convert each embedding
                    for chunk in chunks:
                        try:
                            # Check if it's a mock embedding
                            if chunk.embedding.startswith('mock_embedding_'):
                                logger.info(f"Skipping mock embedding for chunk {chunk.id}")
                                # Set to NULL for mock embeddings - they'll be regenerated
                                db.execute(text("""
                                    UPDATE document_chunks 
                                    SET embedding_vector = NULL 
                                    WHERE id = :id;
                                """), {"id": chunk.id})
                            elif chunk.embedding.startswith('[') and chunk.embedding.endswith(']'):
                                # It's already in pgvector format
                                db.execute(text("""
                                    UPDATE document_chunks 
                                    SET embedding_vector = :embedding::vector 
                                    WHERE id = :id;
                                """), {"embedding": chunk.embedding, "id": chunk.id})
                            else:
                                # Try to parse as JSON
                                import json
                                embedding_list = json.loads(chunk.embedding)
                                # Format for pgvector
                                pgvector_format = f"[{','.join(str(x) for x in embedding_list)}]"
                                db.execute(text("""
                                    UPDATE document_chunks 
                                    SET embedding_vector = :embedding::vector 
                                    WHERE id = :id;
                                """), {"embedding": pgvector_format, "id": chunk.id})
                        except Exception as e:
                            logger.warning(f"Failed to convert embedding for chunk {chunk.id}: {e}")
                            # Rollback the transaction and start fresh
                            db.rollback()
                            # Set to NULL for failed conversions in a new transaction
                            db.execute(text("""
                                UPDATE document_chunks 
                                SET embedding_vector = NULL 
                                WHERE id = :id;
                            """), {"id": chunk.id})
                            db.commit()
                    
                    db.commit()
                    offset += batch_size
                    logger.info(f"Converted {min(offset, count_result.count)}/{count_result.count} embeddings")
            
            # Drop the old embedding column
            logger.info("Dropping old embedding column")
            db.execute(text("ALTER TABLE document_chunks DROP COLUMN embedding;"))
            db.commit()
            
            # Rename the new column
            logger.info("Renaming embedding_vector to embedding")
            db.execute(text("""
                ALTER TABLE document_chunks 
                RENAME COLUMN embedding_vector TO embedding;
            """))
            db.commit()
            
            # Create an index for efficient similarity search
            logger.info("Creating index for similarity search")
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
                ON document_chunks 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """))
            db.commit()
            
            logger.info("Migration completed successfully")
            return True
            
        elif 'vector' in current_type.lower():
            logger.info("Embedding column is already using vector type")
            
            # Just ensure the index exists
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
                ON document_chunks 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """))
            db.commit()
            
            return True
            
        else:
            logger.error(f"Unexpected embedding column type: {current_type}")
            return False
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        db.rollback()
        return False


if __name__ == "__main__":
    # Test the migration
    from ..database import SessionLocal
    
    db = SessionLocal()
    try:
        success = run_migration(db)
        if success:
            print("Migration completed successfully")
        else:
            print("Migration failed")
    finally:
        db.close()