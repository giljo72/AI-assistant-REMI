"""
Unified LLM Service with Model Orchestration
Routes requests to appropriate model service with intelligent model selection
"""
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import json
import aiohttp

logger = logging.getLogger(__name__)

from .nim_service import get_nim_service, NIMGenerationService
from .ollama_service import get_ollama_service, OllamaService

# Import model orchestrator with error handling
try:
    from .model_orchestrator import orchestrator as model_orchestrator, ModelStatus
except ImportError as e:
    logger.warning(f"Could not import model orchestrator: {e}")
    model_orchestrator = None
    # Define ModelStatus fallback if import fails
    from enum import Enum
    class ModelStatus(Enum):
        UNLOADED = "unloaded"
        LOADING = "loading"
        LOADED = "loaded"
        ERROR = "error"
        UNLOADING = "unloading"

class UnifiedLLMService:
    """Unified service to route requests to different LLM backends with orchestration"""
    
    def __init__(self):
        self.nim_service = get_nim_service()
        self.ollama_service = get_ollama_service()
        self.orchestrator = model_orchestrator
        self.active_model = None
        self.active_model_type = None
    
    async def set_active_model(self, model_name: str, model_type: str):
        """Set the active model for chat completions"""
        self.active_model = model_name
        self.active_model_type = model_type
        logger.info(f"Active model set to: {model_name} ({model_type})")
    
    async def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        model_name: Optional[str] = None,
        model_type: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        context_mode: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate chat response using the appropriate service with model orchestration"""
        
        # Analyze request for intelligent routing
        request_type = "chat"
        complexity = "medium"
        domain = "general"
        
        # Analyze messages for routing hints
        all_content = " ".join([msg.get("content", "") for msg in messages]).lower()
        
        if any(keyword in all_content for keyword in ["code", "function", "class", "debug", "error", "implement", "fix"]):
            request_type = "code_analysis"
            domain = "technical"
        elif any(keyword in all_content for keyword in ["business", "strategy", "market", "revenue", "analysis"]):
            domain = "business"
            complexity = "high" if len(all_content) > 500 else "medium"
        
        # Select model if not specified
        if not model_name:
            if self.orchestrator:
                model_name = await self.orchestrator.select_model(
                    request_type=request_type,
                    complexity=complexity,
                    domain=domain,
                    context_size=len(str(messages))
                )
            else:
                # Default model when orchestrator is not available
                model_name = "qwen2.5:32b-instruct-q4_K_M"
                model_type = "ollama"
            
        if not model_name:
            raise ValueError("No suitable model available")
            
        # Get model info
        model_info = self.orchestrator.models.get(model_name) if self.orchestrator else None
        if not model_info and self.orchestrator:
            # Try to find a similar model
            for name, info in self.orchestrator.models.items():
                if model_name in name or name in model_name:
                    model_name = name
                    model_info = info
                    break
                    
        if not model_info:
            # Fallback when orchestrator is not available
            if not self.orchestrator:
                # Use default Ollama backend
                logger.warning(f"Model orchestrator not available, using default Ollama backend for {model_name}")
                async for chunk in self._generate_ollama_stream(
                    model_name, messages, temperature, max_tokens, None
                ):
                    yield chunk
                return
            else:
                raise ValueError(f"Model {model_name} not found")
            
        # Switch to the requested model if it's not already loaded
        if self.orchestrator:
            model_status = self.orchestrator.models.get(model_name)
            if model_status and model_status.status != ModelStatus.LOADED:
                logger.info(f"Switching to model: {model_name}")
                # Use asyncio to call async method
                switch_success = await self.orchestrator.switch_to_model(model_name)
                if not switch_success:
                    logger.warning(f"Failed to switch to model {model_name}, using current model")
            self.orchestrator.mark_model_used(model_name)
        
        try:
            # Route to appropriate backend
            if model_info.backend == "ollama":
                async for chunk in self._generate_ollama_stream(
                    model_name, messages, temperature, max_tokens, model_info.endpoint
                ):
                    yield chunk
            elif model_info.backend == "nim":
                async for chunk in self._generate_nim_stream(
                    model_name, messages, temperature, max_tokens, model_info.endpoint
                ):
                    yield chunk
            else:
                raise ValueError(f"Unsupported backend: {model_info.backend}")
                
        finally:
            # Release model
            if self.orchestrator:
                self.orchestrator.release_model(model_name)
    
    async def _generate_ollama_stream(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        endpoint: str
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using Ollama"""
        
        # Check if model exists
        if not await self.ollama_service.check_model_exists(model_name):
            logger.info(f"Model {model_name} not found locally")
            yield f"Error: Model {model_name} not found. Please install it first."
            return
            
        async with aiohttp.ClientSession() as session:
            data = {
                "model": model_name,
                "messages": messages,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens or 4096
                },
                "stream": True
            }
            
            async with session.post(f"{endpoint}/api/chat", json=data) as response:
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "message" in chunk and "content" in chunk["message"]:
                                yield chunk["message"]["content"]
                        except json.JSONDecodeError:
                            continue
    
    async def _generate_nim_stream(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        endpoint: str
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using NVIDIA NIM"""
        
        # Use 8B NIM service (70B not supported on single RTX 4090)
        nim_service = NIMGenerationService(model_size="8b")
        
        async for chunk in nim_service.generate_chat_response_stream(
            messages=messages,
            max_tokens=max_tokens or 4096,
            temperature=temperature
        ):
            yield chunk
            
        await nim_service.close()
    
    async def health_check(self, model_type: str) -> bool:
        """Check health of specific model service"""
        if model_type == "nvidia-nim":
            return await self.nim_service.health_check()
        elif model_type == "ollama":
            return await self.ollama_service.health_check()
        else:
            return True
    
    async def list_available_models(self, model_type: str) -> List[Dict[str, Any]]:
        """List available models for a specific service"""
        if model_type == "ollama":
            return await self.ollama_service.list_models()
        else:
            return []
    
    async def get_model_status(self) -> List[Dict[str, Any]]:
        """Get status of all models from orchestrator"""
        if self.orchestrator:
            return await self.orchestrator.get_model_status()
        else:
            return []
    
    async def switch_mode(self, mode: str) -> Dict[str, bool]:
        """Switch operational mode"""
        if self.orchestrator:
            return await self.orchestrator.switch_mode(mode)
        else:
            return {"success": False, "error": "orchestrator not available"}
    
    async def close(self):
        """Close all service connections"""
        await self.nim_service.close()
        await self.ollama_service.close()


# Global instance
_llm_service = None

def get_llm_service() -> UnifiedLLMService:
    """Get global unified LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = UnifiedLLMService()
    return _llm_service