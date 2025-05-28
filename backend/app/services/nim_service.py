"""
NVIDIA NIM Service Integration
Provides clean interface to NVIDIA NIM containers for embeddings and text generation
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
import httpx
import json

logger = logging.getLogger(__name__)

class NIMEmbeddingService:
    """Service for NVIDIA NIM Text Embedding"""
    
    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def health_check(self) -> bool:
        """Check if NIM embedding service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/v1/health/ready")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"NIM Embedding health check failed: {e}")
            return False
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents"""
        try:
            # Ensure texts is always a list
            if isinstance(texts, str):
                texts = [texts]
            
            # Filter out empty texts and log them
            valid_texts = []
            for i, text in enumerate(texts):
                if text and text.strip():
                    valid_texts.append(text)
                else:
                    logger.warning(f"Skipping empty text at index {i}")
            
            if not valid_texts:
                raise ValueError("No valid texts to embed after filtering")
            
            # Log the first 100 chars of each text for debugging
            for i, text in enumerate(valid_texts[:3]):  # Only log first 3
                logger.debug(f"Text {i} preview: {text[:100]}...")
            
            payload = {
                "input": valid_texts,
                "model": "nvidia/nv-embedqa-e5-v5",
                "input_type": "passage"  # Use passage for document chunks
            }
            
            logger.debug(f"Sending {len(valid_texts)} texts to NIM for embedding")
            
            response = await self.client.post(
                f"{self.base_url}/v1/embeddings",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            embeddings = [item["embedding"] for item in result["data"]]
            
            logger.info(f"Generated embeddings for {len(valid_texts)} texts (dimension: {len(embeddings[0]) if embeddings else 0})")
            return embeddings
            
        except httpx.HTTPStatusError as e:
            logger.error(f"NIM API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query"""
        try:
            payload = {
                "input": query,
                "model": "nvidia/nv-embedqa-e5-v5",
                "input_type": "query"  # Use query type for search queries
            }
            
            response = await self.client.post(
                f"{self.base_url}/v1/embeddings",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            embedding = result["data"][0]["embedding"]
            
            logger.info(f"Generated query embedding (dimension: {len(embedding)})")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class NIMGenerationService:
    """Service for NVIDIA NIM Text Generation"""
    
    def __init__(self, model_size: str = "8b", base_url: str = None):
        if base_url is None:
            # Auto-select port based on model size
            if model_size == "70b":
                base_url = "http://localhost:8083"
            else:
                base_url = "http://localhost:8082"
        
        self.base_url = base_url.rstrip('/')
        self.model_size = model_size
        self.client = httpx.AsyncClient(timeout=120.0)
        
    async def health_check(self) -> bool:
        """Check if NIM generation service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/v1/health/ready")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"NIM Generation health check failed: {e}")
            return False
    
    async def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """Generate chat response using NIM Llama model"""
        try:
            # Select model based on instance configuration
            model_name = f"meta/llama-3.1-{self.model_size}-instruct"
            
            payload = {
                "model": model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                logger.warning("No choices in NIM response")
                return "Sorry, I couldn't generate a response."
                
        except Exception as e:
            logger.error(f"Failed to generate chat response: {e}")
            return f"Error generating response: {str(e)}"
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class NIMService:
    """Combined service for NIM Embeddings and Generation"""
    
    def __init__(
        self,
        embedding_url: str = "http://localhost:8081",
        generation_url: str = "http://localhost:8082"
    ):
        self.embedding_service = NIMEmbeddingService(embedding_url)
        self.generation_service = NIMGenerationService(generation_url)
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of both NIM services"""
        embedding_healthy = await self.embedding_service.health_check()
        generation_healthy = await self.generation_service.health_check()
        
        return {
            "embeddings": embedding_healthy,
            "generation": generation_healthy,
            "overall": embedding_healthy and generation_healthy
        }
    
    async def process_query_with_context(
        self,
        user_query: str,
        context_documents: List[str],
        max_response_tokens: int = 200
    ) -> Dict[str, Any]:
        """
        Full RAG pipeline: embed query, find relevant context, generate response
        """
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.embed_query(user_query)
            
            # For now, we'll use all context (vector search integration comes later)
            # In full implementation, this would use pgvector to find most relevant docs
            
            # Prepare context for generation
            context_text = "\n\n".join(context_documents[:3])  # Limit context
            
            # Format messages for chat completion
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Use the provided context to answer questions accurately. If the context doesn't contain relevant information, say so."
                },
                {
                    "role": "user", 
                    "content": f"Context:\n{context_text}\n\nQuestion: {user_query}"
                }
            ]
            
            # Generate response
            response = await self.generation_service.generate_chat_response(
                messages=messages,
                max_tokens=max_response_tokens,
                temperature=0.7
            )
            
            return {
                "query": user_query,
                "response": response,
                "context_used": len(context_documents),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in process_query_with_context: {e}")
            return {
                "query": user_query,
                "response": f"Sorry, I encountered an error: {str(e)}",
                "context_used": 0,
                "success": False
            }
    
    async def close(self):
        """Close all HTTP clients"""
        await self.embedding_service.close()
        await self.generation_service.close()


# Global NIM service instance
_nim_service: Optional[NIMService] = None

def get_nim_service() -> NIMService:
    """Get global NIM service instance"""
    global _nim_service
    if _nim_service is None:
        _nim_service = NIMService()
    return _nim_service

async def close_nim_service():
    """Close global NIM service"""
    global _nim_service
    if _nim_service is not None:
        await _nim_service.close()
        _nim_service = None