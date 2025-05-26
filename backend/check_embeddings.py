#!/usr/bin/env python3
"""
Check the current state of embeddings in the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.models.document import Document, DocumentChunk
from sqlalchemy import text

def check_embeddings():
    """Check the current state of embeddings."""
    db = SessionLocal()
    
    try:
        print("Checking embedding state in database...\n")
        
        # 1. Check column info
        result = db.execute(text("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns 
            WHERE table_name = 'document_chunks' 
            AND column_name = 'embedding';
        """)).fetchone()
        
        if result:
            print(f"Embedding column type: {result.data_type} (udt_name: {result.udt_name})")
        else:
            print("Embedding column not found!")
            return
        
        # 2. Get sample embeddings
        print("\nChecking sample embeddings...")
        
        samples = db.execute(text("""
            SELECT 
                id,
                document_id,
                SUBSTRING(content, 1, 50) as content_preview,
                CASE 
                    WHEN embedding IS NULL THEN 'NULL'
                    WHEN embedding::text LIKE 'mock_embedding_%' THEN 'MOCK'
                    WHEN LENGTH(embedding::text) > 100 THEN 'VECTOR'
                    ELSE 'OTHER'
                END as embedding_type,
                SUBSTRING(embedding::text, 1, 50) as embedding_preview
            FROM document_chunks
            LIMIT 10;
        """)).fetchall()
        
        print("\nSample chunks:")
        for sample in samples:
            print(f"\nID: {sample.id}")
            print(f"Content: {sample.content_preview}...")
            print(f"Embedding Type: {sample.embedding_type}")
            print(f"Embedding Preview: {sample.embedding_preview}...")
        
        # 3. Get counts by type
        print("\n\nEmbedding statistics:")
        
        stats = db.execute(text("""
            SELECT 
                CASE 
                    WHEN embedding IS NULL THEN 'NULL'
                    WHEN embedding::text LIKE 'mock_embedding_%' THEN 'MOCK'
                    WHEN LENGTH(embedding::text) > 100 THEN 'VECTOR'
                    ELSE 'OTHER'
                END as embedding_type,
                COUNT(*) as count
            FROM document_chunks
            GROUP BY embedding_type
            ORDER BY count DESC;
        """)).fetchall()
        
        for stat in stats:
            print(f"{stat.embedding_type}: {stat.count} chunks")
        
        # 4. Check if we can query with pgvector
        print("\n\nTesting pgvector functionality...")
        
        try:
            # Try to create a test vector
            test_result = db.execute(text("""
                SELECT '[1,2,3]'::vector as test_vector;
            """)).fetchone()
            
            if test_result:
                print("✓ pgvector is working")
            
            # Check if there's an index
            index_result = db.execute(text("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'document_chunks' 
                AND indexname LIKE '%embedding%';
            """)).fetchall()
            
            if index_result:
                print("\nEmbedding indexes:")
                for idx in index_result:
                    print(f"  - {idx.indexname}")
            else:
                print("\n⚠ No embedding index found")
                
        except Exception as e:
            print(f"✗ pgvector test failed: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_embeddings()