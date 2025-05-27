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
from datetime import datetime, timedelta
import requests
from enum import Enum

# Import these conditionally to avoid startup failures
try:
    import psutil
except ImportError:
    print("Warning: psutil not available - system monitoring disabled")
    psutil = None

try:
    import GPUtil
except ImportError:
    print("Warning: GPUtil not available - GPU monitoring disabled")
    GPUtil = None

from sqlalchemy.orm import Session

# Import config with error handling
try:
    from app.core.config import get_settings
except ImportError:
    print("Warning: Could not import config - using defaults")
    class MockSettings:
        def __init__(self):
            self.OLLAMA_BASE_URL = "http://localhost:11434"
            self.NIM_GENERATION_URL = "http://localhost:8001"
            self.NIM_EMBEDDINGS_URL = "http://localhost:8002"
    def get_settings():
        return MockSettings()

from app.db.database import get_db

class ModelStatus(Enum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    UNLOADING = "unloading"

class OperationalMode(Enum):
    BUSINESS_DEEP = "business_deep"    # Llama 70B solo
    BUSINESS_FAST = "business_fast"    # Qwen 32B + embeddings
    DEVELOPMENT = "development"        # DeepSeek + embeddings
    QUICK = "quick"                   # Mistral + embeddings
    BALANCED = "balanced"             # Smart selection based on query

class ModelInfo:
    """Model information and status"""
    def __init__(self, name: str, backend: str, purpose: str, memory_gb: float, 
                 max_context: int, endpoint: str, display_name: str = None,
                 description: str = None, response_time_estimates: Dict = None):
        self.name = name
        self.backend = backend  # 'nim' or 'ollama'
        self.purpose = purpose  # 'chat', 'reasoning', 'coding', 'embeddings'
        self.memory_gb = memory_gb
        self.max_context = max_context
        self.endpoint = endpoint
        self.display_name = display_name or name
        self.description = description or ""
        self.response_time_estimates = response_time_estimates or {}
        self.status = ModelStatus.UNLOADED
        self.last_used = None
        self.load_time = None
        self.tokens_per_second = 0
        self.current_requests = 0
        self.total_tokens_generated = 0
        self.average_response_time = 0
        self.error_message = None

class ModelOrchestrator:
    """Manages multi-model lifecycle and routing"""
    
    def __init__(self):
        self.settings = get_settings()
        self.models = self._initialize_models()
        self.max_vram_gb = 24
        self.reserved_vram_gb = 1  # Keep 1GB free
        self.mode = OperationalMode.BALANCED
        self.active_primary_model = "qwen2.5:32b-instruct-q4_K_M"  # Default
        self._cached_vram_usage = 0
        self._last_vram_update = time.time()
        self.mode_configs = {
            OperationalMode.BUSINESS_DEEP: ["llama3.1:70b-instruct-q4_K_M"],
            OperationalMode.BUSINESS_FAST: ["qwen2.5:32b-instruct-q4_K_M", "nv-embedqa-e5-v5"],
            OperationalMode.DEVELOPMENT: ["deepseek-coder-v2:16b-lite-instruct-q4_K_M", "nv-embedqa-e5-v5"],
            OperationalMode.QUICK: ["mistral-nemo:latest", "nv-embedqa-e5-v5"],
            OperationalMode.BALANCED: ["qwen2.5:32b-instruct-q4_K_M", "nv-embedqa-e5-v5"]
        }
        self._status_update_callbacks = []
        
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
                description="Solo mode - Unloads all other models for maximum reasoning power",
                response_time_estimates={
                    "simple": "6-12 seconds",
                    "analysis": "40-70 seconds",
                    "complex": "60-120 seconds"
                }
            ),
            "qwen2.5:32b-instruct-q4_K_M": ModelInfo(
                name="qwen2.5:32b-instruct-q4_K_M",
                backend="ollama",
                purpose="reasoning",
                memory_gb=19,
                max_context=32768,
                endpoint="http://localhost:11434",
                display_name="Qwen 2.5 32B (Default)",
                description="Primary model - Advanced reasoning with full document/RAG support",
                response_time_estimates={
                    "simple": "4-8 seconds",
                    "analysis": "20-35 seconds",
                    "complex": "30-60 seconds"
                }
            ),
            "deepseek-coder-v2:16b-lite-instruct-q4_K_M": ModelInfo(
                name="deepseek-coder-v2:16b-lite-instruct-q4_K_M",
                backend="ollama",
                purpose="coding",
                memory_gb=9,
                max_context=16384,
                endpoint="http://localhost:11434",
                display_name="DeepSeek Coder V2 (Self-Aware Mode)",
                description="Code generation and analysis - Use in self-aware mode",
                response_time_estimates={
                    "simple": "3-6 seconds",
                    "analysis": "15-30 seconds",
                    "complex": "25-45 seconds"
                }
            ),
            "mistral-nemo:latest": ModelInfo(
                name="mistral-nemo:latest",
                backend="ollama",
                purpose="chat",
                memory_gb=7,
                max_context=128000,
                endpoint="http://localhost:11434",
                display_name="Mistral Nemo (Quick Responses)",
                description="Fast responses - When speed is the priority",
                response_time_estimates={
                    "simple": "2-4 seconds",
                    "analysis": "10-20 seconds",
                    "complex": "15-30 seconds"
                }
            ),
            "nv-embedqa-e5-v5": ModelInfo(
                name="nv-embedqa-e5-v5",
                backend="nim",
                purpose="embeddings",
                memory_gb=2,
                max_context=512,
                endpoint="http://localhost:8001",
                display_name="NVIDIA Embeddings",
                description="Document processing and RAG - Always active except in Llama 70B mode",
                response_time_estimates={
                    "embedding": "10-100ms per chunk",
                    "search": "10-100ms per query"
                }
            )
        }
        
    def register_status_callback(self, callback):
        """Register a callback for status updates"""
        self._status_update_callbacks.append(callback)
        
    async def _notify_status_change(self):
        """Notify all registered callbacks of status changes"""
        status = await self.get_model_status()
        for callback in self._status_update_callbacks:
            try:
                await callback(status)
            except Exception as e:
                print(f"Error in status callback: {e}")
        
    async def get_current_vram_usage(self) -> float:
        """Get current VRAM usage in GB"""
        # Check if we should update the cache (every 5 seconds)
        current_time = time.time()
        if current_time - self._last_vram_update > 5:
            if GPUtil is None:
                self._cached_vram_usage = 0
            else:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        self._cached_vram_usage = gpus[0].memoryUsed / 1024  # Convert MB to GB
                    else:
                        self._cached_vram_usage = 0
                except:
                    self._cached_vram_usage = 0
            self._last_vram_update = current_time
        
        return self._cached_vram_usage
        
    async def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models"""
        loaded = []
        for name, model in self.models.items():
            if model.status in [ModelStatus.LOADED, ModelStatus.LOADING]:
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
        
        # Get loaded models sorted by priority (least recently used first)
        loaded_models = []
        for name, model in self.models.items():
            if model.status == ModelStatus.LOADED:
                # Calculate priority score (lower = unload first)
                priority = 0
                
                # Embeddings get high priority if preserved
                if preserve_embeddings and model.purpose == "embeddings":
                    priority += 1000
                    
                # Active requests get highest priority
                if model.current_requests > 0:
                    priority += 500
                    
                # Recent usage adds priority
                if model.last_used:
                    minutes_ago = (datetime.now() - model.last_used).total_seconds() / 60
                    priority += max(0, 100 - minutes_ago)  # More recent = higher priority
                    
                loaded_models.append((name, model, priority))
                
        # Sort by priority (ascending - lowest priority first)
        loaded_models.sort(key=lambda x: x[2])
        
        # Unload models until we have enough memory
        for name, model, priority in loaded_models:
            if freed >= needed_gb:
                break
                
            # Skip high priority models unless we really need the memory
            if priority > 100 and freed + model.memory_gb < needed_gb:
                continue
                
            success = await self.unload_model(name)
            if success:
                freed += model.memory_gb
                print(f"Unloaded {name} to free {model.memory_gb}GB (priority: {priority})")
                
        return freed
        
    async def switch_mode(self, mode: OperationalMode) -> bool:
        """Switch to a specific operational mode"""
        self.mode = mode
        target_models = self.mode_configs.get(mode, self.mode_configs[OperationalMode.BALANCED])
        
        print(f"Switching to {mode.value} mode with models: {target_models}")
        
        # Calculate total memory needed
        total_needed = await self.calculate_memory_requirement(target_models)
        current_usage = await self.get_current_vram_usage()
        
        # If switching to business_deep (Llama 70B), unload everything first
        if mode == OperationalMode.BUSINESS_DEEP:
            await self.unload_all_models()
            
        # Load the target models
        success = True
        for model_name in target_models:
            if not await self.load_model(model_name):
                success = False
                
        await self._notify_status_change()
        return success
        
    async def switch_to_model(self, model_name: str) -> bool:
        """Switch to a specific model configuration"""
        self.active_primary_model = model_name
        
        # Special handling for Llama 70B - solo mode
        if model_name == "llama3.1:70b-instruct-q4_K_M":
            return await self.switch_mode(OperationalMode.BUSINESS_DEEP)
        else:
            # For all other models, ensure embeddings is loaded
            embeddings_loaded = await self.ensure_embeddings_loaded()
            
            # Check memory before loading
            model = self.models.get(model_name)
            if model:
                # Smart unload to make room
                current_usage = await self.get_current_vram_usage()
                embeddings_memory = 2 if embeddings_loaded else 0
                available = self.max_vram_gb - self.reserved_vram_gb - current_usage
                
                if available < model.memory_gb:
                    # Need to unload something
                    needed = model.memory_gb - available
                    await self.smart_unload(needed, preserve_embeddings=True)
            
            # Load the requested model
            model_loaded = await self.load_model(model_name)
            
            await self._notify_status_change()
            return embeddings_loaded and model_loaded
    
    async def ensure_embeddings_loaded(self) -> bool:
        """Ensure embeddings model is loaded for document/RAG support"""
        embeddings_model = self.models.get("nv-embedqa-e5-v5")
        if embeddings_model and embeddings_model.status != ModelStatus.LOADED:
            return await self.load_model("nv-embedqa-e5-v5")
        return True
        
    async def unload_all_models(self) -> bool:
        """Unload all models - used for Llama 70B solo mode"""
        success = True
        for name, model in self.models.items():
            if model.status == ModelStatus.LOADED:
                if not await self.unload_model(name):
                    success = False
        return success
        
    async def load_model(self, model_name: str) -> bool:
        """Load a specific model"""
        if model_name not in self.models:
            return False
            
        model = self.models[model_name]
        
        if model.status == ModelStatus.LOADED:
            return True
            
        # Check memory availability
        required_memory = model.memory_gb
        if not await self.ensure_memory_available(required_memory):
            model.status = ModelStatus.ERROR
            model.error_message = "Insufficient VRAM available"
            await self._notify_status_change()
            return False
            
        model.status = ModelStatus.LOADING
        model.error_message = None
        await self._notify_status_change()
        
        try:
            if model.backend == "ollama":
                # For Ollama, first check if model exists
                try:
                    # Check if model is available
                    tags_response = requests.get(f"{model.endpoint}/api/tags", timeout=5)
                    if tags_response.status_code == 200:
                        available_models = [m["name"] for m in tags_response.json().get("models", [])]
                        if model.name not in available_models:
                            model.error_message = f"Model {model.name} not found in Ollama"
                            model.status = ModelStatus.ERROR
                            await self._notify_status_change()
                            return False
                    
                    # Model exists, now "load" it by making a minimal request
                    # This ensures it's loaded into memory
                    response = requests.post(
                        f"{model.endpoint}/api/generate",
                        json={
                            "model": model.name, 
                            "prompt": "Hello",
                            "stream": False,
                            "options": {"num_predict": 1}  # Generate only 1 token to minimize time
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        model.status = ModelStatus.LOADED
                        model.load_time = datetime.now()
                        model.last_used = datetime.now()
                        await self._notify_status_change()
                        return True
                    else:
                        model.error_message = f"Failed to load model: HTTP {response.status_code}"
                        return False
                except requests.exceptions.Timeout:
                    model.error_message = "Timeout loading model - model may be very large"
                    return False
                except Exception as e:
                    model.error_message = f"Error loading model: {str(e)}"
                    return False
            elif model.backend == "nim":
                # NIM models are loaded via Docker - just check if available
                try:
                    response = requests.get(f"{model.endpoint}/v1/health/ready", timeout=5)
                    if response.status_code == 200:
                        model.status = ModelStatus.LOADED
                        model.load_time = datetime.now()
                        model.last_used = datetime.now()
                        await self._notify_status_change()
                        return True
                except:
                    pass
                    
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            model.error_message = str(e)
            
        model.status = ModelStatus.ERROR if model.error_message else ModelStatus.UNLOADED
        await self._notify_status_change()
        return False
        
    async def unload_model(self, model_name: str) -> bool:
        """Unload a specific model"""
        if model_name not in self.models:
            return False
            
        model = self.models[model_name]
        
        if model.status == ModelStatus.UNLOADED:
            return True
            
        model.status = ModelStatus.UNLOADING
        await self._notify_status_change()
        
        try:
            if model.backend == "ollama":
                # Stop the Ollama model to free memory
                try:
                    # Use subprocess to stop the model
                    import subprocess
                    result = subprocess.run(
                        ['ollama', 'stop', model.name],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    model.status = ModelStatus.UNLOADED
                    model.load_time = None
                    await self._notify_status_change()
                    return True
                except Exception as e:
                    print(f"Error stopping Ollama model: {e}")
                    # Even if stop fails, mark as unloaded
                    model.status = ModelStatus.UNLOADED
                    await self._notify_status_change()
                    return True
            elif model.backend == "nim":
                # NIM models can't be dynamically unloaded - they're Docker containers
                # Would need to stop the container which requires orchestration
                print(f"Warning: NIM model {model_name} cannot be dynamically unloaded")
                return False
                
        except Exception as e:
            print(f"Error unloading model {model_name}: {e}")
            model.error_message = str(e)
            
        return False
        
    async def select_model_for_query(self, query: str, context: Dict) -> str:
        """Select the best model for a given query"""
        # If user has manually selected a model, use it
        if context.get("selected_model"):
            return context["selected_model"]
            
        # In balanced mode, analyze query to select best model
        if self.mode == OperationalMode.BALANCED:
            query_lower = query.lower()
            
            # Code-related queries go to DeepSeek
            code_keywords = ['code', 'function', 'class', 'debug', 'error', 'implement', 
                           'python', 'javascript', 'programming', 'syntax']
            if any(keyword in query_lower for keyword in code_keywords):
                if await self.load_model("deepseek-coder-v2:16b-lite-instruct-q4_K_M"):
                    return "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
                    
            # Quick queries go to Mistral
            if len(query) < 100 and '?' in query:
                if await self.load_model("mistral-nemo:latest"):
                    return "mistral-nemo:latest"
                    
            # Complex analysis goes to active primary model
            analysis_keywords = ['analyze', 'explain', 'compare', 'evaluate', 'assess',
                               'strategy', 'business', 'plan', 'decision']
            if any(keyword in query_lower for keyword in analysis_keywords):
                return self.active_primary_model
                
        # Use the active primary model
        return self.active_primary_model
        
    def estimate_response_time(self, model_name: str, query_length: int) -> Dict[str, str]:
        """Estimate response time based on model and query complexity"""
        model = self.models.get(model_name)
        if not model:
            return {"estimate": "Unknown", "confidence": "low"}
            
        # Classify query complexity
        if query_length < 50:
            complexity = "simple"
        elif query_length < 200:
            complexity = "analysis"
        else:
            complexity = "complex"
            
        estimate = model.response_time_estimates.get(complexity, "10-30 seconds")
        
        # Adjust based on current system load
        current_requests = sum(m.current_requests for m in self.models.values())
        if current_requests > 2:
            # Add 50% to estimate if system is busy
            parts = estimate.split('-')
            if len(parts) == 2:
                try:
                    low = int(parts[0])
                    high = int(parts[1].split()[0])
                    estimate = f"{int(low * 1.5)}-{int(high * 1.5)} seconds"
                except:
                    pass
                    
        return {
            "estimate": estimate,
            "complexity": complexity,
            "confidence": "high" if model.tokens_per_second > 0 else "medium"
        }
        
    async def get_model_status(self) -> Dict:
        """Get comprehensive status of all models"""
        # Use cached VRAM reading if available (updated every 5 seconds)
        current_vram = self._cached_vram_usage if hasattr(self, '_cached_vram_usage') else await self.get_current_vram_usage()
        
        models_status = {}
        for name, model in self.models.items():
            # Determine status color
            if model.status == ModelStatus.LOADED:
                if model.backend == "nim":
                    status_color = "green"  # NVIDIA NIM = green
                else:
                    status_color = "blue"   # Ollama = blue
            elif model.status == ModelStatus.LOADING:
                status_color = "yellow"
            elif model.status == ModelStatus.ERROR:
                status_color = "red"
            else:
                status_color = "gray"
                
            models_status[name] = {
                "display_name": model.display_name,
                "description": model.description,
                "status": model.status.value,
                "status_color": status_color,
                "backend": model.backend,
                "purpose": model.purpose,
                "memory_gb": model.memory_gb,
                "last_used": model.last_used.isoformat() if model.last_used else None,
                "is_active": model.status == ModelStatus.LOADED and (
                    model.last_used and (datetime.now() - model.last_used).seconds < 300
                ),
                "tokens_per_second": model.tokens_per_second,
                "current_requests": model.current_requests,
                "total_tokens": model.total_tokens_generated,
                "average_response_time": model.average_response_time,
                "error_message": model.error_message
            }
            
        return {
            "models": models_status,
            "system": {
                "total_vram_gb": self.max_vram_gb,
                "used_vram_gb": current_vram,
                "available_vram_gb": self.max_vram_gb - current_vram,
                "reserved_vram_gb": self.reserved_vram_gb,
                "mode": self.mode.value,
                "active_primary_model": self.active_primary_model,
                "total_requests_active": sum(m.current_requests for m in self.models.values())
            }
        }
    
    async def get_quick_model_status(self) -> Dict:
        """Get minimal model status for quick checks (used by frontend)"""
        # Get current VRAM usage
        current_vram = await self.get_current_vram_usage()
        
        # Get GPU info
        gpu_name = "RTX 4090"  # Default
        gpu_utilization = 0
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_name = gpu.name
                gpu_utilization = gpu.load * 100
        except:
            pass
        
        # Get loaded models info
        models_info = {}
        active_primary = None
        
        for name, model in self.models.items():
            if model.status == ModelStatus.LOADED:
                models_info[name] = {
                    "display_name": model.display_name,
                    "status": model.status.value,
                    "status_color": "green" if model.backend == "nim" else "blue",
                    "tokens_per_second": model.tokens_per_second,
                    "memory_gb": model.memory_gb
                }
                if model.purpose != "embeddings" and active_primary is None:
                    active_primary = name
        
        return {
            "models": models_info,
            "system": {
                "total_vram_gb": self.max_vram_gb,
                "used_vram_gb": current_vram,
                "available_vram_gb": self.max_vram_gb - current_vram,
                "active_primary_model": active_primary,
                "total_requests_active": sum(m.current_requests for m in self.models.values()),
                "gpu_utilization": gpu_utilization,
                "gpu_name": gpu_name
            }
        }
        
    async def update_model_stats(self, model_name: str, tokens: int, duration: float):
        """Update model performance statistics"""
        if model_name in self.models:
            model = self.models[model_name]
            model.last_used = datetime.now()
            model.total_tokens_generated += tokens
            
            if duration > 0:
                model.tokens_per_second = tokens / duration
                
                # Update average response time
                if model.average_response_time == 0:
                    model.average_response_time = duration
                else:
                    # Exponential moving average
                    model.average_response_time = 0.9 * model.average_response_time + 0.1 * duration
                    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get model information"""
        return self.models.get(model_name)
        
    async def handle_request_start(self, model_name: str):
        """Mark the start of a request to a model"""
        if model_name in self.models:
            self.models[model_name].current_requests += 1
            await self._notify_status_change()
            
    async def handle_request_end(self, model_name: str):
        """Mark the end of a request to a model"""
        if model_name in self.models:
            self.models[model_name].current_requests = max(0, self.models[model_name].current_requests - 1)
            await self._notify_status_change()
    
    def mark_model_used(self, model_name: str):
        """Mark a model as being used (synchronous version for compatibility)"""
        if model_name in self.models:
            model = self.models[model_name]
            model.last_used = datetime.now()
            model.current_requests += 1
            # Fire and forget the async notification
            asyncio.create_task(self._notify_status_change())
    
    def release_model(self, model_name: str):
        """Release a model after use (synchronous version for compatibility)"""
        if model_name in self.models:
            model = self.models[model_name]
            model.current_requests = max(0, model.current_requests - 1)
            # Fire and forget the async notification
            asyncio.create_task(self._notify_status_change())
    
    async def select_model(self, request_type: str, complexity: str, domain: str, context_size: int) -> Optional[str]:
        """Select the best model for a given request based on type, complexity, and domain"""
        # If in specific mode, use the configured models
        if self.mode == OperationalMode.BUSINESS_DEEP:
            return "llama3.1:70b-instruct-q4_K_M"
        elif self.mode == OperationalMode.DEVELOPMENT:
            if request_type == "code_analysis":
                return "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
        
        # Balanced mode - intelligent selection
        if request_type == "code_analysis":
            # For code, prefer DeepSeek if available
            if self.models["deepseek-coder-v2:16b-lite-instruct-q4_K_M"].status == ModelStatus.LOADED:
                return "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
            # Fallback to any loaded model
            return self.active_primary_model
        
        elif domain == "business" and complexity == "high":
            # For complex business, prefer larger models
            if self.models["llama3.1:70b-instruct-q4_K_M"].status == ModelStatus.LOADED:
                return "llama3.1:70b-instruct-q4_K_M"
            elif self.models["qwen2.5:32b-instruct-q4_K_M"].status == ModelStatus.LOADED:
                return "qwen2.5:32b-instruct-q4_K_M"
        
        elif context_size > 32000:
            # For very long context, use Mistral Nemo
            if self.models["mistral-nemo:latest"].status == ModelStatus.LOADED:
                return "mistral-nemo:latest"
        
        # Default to active primary model
        return self.active_primary_model


# Global orchestrator instance
try:
    orchestrator = ModelOrchestrator()
except Exception as e:
    print(f"ERROR: Failed to initialize ModelOrchestrator: {e}")
    import traceback
    traceback.print_exc()
    orchestrator = None