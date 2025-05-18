"""
Minimal FastAPI application to verify routing functionality.
This is a completely separate test app to rule out complex configuration issues.
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import uvicorn

# Create a minimal FastAPI app
app = FastAPI(
    title="Minimal Test API",
    description="Minimal test API for verifying routing",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint to verify the app is running."""
    return {
        "message": "Minimal Test API is running",
        "status": "ok"
    }

# Simple ping endpoint
@app.get("/ping")
async def ping() -> Dict[str, Any]:
    """Simple ping endpoint for basic connectivity testing."""
    return {
        "message": "pong",
        "status": "ok"
    }

# Test health endpoint
@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "running"
    }

# File info endpoint
@app.post("/file-info")
async def file_info(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """Get information about an uploaded file without saving it."""
    content = await file.read(1024)  # Read first 1KB only
    
    # Return file info
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "name_param": name,
        "content_preview": content[:50].decode("utf-8", errors="replace"),
        "status": "received"
    }

if __name__ == "__main__":
    print("Starting minimal test API on port 8005...")
    print("Try accessing:")
    print("  - http://localhost:8005/")
    print("  - http://localhost:8005/ping")
    print("  - http://localhost:8005/health")
    uvicorn.run(app, host="0.0.0.0", port=8005)