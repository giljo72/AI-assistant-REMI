"""
Unified LLM Service
Routes requests to appropriate model service (NIM, Ollama, Transformers, NeMo)
"""
import logging
from typing import List, Dict, Any, Optional
from .nim_service import get_nim_service, NIMGenerationService
from .ollama_service import get_ollama_service, OllamaService

logger = logging.getLogger(__name__)

class UnifiedLLMService:
    """Unified service to route requests to different LLM backends"""
    
    def __init__(self):
        self.nim_service = get_nim_service()
        self.ollama_service = get_ollama_service()
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
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate chat response using the appropriate service"""
        
        # Use provided model or fall back to active model
        target_model = model_name or self.active_model
        target_type = model_type or self.active_model_type
        
        if not target_model or not target_type:
            raise ValueError("No model specified and no active model set")
        
        try:
            if target_type == "nvidia-nim":
                return await self._generate_nim_response(
                    target_model, messages, temperature, max_tokens
                )
            elif target_type == "ollama":
                return await self._generate_ollama_response(
                    target_model, messages, temperature, max_tokens
                )
            elif target_type == "transformers":
                return await self._generate_transformers_response(
                    target_model, messages, temperature, max_tokens
                )
            elif target_type == "nemo":
                return await self._generate_nemo_response(
                    target_model, messages, temperature, max_tokens
                )
            else:
                raise ValueError(f"Unsupported model type: {target_type}")
                
        except Exception as e:
            logger.error(f"Error generating response with {target_model} ({target_type}): {e}")
            raise
    
    async def _generate_nim_response(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """Generate response using NVIDIA NIM"""
        
        # Determine which NIM service to use based on model
        if "70b" in model_name.lower():
            nim_service = NIMGenerationService(model_size="70b")
        else:
            nim_service = NIMGenerationService(model_size="8b")
        
        response = await nim_service.generate_chat_response(
            messages=messages,
            max_tokens=max_tokens or 150,
            temperature=temperature
        )
        
        await nim_service.close()
        return response
    
    async def _generate_ollama_response(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """Generate response using Ollama"""
        
        # Check if model exists, if not try to pull it
        if not await self.ollama_service.check_model_exists(model_name):
            logger.info(f"Model {model_name} not found, attempting to pull...")
            await self.ollama_service.pull_model(model_name)
        
        return await self.ollama_service.generate_chat_completion(
            model_name=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    async def _generate_transformers_response(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """Generate response using Transformers (local models)"""
        # Import here to avoid circular imports
        from ..core.transformers_llm import TransformersLLM
        
        llm = TransformersLLM(model_name=model_name)
        
        # Convert messages to single prompt for transformers
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        response = await llm.generate_response(
            prompt=prompt,
            max_length=max_tokens or 150,
            temperature=temperature
        )
        
        return response
    
    async def _generate_nemo_response(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """Generate response using NeMo"""
        # Import here to avoid circular imports
        from ..core.nemo_llm import NeMoLLM
        
        llm = NeMoLLM(model_name=model_name)
        
        # Convert messages to single prompt for NeMo
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        response = await llm.generate_response(
            prompt=prompt,
            max_length=max_tokens or 150,
            temperature=temperature
        )
        
        return response
    
    async def health_check(self, model_type: str) -> bool:
        """Check health of specific model service"""
        if model_type == "nvidia-nim":
            return await self.nim_service.health_check()
        elif model_type == "ollama":
            return await self.ollama_service.health_check()
        else:
            return True  # Assume local models are always available
    
    async def list_available_models(self, model_type: str) -> List[Dict[str, Any]]:
        """List available models for a specific service"""
        if model_type == "ollama":
            return await self.ollama_service.list_models()
        else:
            return []  # Other services don't have dynamic model lists
    
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