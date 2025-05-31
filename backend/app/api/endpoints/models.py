"""
Model Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.services.model_orchestrator import orchestrator

router = APIRouter()

@router.get("/status")
async def get_models_status() -> Dict[str, Any]:
    """Get comprehensive status of all available models"""
    return await orchestrator.get_model_status()

@router.get("/status/quick")
async def get_quick_models_status() -> Dict[str, Any]:
    """Get quick model status for frontend (minimal info, no heavy operations)"""
    return await orchestrator.get_quick_model_status()

@router.post("/load/{model_name}")
async def load_model(model_name: str) -> Dict[str, Any]:
    """Load a specific model"""
    success = await orchestrator.load_model(model_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to load model {model_name}")
    return {"status": "success", "model": model_name}

@router.post("/unload/{model_name}")
async def unload_model(model_name: str) -> Dict[str, Any]:
    """Unload a specific model"""
    success = await orchestrator.unload_model(model_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to unload model {model_name}")
    return {"status": "success", "model": model_name}

@router.post("/switch-mode/{mode}")
async def switch_mode(mode: str) -> Dict[str, Any]:
    """Switch operational mode"""
    valid_modes = ["business_deep", "business_fast", "development", "quick", "balanced"]
    if mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Valid modes: {valid_modes}")
    
    results = await orchestrator.switch_mode(mode)
    return {"status": "success", "mode": mode, "results": results}

@router.get("/memory")
async def get_memory_status() -> Dict[str, Any]:
    """Get current memory usage"""
    current_vram = await orchestrator.get_current_vram_usage()
    loaded_models = await orchestrator.get_loaded_models()
    
    total_allocated = sum(
        orchestrator.models[name].memory_gb 
        for name in loaded_models 
        if name in orchestrator.models
    )
    
    return {
        "total_vram_gb": orchestrator.max_vram_gb,
        "used_vram_gb": current_vram,
        "allocated_vram_gb": total_allocated,
        "available_vram_gb": orchestrator.max_vram_gb - current_vram,
        "loaded_models": loaded_models
    }