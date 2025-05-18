"""
Simplified FastAPI application that doesn't use the complex API router.
This is a cleaner version that only includes direct routes.
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from typing import Optional, Dict, Any

# Create a new FastAPI app
app = FastAPI(
    title="Direct API",
    description="Direct endpoints without complex router structure",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint for verification."""
    return {
        "message": "Direct API is running",
        "version": "0.1.0",
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "source": "direct_main.py"
    }

@app.get("/api/ping")
async def api_ping():
    """Simple ping endpoint under /api."""
    return {
        "message": "pong",
        "source": "direct_main.py"
    }

@app.get("/api/status")
async def api_status():
    """Status endpoint under /api."""
    return {
        "status": "ok",
        "total_files": 0,
        "processed_files": 0,
        "failed_files": 0,
        "processing_files": 0,
        "source": "direct_main.py"
    }

@app.post("/api/upload")
async def api_upload(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Simple file upload endpoint."""
    try:
        content = await file.read(1024)  # Read just first KB
        
        return {
            "status": "success",
            "filename": file.filename,
            "display_name": name,
            "description": description,
            "content_type": file.content_type,
            "content_preview": content[:100].decode('utf-8', errors='replace'),
            "source": "direct_main.py"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": str(type(e).__name__),
            "source": "direct_main.py"
        }