# src/db/repositories/vector_repo.py
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import json
from sqlalchemy import select, delete, func, text
from sqlalchemy.exc import SQLAlchemyError
import logging
import numpy as np

from ...core.db_interface import get_db_session
from ..models import DocumentEmbedding, Document

logger = logging.getLogger(__name__)

class VectorRepository:
    """Repository for vector embedding operations"""
    
    def add_embedding(self, 
                     document_id: int, 
                     chunk_index: int,
                     chunk_text: str,
                     embedding: List[float],
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a vector embedding for a document chunk
        
        Args:
            document_id: ID of the document this embedding belongs to
            chunk_index: Index of the chunk within the document
            chunk_text: Text content of the chunk
            embedding: Vector embedding as a list of floats
            metadata: Optional metadata for this chunk
            
        Returns:
            Embedding record as dictionary if successful
        """
        try:
            # Create a content hash to prevent duplicates
            hash_content = f"{document_id}_{chunk_index}_{chunk_text[:100]}"
            content_hash = hashlib.md5(hash_content.encode()).hexdigest()
            
            with get_db_session() as session:
                # Check if this embedding already exists
                stmt = select(DocumentEmbedding).where(DocumentEmbedding.content_hash == content_hash)
                existing = session.execute(stmt).scalar_one_or_none()
                
                if existing:
                    logger.info(f"Embedding already exists for document {document_id}, chunk {chunk_index}")
                    return {
                        'id': existing.id,
                        'document_id': existing.document_id,
                        'content_hash': existing.content_hash,
                        'metadata': existing.chunk_metadata
                    }
                
                # Create new embedding
                embedding_record = DocumentEmbedding(
                    document_id=document_id,
                    content_hash=content_hash,
                    embedding=embedding,
                    chunk_index=chunk_index,
                    chunk_text=chunk_text,
                    chunk_metadata=metadata
                )
                
                session.add(embedding_record)
                session.flush()  # To get the ID
                
                logger.info(f"Added embedding for document {document_id}, chunk {chunk_index} (ID: {embedding_record.id})")
                
                # Update document chunk count
                session.execute(
                    text("UPDATE documents SET chunk_count = chunk_count + 1 WHERE id = :doc_id"),
                    {"doc_id": document_id}
                )
                
                # Make a copy to return, as the session will be closed
                result = {
                    'id': embedding_record.id,
                    'document_id': embedding_record.document_id,
                    'content_hash': embedding_record.content_hash,
                    'chunk_index': embedding_record.chunk_index,
                    'chunk_text': embedding_record.chunk_text,
                    'metadata': embedding_record.chunk_metadata
                }
                
                return result
        except SQLAlchemyError as e:
            logger.error(f"Database error adding embedding: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding embedding: {e}")
            raise
    
    def delete_document_embeddings(self, document_id: int) -> int:
        """
        Delete all embeddings for a document
        
        Args:
            document_id: ID of document to delete embeddings for
            
        Returns:
            Number of embeddings deleted
        """
        try:
            with get_db_session() as session:
                # Delete the embeddings
                stmt = delete(DocumentEmbedding).where(DocumentEmbedding.document_id == document_id)
                result = session.execute(stmt)
                
                count = result.rowcount
                
                if count > 0:
                    logger.info(f"Deleted {count} embeddings for document {document_id}")
                    
                    # Reset document chunk count
                    session.execute(
                        text("UPDATE documents SET chunk_count = 0 WHERE id = :doc_id"),
                        {"doc_id": document_id}
                    )
                else:
                    logger.info(f"No embeddings found for document {document_id}")
                
                return count
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting document embeddings: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error deleting document embeddings: {e}")
            return 0
    
    def search_similar(self, 
                    query_embedding: List[float],
                    limit: int = 5,
                    filter_document_ids: Optional[List[int]] = None,
                    filter_tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity
        
        Args:
            query_embedding: Query vector embedding
            limit: Maximum number of results to return
            filter_document_ids: Optional list of document IDs to filter by
            filter_tags: Optional list of document tags to filter by
            
        Returns:
            List of matching document chunks with similarity scores
        """
        try:
            # Check if we need to resize the embedding
            if len(query_embedding) != 1536:
                logger.warning(f"Embedding dimension mismatch. Expected 1536, got {len(query_embedding)}. Will normalize to expected dimension.")
                # Truncate or pad the embedding to match the expected dimension
                if len(query_embedding) > 1536:
                    query_embedding = query_embedding[:1536]
                else:
                    # Pad with zeros if too short (shouldn't happen)
                    query_embedding = query_embedding + [0.0] * (1536 - len(query_embedding))
            
            with get_db_session() as session:
                # Create a raw SQL query with the vector cast directly in the query
                # Use bind parameters to avoid SQL injection
                base_query = f"""
                SELECT 
                    e.id, 
                    e.document_id,
                    e.chunk_index,
                    e.chunk_text,
                    d.filename,
                    d.tag,
                    e.chunk_metadata,
                    1 - (e.embedding <=> '{str(query_embedding)}'::vector) as similarity
                FROM 
                    document_embeddings e
                JOIN 
                    documents d ON e.document_id = d.id
                WHERE 
                    d.status = 'Active'
                """
                
                # Add filters if provided
                if filter_document_ids:
                    doc_ids_str = ','.join(str(id) for id in filter_document_ids)
                    base_query += f" AND e.document_id IN ({doc_ids_str})"
                
                if filter_tags:
                    tag_list = "'" + "','".join(filter_tags) + "'"
                    base_query += f" AND d.tag IN ({tag_list})"
                
                # Add order by and limit
                base_query += f" ORDER BY similarity DESC LIMIT {limit}"
                
                # Execute the query
                results = session.execute(text(base_query)).all()
                
                # Convert to dictionaries
                return [
                    {
                        'id': r.id,
                        'document_id': r.document_id,
                        'chunk_index': r.chunk_index,
                        'chunk_text': r.chunk_text,
                        'filename': r.filename,
                        'tag': r.tag,
                        'metadata': r.chunk_metadata or {},
                        'similarity': float(r.similarity)
                    }
                    for r in results
                ]
        except SQLAlchemyError as e:
            logger.error(f"Database error searching vector embeddings: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching vector embeddings: {e}")
            return []