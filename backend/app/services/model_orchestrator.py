"""
Model Orchestrator Service
Manages multi-model lifecycle and intelligent routing

Model Selection Strategy:
1. Llama 70B (Solo Mode): For deep reasoning - runs alone, all other models unloaded
2. Qwen 2.5 32B (Default): Primary model with document/RAG support
3. Mistral Nemo: Quick responses when speed is priority
4. DeepSeek Coder: Code generation in self-aware mode
5. NV-Embedqa: Always runs with Qwen/Mistral/DeepSeek for document/RAG support
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
import psutil
import GPUtil
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import get_settings

class ModelInfo:
    """Model information and status"""
    def __init__(self, name: str, backend: str, purpose: str, memory_gb: float, 
                 max_context: int, endpoint: str, display_name: str = None,
                 description: str = None):
        self.name = name
        self.backend = backend  # 'nim' or 'ollama'
        self.purpose = purpose  # 'chat', 'reasoning', 'coding', 'embeddings'
        self.memory_gb = memory_gb
        self.max_context = max_context
        self.endpoint = endpoint
        self.display_name = display_name or name
        self.description = description or ""
        self.status = "unloaded"
        self.last_used = None
        self.load_time = None
        self.tokens_per_second = 0
        self.current_requests = 0

class ModelOrchestrator:
    """Manages multi-model lifecycle and routing"""
    
    def __init__(self):
        self.settings = get_settings()
        self.models = self._initialize_models()
        self.max_vram_gb = 24
        self.reserved_vram_gb = 1  # Keep 1GB free
        self.mode = "balanced"
        self.active_primary_model = "qwen2.5:32b-instruct-q4_K_M"  # Default
        
    def _initialize_models(self) -> Dict[str, ModelInfo]:
        """Initialize available models configuration"""
        return {
            "llama3.1:70b-instruct-q4_K_M": ModelInfo(
                name="llama3.1:70b-instruct-q4_K_M",
                backend="nim",
                purpose="reasoning",
                memory_gb=22,
                max_context=32768,
                endpoint="http://localhost:8000",
                display_name="Llama 3.1 70B (Deep Reasoning)",
                description="Solo mode - Unloads all other models for maximum reasoning power"
            ),
            "qwen2.5:32b-instruct-q4_K_M": ModelInfo(
                name="qwen2.5:32b-instruct-q4_K_M",
                backend="ollama",
                purpose="reasoning",
                memory_gb=19,
                max_context=32768,
                endpoint="http://localhost:11434",
                display_name="Qwen 2.5 32B (Default)",
                description="Primary model - Advanced reasoning with full document/RAG support"
            ),
            "deepseek-coder-v2:16b-lite-instruct-q4_K_M": ModelInfo(
                name="deepseek-coder-v2:16b-lite-instruct-q4_K_M",
                backend="ollama",
                purpose="coding",
                memory_gb=9,
                max_context=16384,
                endpoint="http://localhost:11434",
                display_name="DeepSeek Coder V2 (Self-Aware Mode)",
                description="Code generation and analysis - Use in self-aware mode"
            ),
            "mistral-nemo:latest": ModelInfo(
                name="mistral-nemo:latest",
                backend="ollama",
                purpose="chat",
                memory_gb=7,
                max_context=128000,
                endpoint="http://localhost:11434",
                display_name="Mistral Nemo (Quick Responses)",
                description="Fast responses - When speed is the priority"
            ),
            "nv-embedqa-e5-v5": ModelInfo(
                name="nv-embedqa-e5-v5",
                backend="nim",
                purpose="embeddings",
                memory_gb=2,
                max_context=512,
                endpoint="http://localhost:8001",
                display_name="NVIDIA Embeddings",
                description="Document processing and RAG - Always active except in Llama 70B mode"
            )
        }
        
    async def get_current_vram_usage(self) -> float:
        """Get current VRAM usage in GB"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                used_memory = gpus[0].memoryUsed / 1024  # Convert MB to GB
                return used_memory
        except:
            pass
        return 0
        
    async def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models"""
        loaded = []
        for name, model in self.models.items():
            if model.status in ["loaded", "loading"]:
                loaded.append(name)
        return loaded
        
    async def calculate_memory_requirement(self, models_to_load: List[str]) -> float:
        """Calculate total memory requirement for a set of models"""
        total = 0
        for model_name in models_to_load:
            if model_name in self.models:
                total += self.models[model_name].memory_gb
        return total
        
    async def ensure_memory_available(self, required_gb: float) -> bool:
        """Ensure enough VRAM is available, unloading models if needed"""
        current_usage = await self.get_current_vram_usage()
        available = self.max_vram_gb - self.reserved_vram_gb - current_usage
        
        if available >= required_gb:
            return True
            
        # Need to free memory
        needed = required_gb - available
        unloaded = await self.smart_unload(needed)
        
        return unloaded >= needed
        
    async def smart_unload(self, needed_gb: float, preserve_embeddings: bool = True) -> float:
        """Intelligently unload models based on usage patterns"""
        freed = 0
        
        # Sort models by last used time (oldest first)
        loaded_models = [
            (name, model) for name, model in self.models.items() 
            if model.status == "loaded"
        ]
        loaded_models.sort(key=lambda x: x[1].last_used or datetime.min)
        
        for name, model in loaded_models:
            if freed >= needed_gb:
                break
                
            # Don't unload embeddings model unless explicitly requested
            if preserve_embeddings and model.purpose == "embeddings":
                continue
                
            # Don't unload models with active requests
            if model.current_requests > 0:
                continue
                
            success = await self.unload_model(name)
            if success:
                freed += model.memory_gb
                
        return freed
        
    async def switch_to_model(self, model_name: str) -> bool:
        """Switch to a specific model configuration"""
        self.active_primary_model = model_name
        
        # Special handling for Llama 70B - solo mode
        if model_name == "llama3.1:70b-instruct-q4_K_M":
            # Unload ALL models including embeddings
            await self.unload_all_models()
            # Load only Llama 70B
            return await self.load_model(model_name)
        else:
            # For all other models, ensure embeddings is loaded
            embeddings_loaded = await self.ensure_embeddings_loaded()
            
            # Unload any other primary models
            for name, model in self.models.items():
                if model.purpose in ["chat", "reasoning", "coding"] and name != model_name:
                    if model.status == "loaded":
                        await self.unload_model(name)
            
            # Load the requested model
            model_loaded = await self.load_model(model_name)
            
            return embeddings_loaded and model_loaded
    
    async def ensure_embeddings_loaded(self) -> bool:
        """Ensure embeddings model is loaded for document/RAG support"""
        embeddings_model = self.models.get("nv-embedqa-e5-v5")
        if embeddings_model and embeddings_model.status != "loaded":
            return await self.load_model("nv-embedqa-e5-v5")
        return True
        
    async def unload_all_models(self) -> bool:
        """Unload all models - used for Llama 70B solo mode"""
        success = True
        for name, model in self.models.items():
            if model.status == "loaded":
                if not await self.unload_model(name):
                    success = False
        return success
        
    async def load_model(self, model_name: str) -> bool:
        """Load a specific model"""
        if model_name not in self.models:
            return False
            
        model = self.models[model_name]
        
        if model.status == "loaded":
            return True
            
        # Check memory availability
        required_memory = model.memory_gb
        if not await self.ensure_memory_available(required_memory):
            return False
            
        model.status = "loading"
        
        try:
            if model.backend == "ollama":
                # Load Ollama model
                response = requests.post(
                    f"{model.endpoint}/api/generate",
                    json={"model": model.name, "prompt": "", "stream": False}
                )
                if response.status_code == 200:
                    model.status = "loaded"
                    model.load_time = datetime.now()
                    return True
            elif model.backend == "nim":
                # NIM models are loaded via Docker - just check if available
                try:
                    response = requests.get(f"{model.endpoint}/v1/health/ready")
                    if response.status_code == 200:
                        model.status = "loaded"
                        model.load_time = datetime.now()
                        return True
                except:
                    pass
                    
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            
        model.status = "unloaded"
        return False
        
    async def unload_model(self, model_name: str) -> bool:
        """Unload a specific model"""
        if model_name not in self.models:
            return False
            
        model = self.models[model_name]
        
        if model.status == "unloaded":
            return True
            
        try:
            if model.backend == "ollama":
                # Unload Ollama model
                # Ollama doesn't have explicit unload, it manages memory automatically
                model.status = "unloaded"
                return True
            elif model.backend == "nim":
                # NIM models can't be dynamically unloaded - they're Docker containers
                # Would need to stop the container which requires orchestration
                print(f"Warning: NIM model {model_name} cannot be dynamically unloaded")
                return False
                
        except Exception as e:
            print(f"Error unloading model {model_name}: {e}")
            
        return False
        
    async def select_model_for_query(self, query: str, context: Dict) -> str:
        """Select the best model for a given query"""
        # If user has manually selected a model, use it
        if context.get("selected_model"):
            return context["selected_model"]
            
        # Use the active primary model
        return self.active_primary_model
        
    async def get_model_status(self) -> Dict:
        """Get comprehensive status of all models"""
        current_vram = await self.get_current_vram_usage()
        
        models_status = {}
        for name, model in self.models.items():
            models_status[name] = {
                "display_name": model.display_name,
                "description": model.description,
                "status": model.status,
                "backend": model.backend,
                "purpose": model.purpose,
                "memory_gb": model.memory_gb,
                "last_used": model.last_used.isoformat() if model.last_used else None,
                "tokens_per_second": model.tokens_per_second,
                "current_requests": model.current_requests
            }
            
        return {
            "models": models_status,
            "system": {
                "total_vram_gb": self.max_vram_gb,
                "used_vram_gb": current_vram,
                "available_vram_gb": self.max_vram_gb - current_vram,
                "mode": self.mode,
                "active_primary_model": self.active_primary_model
            }
        }
        
    async def update_model_stats(self, model_name: str, tokens: int, duration: float):
        """Update model performance statistics"""
        if model_name in self.models:
            model = self.models[model_name]
            model.last_used = datetime.now()
            if duration > 0:
                model.tokens_per_second = tokens / duration
                
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get model information"""
        return self.models.get(model_name)
        
    async def handle_request_start(self, model_name: str):
        """Mark the start of a request to a model"""
        if model_name in self.models:
            self.models[model_name].current_requests += 1
            
    async def handle_request_end(self, model_name: str):
        """Mark the end of a request to a model"""
        if model_name in self.models:
            self.models[model_name].current_requests = max(0, self.models[model_name].current_requests - 1)


# Global orchestrator instance
orchestrator = ModelOrchestrator()