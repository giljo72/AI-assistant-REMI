from fastapi import FastAPI, UploadFile, File, Form, Depends, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import sys
import json
from typing import Optional, List, Dict, Any

from app.api.api import api_router
from app.db.database import Base, engine, get_db
from app.document_processing.status_tracker import status_tracker

# Create database tables
Base.metadata.create_all(bind=engine)

# NeMo integration is handled via Docker container and HTTP API
# Chat endpoints use nemo_docker_client.py for communication
print("Using NeMo Docker container for AI inference")

app = FastAPI(
    title="AI Assistant API",
    description="FastAPI backend for AI Assistant with project-centered containment",
    version="0.1.0",
)

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if we're using NeMo
use_nemo = os.getenv("USE_NEMO", "false").lower() == "true"
use_mock_nemo = os.getenv("USE_MOCK_NEMO", "true").lower() == "true"
model_name = os.getenv("MODEL_NAME", "nvidia/nemo-1")

# Include API router
app.include_router(api_router, prefix="/api")

# Root and health endpoints at application level
@app.get("/")
async def root():
    return {
        "message": "AI Assistant API is running", 
        "model": model_name,
        "using_nemo": use_nemo,
        "using_mock": use_mock_nemo
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "model": model_name,
        "using_nemo": use_nemo,
        "using_mock": use_mock_nemo
    }

@app.get("/ping")
async def root_ping():
    """Simple ping endpoint at root level for easy health checks."""
    return {"message": "pong"}

# Processing status endpoint at root level
@app.get("/processing-status")
async def global_processing_status():
    """
    Global access to processing status information at root level.
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

# Diagnostic endpoints
@app.get("/api/status")
async def api_status():
    """Global API status information."""
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

# Direct file upload endpoint for testing
@app.post("/api/upload")
async def direct_upload(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Direct file upload endpoint for easy testing."""
    try:
        content = await file.read(1024)  # Read just first KB to confirm we got the file
        
        return {
            "status": "success",
            "filename": file.filename,
            "name": name or file.filename,
            "description": description,
            "content_type": file.content_type,
            "size": file.size if hasattr(file, "size") else len(content),
            "content_preview": content[:100].decode('utf-8', errors='replace')
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": str(type(e).__name__)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)