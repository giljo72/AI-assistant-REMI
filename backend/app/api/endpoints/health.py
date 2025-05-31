"""
Simple health check endpoints to verify API is working.
Also provides global access to processing status.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from ...db.database import get_db
from ...document_processing.status_tracker import status_tracker

# Create a router
router = APIRouter()

@router.get("/ping")
async def ping() -> Dict[str, Any]:
    """Simple ping endpoint that always returns successfully."""
    return {
        "status": "ok",
        "message": "pong",
        "service": "API health check"
    }

@router.get("/status")
async def status() -> Dict[str, Any]:
    """Return basic server status information."""
    return {
        "status": "ok",
        "server": "running",
        "version": "1.0.0",
        "environment": "development"
    }

@router.get("/processing-status")
async def global_processing_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Global access to processing status information.
    Access this endpoint via /api/health/processing-status
    """
    try:
        # Get status from tracker
        tracker_status = status_tracker.get_status()
        
        if not tracker_status:
            # Return default values if tracker status is empty
            return {
                "status": "ok",
                "total_files": 0,
                "processed_files": 0,
                "failed_files": 0,
                "processing_files": 0,
                "total_chunks": 0,
                "gpu_usage": 0,
                "eta": 0
            }
            
        # Build response with fallbacks for missing keys
        return {
            "status": "ok",
            "total_files": tracker_status.get("total_files", 0),
            "processed_files": tracker_status.get("processed_files", 0),
            "failed_files": tracker_status.get("failed_files", 0),
            "processing_files": tracker_status.get("processing_files", 0),
            "total_chunks": tracker_status.get("total_chunks", 0),
            "gpu_usage": tracker_status.get("gpu_usage", 0),
            "eta": tracker_status.get("eta", 0)
        }
        
    except Exception as e:
        # Log the error but return a response anyway
        print(f"Error getting processing status: {str(e)}")
        
        # Return basic info even if there's an error
        return {
            "status": "error",
            "message": f"Error retrieving processing status: {str(e)}",
            "total_files": 0,
            "processed_files": 0,
            "failed_files": 0,
            "processing_files": 0
        }