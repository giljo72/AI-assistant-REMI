#!/usr/bin/env python3
import os
import sys

# Add parent directory to path if running from scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Model Reconfiguration Script
Runs all model installation and configuration tasks unattended
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path, PureWindowsPath
import requests
from typing import Dict, List, Optional, Tuple

class ModelReconfiguration:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.backend_path = Path("/mnt/f/assistant/backend")
        self.frontend_path = Path("/mnt/f/assistant/frontend")
        self.models_to_install = [
            "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
        ]
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_ollama_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/version")
            return response.status_code == 200
        except:
            return False
            
    def pull_model(self, model_name: str) -> bool:
        """Pull a model via Ollama API"""
        self.log(f"Pulling model: {model_name}")
        try:
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": model_name},
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "status" in data:
                        status = data["status"]
                        if "total" in data and "completed" in data:
                            percent = (data["completed"] / data["total"]) * 100
                            print(f"\r{status}: {percent:.1f}%", end="", flush=True)
                        else:
                            print(f"\r{status}", end="", flush=True)
                            
            print()  # New line after progress
            self.log(f"Successfully pulled {model_name}")
            return True
            
        except Exception as e:
            self.log(f"Failed to pull {model_name}: {str(e)}", "ERROR")
            return False
            
    def list_models(self) -> List[Dict]:
        """List all installed models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
        except:
            pass
        return []
        
    def create_model_orchestrator(self):
        """Create the ModelOrchestrator service"""
        self.log("Creating ModelOrchestrator service")
        
        orchestrator_code = '''"""
