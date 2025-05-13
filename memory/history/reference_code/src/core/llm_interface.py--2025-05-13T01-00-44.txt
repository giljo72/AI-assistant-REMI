# src/core/llm_interface.py
import os
import requests
import json
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone

from .config import get_settings

logger = logging.getLogger(__name__)

class OllamaInterface:
    """Interface for Ollama LLM API"""
    
    def __init__(self, host: str = None, port: str = None, model: str = None):
        """Initialize Ollama interface"""
        settings = get_settings()
        ollama_settings = settings.get('ollama', {})
        
        self.host = host or ollama_settings.get('host', 'localhost')
        self.port = port or ollama_settings.get('port', '11434')
        self.model = model or ollama_settings.get('model', 'llama3:8b')
        self.base_url = f"http://{self.host}:{self.port}"
        
    def generate(self, 
                prompt: str, 
                context: Optional[List[str]] = None,
                system_prompt: Optional[str] = None,
                temperature: float = 0.7,
                max_tokens: int = 1000) -> str:
        """Generate a response from the LLM"""
        url = f"{self.base_url}/api/generate"
        
        # Add current date and time information to the system prompt
        current_date = datetime.now(timezone.utc)
        date_string = current_date.strftime("%A, %B %d, %Y")
        
        # Modify or create system prompt with date information
        if system_prompt:
            date_aware_system_prompt = f"{system_prompt}\n\nCurrent date: {date_string}."
        else:
            date_aware_system_prompt = f"You are a helpful AI assistant. Current date: {date_string}."
        
        # Ensure payload matches the Ollama API requirements
        payload = {
            "model": self.model,
            "prompt": prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": 8192,
                "num_gpu_layers": 99,  # Load all layers on GPU
                "batch_size": 512,     # Larger batch for 4090
                "num_thread": 16,      # Good for the 4090's capabilities
                "rope_frequency_base": 10000,
                "use_mmap": True,
                "use_mlock": True,
                "main_gpu": 0,
                "split_mode": "layer",
                "tensor_split": None
            }
        }
        
        if date_aware_system_prompt:
            payload["system"] = date_aware_system_prompt
            
        # Do not include context if provided, as it's causing issues
        # If context history is important, we can combine it into the prompt
        if context:
            # Just log that we're ignoring it for now
            logger.info(f"Context provided but being ignored due to API limitations: {len(context)} messages")
        
        try:
            logger.info(f"Sending request to Ollama API: {json.dumps(payload)[:200]}...")
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            # Parse the streaming response
            result = ""
            for line in response.iter_lines():
                if line:
                    try:
                        json_line = json.loads(line)
                        if 'response' in json_line:
                            result += json_line['response']
                        
                        # Check if done
                        if json_line.get('done', False):
                            break
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse Ollama response line: {line}")
            
            return result
        except requests.exceptions.RequestException as e:
            error_msg = f"Error generating from Ollama: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" Response: {e.response.text}"
            logger.error(error_msg)
            return f"Error: Unable to generate response from Ollama. Please check if Ollama is running with the model {self.model}."
        except Exception as e:
            logger.error(f"Unexpected error in Ollama generation: {e}")
            return f"Error: Unexpected issue while generating response. Please try again later."
        
    def check_model(self) -> bool:
        """Check if the specified model is available in Ollama"""
        url = f"{self.base_url}/api/tags"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            return self.model in model_names
        except Exception as e:
            logger.error(f"Error checking Ollama models: {e}")
            return False