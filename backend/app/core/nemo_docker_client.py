"""
NeMo Docker Client for AI Assistant Backend
Communicates with NeMo container API for real AI inference
"""
import os
import logging
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NeMoConfig:
    """Configuration for NeMo Docker connection"""
    host: str = "localhost"
    port: int = 8889
    timeout: float = 30.0
    max_retries: int = 3
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

class NeMoDockerClient:
    """Client for communicating with NeMo Docker container"""
    
    def __init__(self, config: Optional[NeMoConfig] = None):
        self.config = config or NeMoConfig()
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )
        self.is_available = False
        
    async def check_health(self) -> bool:
        """Check if NeMo container is healthy and responsive"""
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                data = response.json()
                self.is_available = data.get("status") == "healthy"
                logger.info(f"NeMo container health: {data}")
                return self.is_available
            else:
                logger.warning(f"NeMo health check failed: {response.status_code}")
                self.is_available = False
                return False
                
        except Exception as e:
            logger.warning(f"NeMo container not reachable: {e}")
            self.is_available = False
            return False
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded NeMo model"""
        try:
            response = await self.client.get("/model/info")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get model info: {response.status_code}")
                return {"error": "Failed to get model info"}
                
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {"error": str(e)}
    
    async def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        max_length: int = 150,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40
    ) -> Dict[str, Any]:
        """Generate chat response using NeMo model"""
        
        # Check if container is available
        if not await self.check_health():
            raise Exception("NeMo container is not available")
        
        try:
            # Format request for NeMo API
            request_data = {
                "messages": [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in messages
                ],
                "max_length": max_length,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k
            }
            
            logger.info(f"Sending request to NeMo container: {len(messages)} messages")
            
            response = await self.client.post("/chat/generate", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Generated response in {result.get('generation_time', 0):.2f}s")
                return result
            else:
                error_msg = f"NeMo generation failed: {response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global client instance
_nemo_client: Optional[NeMoDockerClient] = None

def get_nemo_client() -> NeMoDockerClient:
    """Get or create NeMo Docker client"""
    global _nemo_client
    
    if _nemo_client is None:
        config = NeMoConfig(
            host=os.getenv("NEMO_HOST", "localhost"),
            port=int(os.getenv("NEMO_PORT", "8889")),
            timeout=float(os.getenv("NEMO_TIMEOUT", "30.0"))
        )
        _nemo_client = NeMoDockerClient(config)
    
    return _nemo_client

async def generate_chat_response_async(
    messages: List[Dict[str, str]],
    max_length: int = 150,
    temperature: float = 0.7,
    **kwargs
) -> str:
    """Async wrapper for generating chat responses with NeMo"""
    client = get_nemo_client()
    
    try:
        result = await client.generate_chat_response(
            messages=messages,
            max_length=max_length,
            temperature=temperature,
            **kwargs
        )
        return result["response"]
        
    except Exception as e:
        logger.error(f"NeMo generation failed: {e}")
        
        # Fallback to informative message
        user_message = messages[-1]["content"] if messages else "Hello"
        return f"NeMo container error: {str(e)}. Message was: '{user_message}'"

def generate_chat_response_sync(
    messages: List[Dict[str, str]],
    max_length: int = 150,
    temperature: float = 0.7,
    **kwargs
) -> str:
    """Synchronous wrapper for generating chat responses with NeMo"""
    try:
        # Run async function in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                generate_chat_response_async(messages, max_length, temperature, **kwargs)
            )
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in sync wrapper: {e}")
        user_message = messages[-1]["content"] if messages else "Hello"
        return f"Error connecting to NeMo: {str(e)}. Your message: '{user_message}'"