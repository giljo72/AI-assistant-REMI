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

# Create database tables
Base.metadata.create_all(bind=engine)

# Use mock NeMo if specified or if NeMo import fails
use_mock_nemo = os.getenv("USE_MOCK_NEMO", "false").lower() == "true"

if use_mock_nemo:
    try:
        from app.core.mock_nemo import load_model
        nemo_model = load_model(os.getenv("MODEL_NAME", "nvidia/nemo-1"))
        print("Using mock NeMo model for development")
    except ImportError:
        print("Mock NeMo module not found. Please create the mock module first.")
else:
    try:
        # Try to import real NeMo
        import nemo
        print("Using real NeMo model")
        # Add real NeMo initialization here
    except ImportError:
        print("NeMo import failed, falling back to mock")
        try:
            from app.core.mock_nemo import load_model
            nemo_model = load_model(os.getenv("MODEL_NAME", "nvidia/nemo-1"))
        except ImportError:
            print("Mock NeMo module not found. Please create the mock module first.")

app = FastAPI(
    title="AI Assistant API",
    description="FastAPI backend for AI Assistant with project-centered containment",
    version="0.1.0",
)

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if we're using NeMo
use_nemo = os.getenv("USE_NEMO", "false").lower() == "true"
model_name = os.getenv("MODEL_NAME", "nvidia/nemo-1")

# Include API router
app.include_router(api_router, prefix="/api")

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

# Direct routes that bypass the api_router completely
@app.get("/direct-ping")
async def direct_ping():
    """Direct ping endpoint that bypasses the api_router."""
    return {"message": "direct ping successful", "source": "main.py"}

@app.get("/api/direct-health")
async def direct_health():
    """Direct health endpoint with /api prefix that bypasses the api_router."""
    return {"status": "direct health check successful", "source": "main.py"}

@app.get("/api/direct-status")
async def direct_status():
    """Direct status endpoint with /api prefix."""
    return {
        "status": "ok",
        "total_files": 0,
        "processed_files": 0,
        "failed_files": 0,
        "processing_files": 0,
        "source": "direct endpoint in main.py"
    }

@app.post("/api/direct-upload")
async def direct_upload(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Direct file upload endpoint that bypasses the api_router."""
    try:
        content = await file.read(1024)  # Read just first KB to confirm we got the file
        
        return {
            "status": "success",
            "filename": file.filename,
            "display_name": name,
            "description": description,
            "content_type": file.content_type,
            "size": file.size if hasattr(file, "size") else len(content),
            "content_preview": content[:100].decode('utf-8', errors='replace'),
            "source": "direct endpoint in main.py"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": str(type(e).__name__),
            "source": "direct endpoint in main.py"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)