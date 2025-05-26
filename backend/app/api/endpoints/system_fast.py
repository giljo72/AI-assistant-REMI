"""Fast system status endpoints for UI responsiveness"""
from typing import Dict, Any
from fastapi import APIRouter
import logging
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)
router = APIRouter()

# Cache for expensive operations
_model_status_cache = {
    "data": None,
    "timestamp": None,
    "lock": threading.Lock()
}

CACHE_DURATION = timedelta(seconds=5)  # Cache for 5 seconds

@router.get("/active-model-quick")
async def get_active_model_quick() -> Dict[str, Any]:
    """
    Quick endpoint to get just the active model name.
    Uses caching to avoid slow GPU queries.
    """
    with _model_status_cache["lock"]:
        # Check cache
        if (_model_status_cache["data"] is not None and 
            _model_status_cache["timestamp"] is not None and
            datetime.now() - _model_status_cache["timestamp"] < CACHE_DURATION):
            return _model_status_cache["data"]
        
        # Cache miss - get fresh data
        try:
            from ...services.model_orchestrator import orchestrator
            active_model = orchestrator.get_active_model()
            
            result = {
                "active_model": active_model if active_model else "qwen2.5:32b-instruct-q4_K_M",
                "timestamp": datetime.now().isoformat()
            }
            
            # Update cache
            _model_status_cache["data"] = result
            _model_status_cache["timestamp"] = datetime.now()
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting active model: {e}")
            # Return default
            return {
                "active_model": "qwen2.5:32b-instruct-q4_K_M",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

@router.get("/vram-usage-quick")
async def get_vram_usage_quick() -> Dict[str, Any]:
    """
    Quick VRAM usage check with caching.
    """
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        
        return {
            "used_gb": round(info.used / (1024**3), 1),
            "total_gb": round(info.total / (1024**3), 1),
            "free_gb": round(info.free / (1024**3), 1),
            "timestamp": datetime.now().isoformat()
        }
    except:
        return {
            "used_gb": 0,
            "total_gb": 24,
            "free_gb": 24,
            "timestamp": datetime.now().isoformat()
        }