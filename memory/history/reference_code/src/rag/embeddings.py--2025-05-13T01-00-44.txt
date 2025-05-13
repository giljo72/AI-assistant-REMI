# src/rag/embeddings.py
from typing import List, Dict, Any, Optional
import logging
import numpy as np
import time
import hashlib
import tenacity
from tenacity import retry, stop_after_attempt, wait_exponential
import requests

from ..core.config import get_settings
from ..db.repositories.vector_repo import VectorRepository

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generates and stores vector embeddings for document chunks"""
    
    def __init__(self, vector_repo: VectorRepository):
        """
        Initialize the embedding generator
        
        Args:
            vector_repo: Repository for vector operations
        """
        self.vector_repo = vector_repo
        self.settings = get_settings()
        self.dimension = self.settings['database'].get('vector_dimension', 1536)
        self.model = self.settings['rag'].get('embedding_model', 'text-embedding-ada-002')
        self.ollama_host = self.settings['ollama'].get('host', 'localhost')
        self.ollama_port = self.settings['ollama'].get('port', '11434')
        self.ollama_model = self.settings['ollama'].get('model', 'llama3:8b')
        self.ollama_url = f"http://{self.ollama_host}:{self.ollama_port}/api/embeddings"
    
    def generate_for_document(self, 
                             document_id: int, 
                             chunks: List[Dict[str, Any]]) -> int:
        """
        Generate embeddings for all chunks from a document
        
        Args:
            document_id: ID of the document
            chunks: List of text chunks with metadata
            
        Returns:
            Number of embeddings created
        """
        count = 0
        
        for chunk in chunks:
            try:
                text = chunk['text']
                chunk_index = chunk.get('chunk_index', count)
                
                # Generate embedding
                embedding = self.generate_embedding(text)
                
                if embedding:
                    # Store embedding in database
                    self.vector_repo.add_embedding(
                        document_id=document_id,
                        chunk_index=chunk_index,
                        chunk_text=text,
                        embedding=embedding,
                        metadata=chunk.get('metadata')
                    )
                    count += 1
                else:
                    logger.warning(f"Failed to generate embedding for chunk {chunk_index} of document {document_id}")
            except Exception as e:
                logger.error(f"Error generating embedding for chunk: {e}")
        
        logger.info(f"Generated {count} embeddings for document {document_id}")
        return count
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a text chunk using Ollama
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector as list of floats if successful, None otherwise
        """
        try:
            # Truncate text if too long (most embedding models have limits)
            # A conservative limit for most models is around 8K tokens
            if len(text) > 8000:
                logger.warning(f"Text too long ({len(text)} chars), truncating to 8000 chars")
                text = text[:8000]
            
            payload = {
                "model": self.ollama_model,
                "prompt": text
            }
            
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=30  # 30 second timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get('embedding', [])
                
                # Check if embedding has expected dimension
                if len(embedding) != self.dimension:
                    logger.warning(
                        f"Embedding dimension mismatch. Expected {self.dimension}, got {len(embedding)}. "
                        f"Will normalize to expected dimension."
                    )
                    
                    # Normalize to expected dimension using padding or truncation
                    if len(embedding) < self.dimension:
                        # Pad with zeros
                        embedding.extend([0.0] * (self.dimension - len(embedding)))
                    else:
                        # Truncate
                        embedding = embedding[:self.dimension]
                
                return embedding
            else:
                logger.error(f"Error from Ollama API: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def generate_query_embedding(self, query: str) -> Optional[List[float]]:
        """
        Generate embedding for a search query
        
        Args:
            query: Search query text
            
        Returns:
            Embedding vector as list of floats if successful, None otherwise
        """
        # Use the same process as for document chunks
        return self.generate_embedding(query)
    
    def delete_document_embeddings(self, document_id: int) -> int:
        """
        Delete all embeddings for a document
        
        Args:
            document_id: ID of document to delete embeddings for
            
        Returns:
            Number of embeddings deleted
        """
        return self.vector_repo.delete_document_embeddings(document_id)