Model Orchestrator Service
Manages multi-model lifecycle and intelligent routing
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
                 max_context: int, endpoint: str):
        self.name = name
        self.backend = backend  # 'nim' or 'ollama'
        self.purpose = purpose  # 'chat', 'reasoning', 'coding', 'embeddings'
        self.memory_gb = memory_gb
        self.max_context = max_context
        self.endpoint = endpoint
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
        
    def _initialize_models(self) -> Dict[str, ModelInfo]:
        """Initialize available models configuration"""
        return {
            "llama-3.1-70b": ModelInfo(
                name="llama-3.1-70b",
                backend="nim",
                purpose="reasoning",
                memory_gb=22,
                max_context=32768,
                endpoint="http://localhost:8000"
            ),
            "qwen2.5-32b": ModelInfo(
                name="qwen2.5-32b",
                backend="ollama",
                purpose="reasoning",
                memory_gb=17,
                max_context=32768,
                endpoint="http://localhost:11434"
            ),
            "deepseek-coder-v2:16b-lite-instruct-q4_K_M": ModelInfo(
                name="deepseek-coder-v2:16b-lite-instruct-q4_K_M",
                backend="ollama",
                purpose="coding",
                memory_gb=9,
                max_context=16384,
                endpoint="http://localhost:11434"
            ),
            "mistral-nemo:latest": ModelInfo(
                name="mistral-nemo:latest",
                backend="ollama",
                purpose="chat",
                memory_gb=7,
                max_context=128000,
                endpoint="http://localhost:11434"
            ),
            "nv-embedqa-e5-v5": ModelInfo(
                name="nv-embedqa-e5-v5",
                backend="nim",
                purpose="embeddings",
                memory_gb=2,
                max_context=512,
                endpoint="http://localhost:8001"
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
        
    async def smart_unload(self, needed_gb: float) -> float:
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
                
            # Don't unload embeddings model or models with active requests
            if model.purpose == "embeddings" or model.current_requests > 0:
                continue
                
            success = await self.unload_model(name)
            if success:
                freed += model.memory_gb
                
        return freed
        
    async def load_model(self, model_name: str) -> bool:
        """Load a specific model"""
        if model_name not in self.models:
            return False
            
        model = self.models[model_name]
        
        if model.status == "loaded":
            return True
            
        if model.status == "loading":
            # Wait for loading to complete
            for _ in range(60):  # 60 second timeout
                await asyncio.sleep(1)
                if model.status != "loading":
                    break
            return model.status == "loaded"
            
        # Check memory availability
        if not await self.ensure_memory_available(model.memory_gb):
            return False
            
        model.status = "loading"
        model.load_time = datetime.now()
        
        try:
            if model.backend == "ollama":
                # Load via Ollama
                response = requests.post(
                    f"{model.endpoint}/api/generate",
                    json={"model": model.name, "prompt": "", "keep_alive": "5m"}
                )
                success = response.status_code == 200
            else:
                # NIM models are always loaded
                success = True
                
            if success:
                model.status = "loaded"
                model.last_used = datetime.now()
                return True
            else:
                model.status = "error"
                return False
                
        except Exception as e:
            model.status = "error"
            return False
            
    async def unload_model(self, model_name: str) -> bool:
        """Unload a specific model"""
        if model_name not in self.models:
            return False
            
        model = self.models[model_name]
        
        if model.status == "unloaded":
            return True
            
        if model.backend == "ollama":
            try:
                # Unload via Ollama
                response = requests.post(
                    f"{model.endpoint}/api/generate",
                    json={"model": model.name, "prompt": "", "keep_alive": "0"}
                )
                if response.status_code == 200:
                    model.status = "unloaded"
                    model.current_requests = 0
                    return True
            except:
                pass
                
        # NIM models cannot be unloaded
        return False
        
    async def switch_mode(self, mode: str) -> Dict[str, bool]:
        """Switch between operational modes"""
        self.mode = mode
        
        mode_configs = {
            "business_deep": ["llama-3.1-70b", "nv-embedqa-e5-v5"],
            "business_fast": ["qwen2.5-32b", "nv-embedqa-e5-v5", "mistral-nemo:latest"],
            "development": ["deepseek-coder-v2:16b-lite-instruct-q4_K_M", 
                          "nv-embedqa-e5-v5", "mistral-nemo:latest"],
            "quick": ["mistral-nemo:latest", "nv-embedqa-e5-v5"],
            "balanced": ["mistral-nemo:latest", "nv-embedqa-e5-v5"]
        }
        
        target_models = mode_configs.get(mode, mode_configs["balanced"])
        results = {}
        
        # Unload models not in target set
        for name, model in self.models.items():
            if name not in target_models and model.status == "loaded":
                results[name] = await self.unload_model(name)
                
        # Load target models
        for model_name in target_models:
            results[model_name] = await self.load_model(model_name)
            
        return results
        
    async def select_model(self, request_type: str, complexity: str = "medium",
                          domain: str = "general", context_size: int = 0) -> Optional[str]:
        """Intelligently select the best model for a request"""
        
        # Embedding requests always use embeddings model
        if request_type == "embedding":
            await self.load_model("nv-embedqa-e5-v5")
            return "nv-embedqa-e5-v5"
            
        # Code analysis requests use deepseek
        if request_type == "code_analysis" or domain == "technical":
            if await self.load_model("deepseek-coder-v2:16b-lite-instruct-q4_K_M"):
                return "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
                
        # High complexity business requests
        if complexity == "high" and domain == "business":
            # Try Llama 70B first
            if await self.load_model("llama-3.1-70b"):
                return "llama-3.1-70b"
            # Fall back to Qwen 32B
            if await self.load_model("qwen2.5-32b"):
                return "qwen2.5-32b"
                
        # Long context requests
        if context_size > 32000:
            if await self.load_model("mistral-nemo:latest"):
                return "mistral-nemo:latest"
                
        # Default to whatever is loaded
        loaded = await self.get_loaded_models()
        for model_name in loaded:
            model = self.models[model_name]
            if model.purpose in ["chat", "reasoning"]:
                return model_name
                
        # Last resort - load mistral-nemo
        if await self.load_model("mistral-nemo:latest"):
            return "mistral-nemo:latest"
            
        return None
        
    async def get_model_status(self) -> List[Dict]:
        """Get status of all models"""
        status_list = []
        
        for name, model in self.models.items():
            status_list.append({
                "name": model.name,
                "backend": model.backend,
                "purpose": model.purpose,
                "status": model.status,
                "memory_gb": model.memory_gb,
                "max_context": model.max_context,
                "last_used": model.last_used.isoformat() if model.last_used else None,
                "tokens_per_second": model.tokens_per_second,
                "current_requests": model.current_requests
            })
            
        return status_list
        
    def mark_model_used(self, model_name: str):
        """Mark a model as recently used"""
        if model_name in self.models:
            self.models[model_name].last_used = datetime.now()
            self.models[model_name].current_requests += 1
            
    def release_model(self, model_name: str):
        """Release a model after use"""
        if model_name in self.models:
            self.models[model_name].current_requests = max(0, 
                self.models[model_name].current_requests - 1)


# Global instance
model_orchestrator = ModelOrchestrator()
'''
        
        orchestrator_path = self.backend_path / "app" / "services" / "model_orchestrator.py"
        orchestrator_path.write_text(orchestrator_code)
        self.log(f"Created {orchestrator_path}")
        
    def update_llm_service(self):
        """Update LLM service to use model orchestrator"""
        self.log("Updating LLM service for model orchestration")
        
        llm_service_code = '''"""
Updated LLM Service with Model Orchestration
"""

import asyncio
import json
from typing import Dict, Any, Optional, AsyncGenerator
import aiohttp
from app.services.model_orchestrator import model_orchestrator

class LLMService:
    """Service for handling LLM interactions with model orchestration"""
    
    def __init__(self):
        self.orchestrator = model_orchestrator
        
    async def generate_response(self, 
                              prompt: str,
                              model: Optional[str] = None,
                              max_tokens: int = 4096,
                              temperature: float = 0.7,
                              stream: bool = True,
                              context_mode: Optional[str] = None,
                              **kwargs) -> AsyncGenerator[str, None]:
        """Generate response with intelligent model selection"""
        
        # Determine request characteristics
        request_type = "chat"
        complexity = "medium"
        domain = "general"
        
        # Analyze prompt for routing hints
        prompt_lower = prompt.lower()
        if any(keyword in prompt_lower for keyword in ["code", "function", "class", "debug", "error"]):
            request_type = "code_analysis"
            domain = "technical"
        elif any(keyword in prompt_lower for keyword in ["business", "strategy", "market", "revenue"]):
            domain = "business"
            complexity = "high" if len(prompt) > 500 else "medium"
        
        # Select model if not specified
        if not model:
            model = await self.orchestrator.select_model(
                request_type=request_type,
                complexity=complexity,
                domain=domain,
                context_size=len(prompt)
            )
            
        if not model:
            raise Exception("No suitable model available")
            
        # Mark model as in use
        self.orchestrator.mark_model_used(model)
        
        try:
            model_info = self.orchestrator.models.get(model)
            if not model_info:
                raise Exception(f"Model {model} not found")
                
            # Route to appropriate backend
            if model_info.backend == "ollama":
                async for chunk in self._generate_ollama(
                    model=model,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream,
                    endpoint=model_info.endpoint
                ):
                    yield chunk
            else:  # NIM
                async for chunk in self._generate_nim(
                    model=model,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream,
                    endpoint=model_info.endpoint
                ):
                    yield chunk
                    
        finally:
            # Release model
            self.orchestrator.release_model(model)
            
    async def _generate_ollama(self, model: str, prompt: str, max_tokens: int,
                             temperature: float, stream: bool, endpoint: str) -> AsyncGenerator[str, None]:
        """Generate response using Ollama backend"""
        async with aiohttp.ClientSession() as session:
            data = {
                "model": model,
                "prompt": prompt,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                },
                "stream": stream
            }
            
            async with session.post(f"{endpoint}/api/generate", json=data) as response:
                if stream:
                    async for line in response.content:
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    yield chunk["response"]
                            except json.JSONDecodeError:
                                continue
                else:
                    result = await response.json()
                    yield result.get("response", "")
                    
    async def _generate_nim(self, model: str, prompt: str, max_tokens: int,
                          temperature: float, stream: bool, endpoint: str) -> AsyncGenerator[str, None]:
        """Generate response using NVIDIA NIM backend"""
        async with aiohttp.ClientSession() as session:
            data = {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": stream
            }
            
            headers = {
                "Authorization": f"Bearer {self.orchestrator.settings.NGC_API_KEY}"
            }
            
            async with session.post(
                f"{endpoint}/v1/chat/completions", 
                json=data,
                headers=headers
            ) as response:
                if stream:
                    async for line in response.content:
                        if line and line.startswith(b"data: "):
                            try:
                                chunk = json.loads(line[6:])
                                if "choices" in chunk:
                                    content = chunk["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
                else:
                    result = await response.json()
                    yield result["choices"][0]["message"]["content"]

# Global instance
llm_service = LLMService()
'''
        
        llm_service_path = self.backend_path / "app" / "services" / "llm_service.py"
        llm_service_path.write_text(llm_service_code)
        self.log(f"Updated {llm_service_path}")
        
    def add_model_api_endpoints(self):
        """Add API endpoints for model management"""
        self.log("Adding model management API endpoints")
        
        models_api_code = '''"""
Model Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.services.model_orchestrator import model_orchestrator

router = APIRouter(prefix="/api/models", tags=["models"])

@router.get("/status")
async def get_models_status() -> List[Dict[str, Any]]:
    """Get status of all available models"""
    return await model_orchestrator.get_model_status()

@router.post("/load/{model_name}")
async def load_model(model_name: str) -> Dict[str, Any]:
    """Load a specific model"""
    success = await model_orchestrator.load_model(model_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to load model {model_name}")
    return {"status": "success", "model": model_name}

@router.post("/unload/{model_name}")
async def unload_model(model_name: str) -> Dict[str, Any]:
    """Unload a specific model"""
    success = await model_orchestrator.unload_model(model_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to unload model {model_name}")
    return {"status": "success", "model": model_name}

@router.post("/switch-mode/{mode}")
async def switch_mode(mode: str) -> Dict[str, Any]:
    """Switch operational mode"""
    valid_modes = ["business_deep", "business_fast", "development", "quick", "balanced"]
    if mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Valid modes: {valid_modes}")
    
    results = await model_orchestrator.switch_mode(mode)
    return {"status": "success", "mode": mode, "results": results}

@router.get("/memory")
async def get_memory_status() -> Dict[str, Any]:
    """Get current memory usage"""
    current_vram = await model_orchestrator.get_current_vram_usage()
    loaded_models = await model_orchestrator.get_loaded_models()
    
    total_allocated = sum(
        model_orchestrator.models[name].memory_gb 
        for name in loaded_models 
        if name in model_orchestrator.models
    )
    
    return {
        "total_vram_gb": model_orchestrator.max_vram_gb,
        "used_vram_gb": current_vram,
        "allocated_vram_gb": total_allocated,
        "available_vram_gb": model_orchestrator.max_vram_gb - current_vram,
        "loaded_models": loaded_models
    }
'''
        
        models_api_path = self.backend_path / "app" / "api" / "endpoints" / "models.py"
        models_api_path.write_text(models_api_code)
        self.log(f"Created {models_api_path}")
        
    def update_main_api_router(self):
        """Update main API router to include models endpoints"""
        self.log("Updating main API router")
        
        api_path = self.backend_path / "app" / "api" / "api.py"
        content = api_path.read_text()
        
        # Add import
        if "from app.api.endpoints import models" not in content:
            import_section = content.find("from app.api.endpoints")
            if import_section != -1:
                # Find the end of imports
                import_end = content.find("\n\n", import_section)
                new_import = "from app.api.endpoints import models"
                content = content[:import_end] + f"\n{new_import}" + content[import_end:]
        
        # Add router
        if "router.include_router(models.router)" not in content:
            # Find where routers are included
            router_section = content.rfind("api_router.include_router")
            if router_section != -1:
                # Find the end of this line
                line_end = content.find("\n", router_section)
                new_router = "api_router.include_router(models.router)"
                content = content[:line_end+1] + f"{new_router}\n" + content[line_end+1:]
        
        api_path.write_text(content)
        self.log(f"Updated {api_path}")
        
    def update_frontend_model_ui(self):
        """Update frontend model UI components"""
        self.log("Updating frontend model UI")
        
        # First, update the SystemModelsPanel component
        models_panel_code = '''import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  IconButton,
  Chip,
  Grid,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Tooltip
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import CircleIcon from '@mui/icons-material/Circle';
import { systemService } from '../../services/systemService';
import { modelService } from '../../services/modelService';

interface ModelStatus {
  name: string;
  backend: 'nim' | 'ollama';
  purpose: 'chat' | 'reasoning' | 'coding' | 'embeddings';
  status: 'loaded' | 'loading' | 'unloaded' | 'error';
  memory_gb: number;
  max_context: number;
  last_used: string | null;
  tokens_per_second: number;
  current_requests: number;
}

interface MemoryStatus {
  total_vram_gb: number;
  used_vram_gb: number;
  allocated_vram_gb: number;
  available_vram_gb: number;
  loaded_models: string[];
}

export const SystemModelsPanel: React.FC = () => {
  const [models, setModels] = useState<ModelStatus[]>([]);
  const [memory, setMemory] = useState<MemoryStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('balanced');
  const [switching, setSwitching] = useState(false);

  const fetchModelStatus = async () => {
    setLoading(true);
    try {
      const [modelStatus, memoryStatus] = await Promise.all([
        modelService.getModelsStatus(),
        modelService.getMemoryStatus()
      ]);
      setModels(modelStatus);
      setMemory(memoryStatus);
    } catch (error) {
      console.error('Failed to fetch model status:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModelStatus();
    const interval = setInterval(fetchModelStatus, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const handleModeSwitch = async (newMode: string) => {
    setSwitching(true);
    try {
      await modelService.switchMode(newMode);
      setMode(newMode);
      await fetchModelStatus();
    } catch (error) {
      console.error('Failed to switch mode:', error);
    } finally {
      setSwitching(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'loaded':
        return <CheckCircleIcon sx={{ color: '#4caf50' }} />;
      case 'loading':
        return <CircularProgress size={20} />;
      case 'error':
        return <ErrorIcon sx={{ color: '#f44336' }} />;
      default:
        return <CircleIcon sx={{ color: '#ccc' }} />;
    }
  };

  const getBackendColor = (backend: string) => {
    return backend === 'nim' ? '#4caf50' : '#2196f3'; // Green for NIM, Blue for Ollama
  };

  const getPurposeLabel = (purpose: string) => {
    const labels = {
      chat: 'Quick Chat & Drafting',
      reasoning: 'Business Analysis & Strategy',
      coding: 'Code Analysis & Development',
      embeddings: 'Document Processing & RAG'
    };
    return labels[purpose] || purpose;
  };

  const formatLastUsed = (lastUsed: string | null) => {
    if (!lastUsed) return 'Never';
    const date = new Date(lastUsed);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Active';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">Model Management</Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Mode</InputLabel>
            <Select
              value={mode}
              onChange={(e) => handleModeSwitch(e.target.value)}
              disabled={switching}
              label="Mode"
            >
              <MenuItem value="business_deep">Business Deep (Llama 70B)</MenuItem>
              <MenuItem value="business_fast">Business Fast (Qwen 32B)</MenuItem>
              <MenuItem value="development">Development (DeepSeek)</MenuItem>
              <MenuItem value="quick">Quick Response (Mistral)</MenuItem>
              <MenuItem value="balanced">Balanced</MenuItem>
            </Select>
          </FormControl>
          <IconButton onClick={fetchModelStatus} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {memory && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle2" gutterBottom>VRAM Usage</Typography>
            <Box sx={{ mb: 1 }}>
              <LinearProgress 
                variant="determinate" 
                value={(memory.used_vram_gb / memory.total_vram_gb) * 100}
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>
            <Typography variant="body2" color="text.secondary">
              {memory.used_vram_gb.toFixed(1)} GB / {memory.total_vram_gb} GB 
              ({memory.available_vram_gb.toFixed(1)} GB available)
            </Typography>
          </CardContent>
        </Card>
      )}

      <Grid container spacing={2}>
        {models.map((model) => (
          <Grid item xs={12} key={model.name}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      {getStatusIcon(model.status)}
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        {model.name}
                      </Typography>
                      <Chip 
                        label={model.backend.toUpperCase()} 
                        size="small"
                        sx={{ 
                          backgroundColor: getBackendColor(model.backend),
                          color: 'white'
                        }}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {getPurposeLabel(model.purpose)}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Memory: {model.memory_gb} GB
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Context: {(model.max_context / 1000).toFixed(0)}K
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Last Used: {formatLastUsed(model.last_used)}
                      </Typography>
                      {model.tokens_per_second > 0 && (
                        <Typography variant="caption" color="text.secondary">
                          Speed: {model.tokens_per_second} tok/s
                        </Typography>
                      )}
                      {model.current_requests > 0 && (
                        <Typography variant="caption" color="primary">
                          Active: {model.current_requests} requests
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};
'''
        
        models_panel_path = self.frontend_path / "src" / "components" / "modals" / "SystemModelsPanel.tsx"
        models_panel_path.write_text(models_panel_code)
        self.log(f"Updated {models_panel_path}")
        
    def create_model_service(self):
        """Create frontend model service"""
        self.log("Creating frontend model service")
        
        model_service_code = '''import api from './api';

export interface ModelStatus {
  name: string;
  backend: 'nim' | 'ollama';
  purpose: 'chat' | 'reasoning' | 'coding' | 'embeddings';
  status: 'loaded' | 'loading' | 'unloaded' | 'error';
  memory_gb: number;
  max_context: number;
  last_used: string | null;
  tokens_per_second: number;
  current_requests: number;
}

export interface MemoryStatus {
  total_vram_gb: number;
  used_vram_gb: number;
  allocated_vram_gb: number;
  available_vram_gb: number;
  loaded_models: string[];
}

class ModelService {
  async getModelsStatus(): Promise<ModelStatus[]> {
    const response = await api.get('/models/status');
    return response.data;
  }

  async getMemoryStatus(): Promise<MemoryStatus> {
    const response = await api.get('/models/memory');
    return response.data;
  }

  async loadModel(modelName: string): Promise<void> {
    await api.post(`/models/load/${modelName}`);
  }

  async unloadModel(modelName: string): Promise<void> {
    await api.post(`/models/unload/${modelName}`);
  }

  async switchMode(mode: string): Promise<void> {
    await api.post(`/models/switch-mode/${mode}`);
  }
}

export const modelService = new ModelService();
'''
        
        model_service_path = self.frontend_path / "src" / "services" / "modelService.ts"
        model_service_path.write_text(model_service_code)
        self.log(f"Created {model_service_path}")
        
    def update_requirements(self):
        """Update requirements.txt with new dependencies"""
        self.log("Updating requirements.txt")
        
        req_path = self.backend_path / "requirements.txt"
        requirements = req_path.read_text()
        
        new_deps = ["gputil==1.4.0", "psutil==5.9.8"]
        
        for dep in new_deps:
            if dep not in requirements:
                requirements += f"\n{dep}"
                
        req_path.write_text(requirements.strip() + "\n")
        self.log(f"Updated {req_path}")
        
    def run_full_configuration(self):
        """Run the complete model reconfiguration"""
        self.log("Starting model reconfiguration process")
        
        # Check if Ollama is running
        if not self.check_ollama_running():
            self.log("Ollama is not running. Please start Ollama first.", "ERROR")
            return
            
        # List current models
        current_models = self.list_models()
        self.log(f"Currently installed models: {len(current_models)}")
        for model in current_models:
            self.log(f"  - {model['name']}")
            
        # Install missing models
        for model_name in self.models_to_install:
            found = any(m['name'] == model_name for m in current_models)
            if not found:
                self.pull_model(model_name)
            else:
                self.log(f"Model {model_name} already installed")
                
        # Create backend components
        self.create_model_orchestrator()
        self.update_llm_service()
        self.add_model_api_endpoints()
        self.update_main_api_router()
        
        # Update frontend components
        self.update_frontend_model_ui()
        self.create_model_service()
        
        # Update requirements
        self.update_requirements()
        
        self.log("Model reconfiguration completed successfully!")
        self.log("Please restart the backend and frontend services to apply changes.")
        
        # Create restart script
        restart_script = '''#!/bin/bash
echo "Restarting AI Assistant services..."

# Stop services
cd /mnt/f/assistant
./stopai.bat

# Wait a moment
sleep 3

# Start services
./startai.bat

echo "Services restarted. Please check the application."
'''
        
        restart_path = Path("/mnt/f/assistant/restart_services.sh")
        restart_path.write_text(restart_script)
        restart_path.chmod(0o755)
        self.log(f"Created restart script: {restart_path}")

if __name__ == "__main__":
    configurator = ModelReconfiguration()
    configurator.run_full_configuration()
'''