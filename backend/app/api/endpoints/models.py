"""
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