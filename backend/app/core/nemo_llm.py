"""
Real NeMo LLM integration for chat functionality.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np

try:
    from nemo.collections.nlp.models import GPTModel
    from nemo.collections.nlp.modules.common.text_generation_utils import (
        generate_candidates, 
        get_computeprob_response
    )
    from nemo.collections.nlp.models.language_modeling.megatron_gpt_model import MegatronGPTModel
    NEMO_AVAILABLE = True
except ImportError:
    NEMO_AVAILABLE = False
    print("NeMo not available, using mock implementation")

logger = logging.getLogger(__name__)

class NeMoLLM:
    """Real NeMo LLM wrapper for chat functionality."""
    
    def __init__(self, model_name: str = "nvidia/nemo-megatron-gpt-20b", device: str = "cuda"):
        """Initialize NeMo LLM.
        
        Args:
            model_name: Name/path of the NeMo model to load
            device: Device to run inference on (cuda/cpu)
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.is_initialized = False
        
        if NEMO_AVAILABLE:
            self._load_model()
        else:
            logger.warning("NeMo not available, using mock responses")
    
    def _load_model(self):
        """Load the NeMo LLM model."""
        try:
            logger.info(f"Loading NeMo model: {self.model_name}")
            
            # For pre-trained NeMo models
            if self.model_name.startswith("nvidia/"):
                # Load from NGC or HuggingFace
                self.model = MegatronGPTModel.from_pretrained(self.model_name)
            else:
                # Load local .nemo file
                self.model = MegatronGPTModel.restore_from(self.model_name)
            
            # Move to appropriate device
            if self.device == "cuda" and self.model.device.type != "cuda":
                self.model = self.model.cuda()
            
            self.is_initialized = True
            logger.info(f"Successfully loaded NeMo model on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load NeMo model: {e}")
            self.is_initialized = False
            raise
    
    def generate(self, 
                prompt: str, 
                max_length: int = 100,
                temperature: float = 0.7,
                top_p: float = 0.9,
                top_k: int = 40) -> str:
        """Generate text response using NeMo LLM.
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Top-p sampling threshold
            top_k: Top-k sampling threshold
            
        Returns:
            Generated text response
        """
        if not NEMO_AVAILABLE or not self.is_initialized:
            return self._mock_generate(prompt, max_length)
        
        try:
            # Prepare generation parameters
            generation_params = {
                "tokens_to_generate": max_length,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "repetition_penalty": 1.1,
                "add_BOS": True,
            }
            
            # Generate response
            with self.model.cuda():
                response = self.model.generate(
                    inputs=[prompt],
                    **generation_params
                )
            
            # Extract generated text (remove input prompt)
            generated_text = response[0]
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return self._mock_generate(prompt, max_length)
    
    def chat_generate(self, 
                     messages: List[Dict[str, str]], 
                     max_length: int = 150,
                     temperature: float = 0.7) -> str:
        """Generate chat response from conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_length: Maximum response length
            temperature: Sampling temperature
            
        Returns:
            Generated chat response
        """
        # Format messages into a prompt
        prompt = self._format_chat_prompt(messages)
        return self.generate(prompt, max_length, temperature)
    
    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages into a prompt string.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"Human: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)
    
    def _mock_generate(self, prompt: str, max_length: int = 100) -> str:
        """Fallback mock generation when NeMo is not available."""
        return f"Mock NeMo response to: {prompt[:50]}... (Generated {max_length} token response)"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "is_initialized": self.is_initialized,
            "nemo_available": NEMO_AVAILABLE,
            "model_type": "NeMo LLM" if NEMO_AVAILABLE else "Mock"
        }

# Global model instance
_nemo_llm = None

def get_nemo_llm(model_name: Optional[str] = None) -> NeMoLLM:
    """Get or create NeMo LLM instance.
    
    Args:
        model_name: Optional model name to load
        
    Returns:
        NeMoLLM instance
    """
    global _nemo_llm
    
    if _nemo_llm is None or (model_name and model_name != _nemo_llm.model_name):
        model_name = model_name or os.getenv("NEMO_MODEL_NAME", "nvidia/nemo-megatron-gpt-20b")
        _nemo_llm = NeMoLLM(model_name)
    
    return _nemo_llm

def generate_chat_response(messages: List[Dict[str, str]], **kwargs) -> str:
    """Generate chat response using NeMo LLM.
    
    Args:
        messages: Chat message history
        **kwargs: Additional generation parameters
        
    Returns:
        Generated response string
    """
    llm = get_nemo_llm()
    return llm.chat_generate(messages, **kwargs)