"""
Embedding Service for generating text embeddings using sentence-transformers.
This service provides real embeddings to replace the mock implementation.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding service.
        
        Args:
            model_name: The sentence-transformer model to use.
                       Default is all-MiniLM-L6-v2 which produces 384-dim embeddings.
                       For 768-dim (matching our pgvector setup), use:
                       - sentence-transformers/all-mpnet-base-v2
                       - BAAI/bge-base-en-v1.5
        """
        self.model: Optional[SentenceTransformer] = None
        self.model_name = model_name
        self.dimension: Optional[int] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._lock = asyncio.Lock()
        
    async def initialize(self) -> None:
        """Load the embedding model asynchronously."""
        async with self._lock:
            if self.model is not None:
                return
                
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                # Load model in thread to avoid blocking
                self.model = await asyncio.to_thread(
                    SentenceTransformer, 
                    self.model_name,
                    device=self.device
                )
                
                # Get embedding dimension
                test_embedding = await asyncio.to_thread(
                    self.model.encode, 
                    "test",
                    normalize_embeddings=True
                )
                self.dimension = len(test_embedding)
                
                logger.info(f"Embedding model loaded successfully. Dimension: {self.dimension}")
                
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
                
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding
        """
        if not self.model:
            await self.initialize()
            
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.dimension
            
        try:
            # Generate embedding in thread pool
            embedding = await asyncio.to_thread(
                self.model.encode,
                text,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
            
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        if not self.model:
            await self.initialize()
            
        if not texts:
            return []
            
        # Filter out empty texts but remember their positions
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)
                
        if not valid_texts:
            # All texts were empty, return zero vectors
            return [[0.0] * self.dimension for _ in texts]
            
        try:
            # Generate embeddings in batch
            embeddings = await asyncio.to_thread(
                self.model.encode,
                valid_texts,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=32
            )
            
            # Reconstruct full results with zero vectors for empty texts
            results = []
            valid_idx = 0
            for i in range(len(texts)):
                if i in valid_indices:
                    results.append(embeddings[valid_idx].tolist())
                    valid_idx += 1
                else:
                    results.append([0.0] * self.dimension)
                    
            return results
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
            
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if not self.model:
            await self.initialize()
            
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "device": self.device,
            "max_seq_length": self.model.max_seq_length
        }
        
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.model:
            # Clear model from GPU memory if using CUDA
            if self.device == "cuda":
                del self.model
                torch.cuda.empty_cache()
            else:
                del self.model
            self.model = None
            logger.info("Embedding model cleaned up")

# Global instance for dependency injection
_embedding_service: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        # Use a model that produces 768-dimensional embeddings to match pgvector
        _embedding_service = EmbeddingService("sentence-transformers/all-mpnet-base-v2")
    return _embedding_service