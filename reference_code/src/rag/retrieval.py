# src/rag/retrieval.py
from typing import List, Dict, Any, Optional
import logging

from ..db.repositories.vector_repo import VectorRepository
from ..db.repositories.project_repo import ProjectRepository
from .embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

class DocumentRetriever:
    """Retrieves relevant document chunks based on query embeddings"""
    
    def __init__(self, 
                vector_repo: VectorRepository, 
                project_repo: ProjectRepository,
                embedding_generator: EmbeddingGenerator):
        """
        Initialize the document retriever
        
        Args:
            vector_repo: Repository for vector operations
            project_repo: Repository for project operations
            embedding_generator: Generator for embeddings
        """
        self.vector_repo = vector_repo
        self.project_repo = project_repo
        self.embedding_generator = embedding_generator
        
    def retrieve_for_query(self, 
                         query: str, 
                         project_id: Optional[int] = None,
                         limit: int = 5,
                         filter_tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a query
        
        Args:
            query: Query text
            project_id: Optional project ID to filter by
            limit: Maximum number of results to return
            filter_tags: Optional list of document tags to filter by
            
        Returns:
            List of relevant document chunks with similarity scores
        """
        # Generate embedding for the query
        query_embedding = self.embedding_generator.generate_query_embedding(query)
        
        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return []
        
        # Filter documents by project if specified
        filter_document_ids = None
        
        if project_id:
            # Get all documents associated with this project
            project_documents = self.project_repo.get_project_documents(project_id)
            
            if project_documents:
                filter_document_ids = [doc['id'] for doc in project_documents]
            else:
                # No documents in project, return empty results
                logger.info(f"No documents found for project {project_id}")
                return []
        
        # Perform vector search
        results = self.vector_repo.search_similar(
            query_embedding=query_embedding,
            limit=limit,
            filter_document_ids=filter_document_ids,
            filter_tags=filter_tags
        )
        
        return results
    
    def retrieve_from_documents(self,
                              query: str,
                              document_ids: List[int],
                              limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks from specific documents
        
        Args:
            query: Query text
            document_ids: List of document IDs to search within
            limit: Maximum number of results to return
            
        Returns:
            List of relevant document chunks with similarity scores
        """
        # Generate embedding for the query
        query_embedding = self.embedding_generator.generate_query_embedding(query)
        
        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return []
        
        if not document_ids:
            logger.warning("No document IDs provided for retrieval")
            return []
        
        # Perform vector search limited to specified documents
        results = self.vector_repo.search_similar(
            query_embedding=query_embedding,
            limit=limit,
            filter_document_ids=document_ids
        )
        
        # Log the retrieval results
        logger.info(f"Retrieved {len(results)} chunks from specified documents {document_ids}")
        
        return results
    
    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks into a context for the LLM
        
        Args:
            results: List of retrieved document chunks
            
        Returns:
            Formatted context string
        """
        if not results:
            return ""
        
        context_parts = []
        
        for i, result in enumerate(results):
            similarity = result.get('similarity', 0) * 100  # Convert to percentage
            
            # Format as a context block
            context_block = f"[Document {i+1}] {result['filename']} (Relevance: {similarity:.1f}%)\n"
            context_block += result['chunk_text']
            
            context_parts.append(context_block)
        
        return "\n\n".join(context_parts)