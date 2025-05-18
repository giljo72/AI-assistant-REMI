"""
Test endpoints for debugging file uploads and API issues.
"""

import os
import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ...db.database import get_db

router = APIRouter()

@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for testing API connectivity.
    """
    return {"status": "ok", "message": "pong"}

# Add a duplicate endpoint with a different path
@router.get("/ping2")
async def ping2():
    """
    Duplicate ping endpoint for testing with a different path.
    """
    return {"status": "ok", "message": "pong2"}

@router.get("/status")
async def test_status():
    """
    Test status endpoint for checking global processing state.
    """
    return {
        "status": "ok",
        "total_files": 0,
        "processed_files": 0,
        "processing_files": 0,
        "failed_files": 0,
        "gpu_usage": 20.5,  # Mock value
        "message": "This is a test status endpoint"
    }

@router.post("/test-upload")
async def test_upload(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
):
    """
    Test endpoint for file upload without database interactions.
    """
    try:
        content = await file.read(1024)  # Read first 1KB only
        content_preview = content[:100].decode('utf-8', errors='replace') if content else ""
        
        return {
            "status": "success",
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size,
            "name_parameter": name,
            "content_preview": content_preview + ("..." if len(content) > 100 else "")
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e), "type": str(type(e).__name__)}
        )

@router.get("/db-test")
async def test_database(db: Session = Depends(get_db)):
    """
    Test database connectivity.
    """
    try:
        # Simple query to verify DB connection
        result = db.execute("SELECT 1 as test").first()
        return {"status": "connected", "test_value": result[0]}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e), "type": str(type(e).__name__)}
        )