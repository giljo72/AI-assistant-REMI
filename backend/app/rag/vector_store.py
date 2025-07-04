from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import json
import os
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
EMBEDDING_DIMENSIONS = 1024  # Default for NIM embeddings

class VectorStore:
    """
    Interface for storing and retrieving vector embeddings using pgvector.
    
    This class handles the integration with PostgreSQL's pgvector extension
    for efficient vector similarity search.
    """
    
    def __init__(self, db_session: Session, embedding_service=None, embedding_dimensions: int = EMBEDDING_DIMENSIONS):
        """
        Initialize the vector store.
        
        Args:
            db_session: SQLAlchemy database session
            embedding_service: Optional embedding service instance
            embedding_dimensions: Dimension of the embedding vectors
        """
        self.db = db_session
        self.embedding_service = embedding_service
        self.embedding_dimensions = embedding_dimensions
        
        # Ensure pgvector extension is available
        self._initialize_pgvector()
    
    def _initialize_pgvector(self) -> None:
        """
        Initialize the pgvector extension and required tables.
        """
        try:
            # Create the pgvector extension if it doesn't exist
            self.db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            self.db.commit()
            
            # Verify the extension is available
            result = self.db.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector';")).fetchone()
            if not result:
                logger.error("pgvector extension could not be created")
                raise RuntimeError("pgvector extension is not available")
            
            logger.info("pgvector extension verified")
        except Exception as e:
            logger.error(f"Error initializing pgvector: {str(e)}")
            raise
    
    def string_to_vector(self, embedding_str: str) -> List[float]:
        """
        Convert a string representation of an embedding to a list of floats.
        
        Args:
            embedding_str: String representation of an embedding vector
            
        Returns:
            List of float values representing the embedding
        """
        try:
            # Try to parse as JSON first
            return json.loads(embedding_str)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, try comma-separated values
            try:
                return [float(x) for x in embedding_str.strip('[]').split(',')]
            except (ValueError, AttributeError):
                logger.error(f"Could not convert embedding string to vector: {embedding_str[:50]}...")
                # Return a zero vector as fallback
                return [0.0] * self.embedding_dimensions
    
    def format_for_pgvector(self, vector: List[float]) -> str:
        """
        Format a vector for pgvector storage.
        
        Args:
            vector: List of floats representing the embedding vector
            
        Returns:
            String formatted for pgvector
        """
        return f"[{','.join(str(x) for x in vector)}]"
    
    def update_document_embedding(self, document_id: str, chunk_id: str, embedding: List[float]) -> bool:
        """
        Update the embedding for a document chunk.
        
        Args:
            document_id: ID of the document
            chunk_id: ID of the document chunk
            embedding: Vector embedding to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # For pgvector, we can pass the list directly
            # SQLAlchemy with pgvector handles the conversion
            from ..db.models.document import DocumentChunk
            
            chunk = self.db.query(DocumentChunk).filter_by(
                id=chunk_id,
                document_id=document_id
            ).first()
            
            if chunk:
                chunk.embedding = embedding  # pgvector handles list -> vector conversion
                self.db.commit()
                return True
            else:
                logger.error(f"Chunk not found: {chunk_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating document embedding: {str(e)}")
            self.db.rollback()
            return False
    
    def similarity_search(
        self, 
        query_embedding: List[float],
        project_id: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
        chunk_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_embedding: Vector embedding of the query
            project_id: Optional project ID to filter results
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of document chunks with similarity scores
        """
        try:
            # For pgvector with SQLAlchemy, we pass the list directly
            # No need to format as string
            
            # Build the similarity search query
            if project_id:
                # Search within a specific project with prioritization
                query = text("""
                    SELECT 
                        dc.id as chunk_id,
                        dc.document_id,
                        dc.content,
                        dc.chunk_index,
                        dc.meta_data,
                        d.filename,
                        d.filetype,
                        pd.priority,
                        1 - (dc.embedding <=> :query_vector) as similarity
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    JOIN project_documents pd ON d.id = pd.document_id
                    WHERE 
                        pd.project_id = :project_id
                        AND pd.is_active = true
                        AND 1 - (dc.embedding <=> :query_vector) > :similarity_threshold
                    ORDER BY 
                        pd.priority * (1 - (dc.embedding <=> :query_vector)) DESC
                    LIMIT :limit
                """)
                
                # Format the query with the vector literal
                vector_str = self.format_for_pgvector(query_embedding)
                
                result = self.db.execute(
                    text(f"""
                    SELECT 
                        dc.id as chunk_id,
                        dc.document_id,
                        dc.content,
                        dc.chunk_index,
                        dc.meta_data,
                        d.filename,
                        d.filetype,
                        pd.priority,
                        1 - (dc.embedding <=> '{vector_str}'::vector) as similarity
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    JOIN project_documents pd ON d.id = pd.document_id
                    WHERE 
                        pd.project_id = :project_id
                        AND pd.is_active = true
                        AND 1 - (dc.embedding <=> '{vector_str}'::vector) > :similarity_threshold
                    ORDER BY 
                        pd.priority * (1 - (dc.embedding <=> '{vector_str}'::vector)) DESC
                    LIMIT :limit
                    """), 
                    {
                        "project_id": project_id,
                        "similarity_threshold": similarity_threshold,
                        "limit": limit
                    }
                ).fetchall()
            else:
                # Global search across all documents
                query = text("""
                    SELECT 
                        dc.id as chunk_id,
                        dc.document_id,
                        dc.content,
                        dc.chunk_index,
                        dc.meta_data,
                        d.filename,
                        d.filetype,
                        1 - (dc.embedding <=> :query_vector) as similarity
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    WHERE 
                        1 - (dc.embedding <=> :query_vector) > :similarity_threshold
                    ORDER BY 
                        similarity DESC
                    LIMIT :limit
                """)
                
                # Format the query with the vector literal
                vector_str = self.format_for_pgvector(query_embedding)
                
                result = self.db.execute(
                    text(f"""
                    SELECT 
                        dc.id as chunk_id,
                        dc.document_id,
                        dc.content,
                        dc.chunk_index,
                        dc.meta_data,
                        d.filename,
                        d.filetype,
                        1 - (dc.embedding <=> '{vector_str}'::vector) as similarity
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    WHERE 
                        1 - (dc.embedding <=> '{vector_str}'::vector) > :similarity_threshold
                    ORDER BY 
                        similarity DESC
                    LIMIT :limit
                    """), 
                    {
                        "similarity_threshold": similarity_threshold,
                        "limit": limit
                    }
                ).fetchall()
            
            # Convert result to dictionaries
            chunks = []
            for row in result:
                chunk = dict(row._mapping)
                # Convert JSON string to dict if needed
                if isinstance(chunk.get("meta_data"), str):
                    try:
                        chunk["meta_data"] = json.loads(chunk["meta_data"])
                    except (json.JSONDecodeError, TypeError):
                        pass
                chunks.append(chunk)
            
            return chunks
        
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text using NIM.
        
        REQUIRES NIM embedding service - no fallback to mock embeddings.
        
        Args:
            text: Text to generate an embedding for
            
        Returns:
            Embedding vector
            
        Raises:
            Exception: If NIM service is not available or fails
        """
        if not self.embedding_service:
            raise Exception("NIM embedding service is required but not configured")
            
        try:
            # Validate and clean the text
            if not text or not text.strip():
                raise ValueError("Cannot generate embedding for empty text")
            
            # Clean the text - remove null bytes and normalize whitespace
            cleaned_text = text.replace('\x00', '').strip()
            
            # Ensure text isn't too long (NIM might have limits)
            max_length = 8192  # Typical limit for embedding models
            if len(cleaned_text) > max_length:
                logger.warning(f"Text too long ({len(cleaned_text)} chars), truncating to {max_length}")
                cleaned_text = cleaned_text[:max_length]
            
            # Log text preview for debugging
            logger.debug(f"Generating embedding for text: {cleaned_text[:100]}...")
            
            # Check which method the embedding service supports
            if hasattr(self.embedding_service, 'embed_text'):
                return await self.embedding_service.embed_text(cleaned_text)
            elif hasattr(self.embedding_service, 'embed_documents'):
                # NIM uses embed_documents for text chunks
                embeddings = await self.embedding_service.embed_documents([cleaned_text])
                if not embeddings or len(embeddings) == 0:
                    raise Exception("NIM returned empty embeddings")
                return embeddings[0]
            else:
                raise Exception("Embedding service has no compatible embed method")
        except Exception as e:
            logger.error(f"Failed to generate NIM embedding for text length {len(text)}: {e}")
            raise Exception(f"NIM embedding generation failed: {str(e)}")
    
    # Mock embedding method removed - NIM embeddings are required


# Create a factory function to get the vector store
def get_vector_store(db_session: Session, embedding_service=None) -> VectorStore:
    """
    Get a VectorStore instance.
    
    Args:
        db_session: SQLAlchemy database session
        embedding_service: Optional embedding service instance
        
    Returns:
        Initialized VectorStore
    """
    return VectorStore(db_session, embedding_service)