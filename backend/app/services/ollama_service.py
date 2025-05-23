"""
Ollama Service Integration
Provides clean interface to Ollama for local model inference
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
import httpx
import json

logger = logging.getLogger(__name__)

class OllamaService:
    """Service for Ollama local model inference"""
    
    def __init__(self, base_url: str = None):
        # Since you're running everything in Windows, but we're coding in WSL2
        # Always use the Windows IP for Ollama
        if base_url is None:
            base_url = "http://10.1.0.224:11434"
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout for large models
        
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available Ollama models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            result = response.json()
            return result.get("models", [])
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull/download a model"""
        try:
            payload = {"name": model_name}
            
            # Use streaming to handle long download times
            async with self.client.stream(
                'POST', 
                f"{self.base_url}/api/pull",
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        try:
                            status = json.loads(line)
                            logger.info(f"Pull status: {status}")
                        except json.JSONDecodeError:
                            continue
            
            logger.info(f"Successfully pulled model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    async def generate_chat_response(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """Generate chat response using Ollama model"""
        try:
            # Convert messages to Ollama format
            # Ollama uses a simple prompt format, so we'll combine messages
            prompt = self._format_messages_for_ollama(messages)
            
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                }
            }
            
            # Add max tokens if specified
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Failed to generate response with {model_name}: {e}")
            raise
    
    async def generate_chat_completion(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate chat completion using Ollama's chat API (if available)"""
        try:
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            # Try the new chat API first
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result["message"]["content"]
                
            except (httpx.HTTPStatusError, KeyError):
                # Fall back to generate API
                logger.info(f"Chat API not available for {model_name}, using generate API")
                return await self.generate_chat_response(
                    model_name, messages, temperature, max_tokens
                )
            
        except Exception as e:
            logger.error(f"Failed to generate chat completion with {model_name}: {e}")
            raise
    
    def _format_messages_for_ollama(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages for Ollama's generate API"""
        formatted_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                formatted_parts.append(f"System: {content}")
            elif role == "user":
                formatted_parts.append(f"Human: {content}")
            elif role == "assistant":
                formatted_parts.append(f"Assistant: {content}")
        
        # Add final prompt for response
        formatted_parts.append("Assistant:")
        
        return "\n\n".join(formatted_parts)
    
    async def check_model_exists(self, model_name: str) -> bool:
        """Check if a model exists locally"""
        try:
            models = await self.list_models()
            return any(model["name"] == model_name for model in models)
        except Exception:
            return False
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global instance
_ollama_service = None

def get_ollama_service() -> OllamaService:
    """Get global Ollama service instance"""
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
    return _ollama_service