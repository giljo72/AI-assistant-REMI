#!/usr/bin/env python3
"""
Test script to verify pgvector functionality after migration.
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.models.document import Document, DocumentChunk
from app.rag.vector_store import get_vector_store
from app.services.embedding_service import get_embedding_service
from sqlalchemy import text

async def test_pgvector_search():
    """Test pgvector search functionality."""
    db = SessionLocal()
    
    try:
        print("Testing pgvector search functionality...\n")
        
        # 1. Check if pgvector extension is installed
        result = db.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector';")).fetchone()
        if result:
            print("✓ pgvector extension is installed")
        else:
            print("✗ pgvector extension is NOT installed")
            return
        
        # 2. Check column type
        result = db.execute(text("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns 
            WHERE table_name = 'document_chunks' 
            AND column_name = 'embedding';
        """)).fetchone()
        
        if result:
            print(f"✓ Embedding column exists: type={result.data_type}, udt_name={result.udt_name}")
        else:
            print("✗ Embedding column does not exist")
            return
        
        # 3. Check if there are any documents with embeddings
        chunk_count = db.query(DocumentChunk).filter(DocumentChunk.embedding != None).count()
        print(f"\nFound {chunk_count} chunks with embeddings")
        
        if chunk_count == 0:
            print("No chunks with embeddings found. Please process some documents first.")
            return
        
        # 4. Get a sample chunk to test search
        sample_chunk = db.query(DocumentChunk).filter(DocumentChunk.embedding != None).first()
        print(f"\nSample chunk content: {sample_chunk.content[:100]}...")
        
        # 5. Initialize embedding service and vector store
        embedding_service = get_embedding_service()
        await embedding_service.initialize()
        
        vector_store = get_vector_store(db, embedding_service)
        
        # 6. Generate a test query embedding
        test_query = "test query for document search"
        print(f"\nGenerating embedding for query: '{test_query}'")
        query_embedding = await embedding_service.embed_text(test_query)
        print(f"✓ Generated embedding with dimension: {len(query_embedding)}")
        
        # 7. Test similarity search
        print("\nTesting similarity search...")
        
        # Get the project ID from the sample chunk
        document = db.query(Document).filter_by(id=sample_chunk.document_id).first()
        project_id = None
        if document and document.project_documents:
            project_id = document.project_documents[0].project_id
            print(f"Using project_id: {project_id}")
        
        # Perform search with very low threshold
        results = vector_store.similarity_search(
            query_embedding=query_embedding,
            project_id=project_id,
            limit=5,
            similarity_threshold=0.1  # Very low threshold for testing
        )
        
        print(f"\nSearch returned {len(results)} results:")
        for i, result in enumerate(results):
            print(f"\n{i+1}. Document: {result['filename']}")
            print(f"   Similarity: {result['similarity']:.4f}")
            print(f"   Content: {result['content'][:100]}...")
        
        if not results:
            # Try a direct SQL query to debug
            print("\nNo results found. Testing with direct SQL...")
            
            # Check if embeddings are stored correctly
            test_result = db.execute(text("""
                SELECT 
                    dc.id,
                    dc.content,
                    dc.embedding IS NOT NULL as has_embedding,
                    pg_typeof(dc.embedding) as embedding_type
                FROM document_chunks dc
                LIMIT 5;
            """)).fetchall()
            
            print("\nDirect SQL test results:")
            for row in test_result:
                print(f"  ID: {row.id}, Has embedding: {row.has_embedding}, Type: {row.embedding_type}")
        
        print("\n✓ Test completed")
        
    except Exception as e:
        print(f"\n✗ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_pgvector_search())