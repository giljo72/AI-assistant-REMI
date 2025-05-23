"""
Windows-compatible LLM integration using Transformers library.
This replaces NeMo for Windows compatibility.
"""
import os
import logging
from typing import List, Dict, Any, Optional
import torch

try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        GenerationConfig,
        pipeline
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Transformers not available, using mock implementation")

logger = logging.getLogger(__name__)

class TransformersLLM:
    """Windows-compatible LLM wrapper using Transformers."""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-large", device: str = "auto"):
        """Initialize Transformers LLM.
        
        Args:
            model_name: Name of the model to load from HuggingFace
            device: Device to run inference on (auto/cuda/cpu)
        """
        self.model_name = model_name
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.is_initialized = False
        
        # For chat models, we'll use pipeline
        self.chat_pipeline = None
        
        if TRANSFORMERS_AVAILABLE:
            self._load_model()
        else:
            logger.warning("Transformers not available, using mock responses")
    
    def _load_model(self):
        """Load the Transformers model."""
        try:
            logger.info(f"Loading Transformers model: {self.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map=self.device if self.device == "cuda" else None
            )
            
            if self.device == "cpu":
                self.model = self.model.to("cpu")
            
            # Create text generation pipeline
            self.chat_pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            self.is_initialized = True
            logger.info(f"Successfully loaded Transformers model on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load Transformers model: {e}")
            self.is_initialized = False
            # Don't raise - fall back to mock
    
    def generate(self, 
                prompt: str, 
                max_length: int = 4096,
                temperature: float = 0.7,
                top_p: float = 0.9,
                top_k: int = 40) -> str:
        """Generate text response using Transformers LLM.
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Top-p sampling threshold
            top_k: Top-k sampling threshold
            
        Returns:
            Generated text response
        """
        if not TRANSFORMERS_AVAILABLE or not self.is_initialized or not self.chat_pipeline:
            return self._mock_generate(prompt, max_length)
        
        try:
            # Generate response
            generation_config = {
                "max_new_tokens": max_length,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "do_sample": True,
                "repetition_penalty": 1.1,
                "return_full_text": False,
                "pad_token_id": self.tokenizer.eos_token_id
            }
            
            result = self.chat_pipeline(
                prompt,
                **generation_config
            )
            
            # Extract generated text
            generated_text = result[0]["generated_text"]
            
            # Clean up the response
            generated_text = generated_text.strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return self._mock_generate(prompt, max_length)
    
    def chat_generate(self, 
                     messages: List[Dict[str, str]], 
                     max_length: int = 4096,
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
        
        # Add a system message for better responses
        prompt_parts.append("You are a helpful AI assistant. Provide helpful, accurate, and concise responses.")
        prompt_parts.append("")
        
        for message in messages[-10:]:  # Use last 10 messages for context
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
    
    def _mock_generate(self, prompt: str, max_length: int = 4096) -> str:
        """Fallback mock generation when Transformers is not available."""
        return f"Mock Transformers response to: {prompt[:50]}... (Generated {max_length} token response)"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "is_initialized": self.is_initialized,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "model_type": "Transformers LLM" if TRANSFORMERS_AVAILABLE else "Mock",
            "cuda_available": torch.cuda.is_available() if TRANSFORMERS_AVAILABLE else False
        }

# Global model instance
_transformers_llm = None

def get_transformers_llm(model_name: Optional[str] = None) -> TransformersLLM:
    """Get or create Transformers LLM instance.
    
    Args:
        model_name: Optional model name to load
        
    Returns:
        TransformersLLM instance
    """
    global _transformers_llm
    
    if _transformers_llm is None or (model_name and model_name != _transformers_llm.model_name):
        # Default to a good chat model
        model_name = model_name or os.getenv("TRANSFORMERS_MODEL_NAME", "microsoft/DialoGPT-large")
        _transformers_llm = TransformersLLM(model_name)
    
    return _transformers_llm

def generate_chat_response(messages: List[Dict[str, str]], **kwargs) -> str:
    """Generate chat response using Transformers LLM.
    
    Args:
        messages: Chat message history
        **kwargs: Additional generation parameters
        
    Returns:
        Generated response string
    """
    llm = get_transformers_llm()
    return llm.chat_generate(messages, **kwargs)