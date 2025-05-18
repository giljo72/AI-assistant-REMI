"""
Minimal FastAPI test application to verify functionality.
This is a standalone app for testing only.
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

# Create a fresh FastAPI application
app = FastAPI(
    title="Test API",
    description="Test application for validating FastAPI functionality",
    version="0.1.0",
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint for testing."""
    return {"message": "Test API is running"}

@app.get("/ping")
async def ping():
    """Ping endpoint for testing basic functionality."""
    return {"status": "success", "message": "pong"}

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None)
):
    """Test endpoint for file upload."""
    content = await file.read(1024)  # Read first 1KB
    content_preview = content[:100].decode('utf-8', errors='replace') if content else ""
    
    return {
        "status": "success", 
        "filename": file.filename,
        "name_param": name,
        "content_type": file.content_type,
        "size": file.size if hasattr(file, 'size') else None,
        "content_preview": content_preview + ("..." if len(content) > 100 else "")
    }

if __name__ == "__main__":
    """Run the app directly using uvicorn."""
    print("Starting test application on http://localhost:8001")
    print("Try accessing:")
    print("  - http://localhost:8001/")
    print("  - http://localhost:8001/ping")
    print("  - http://localhost:8001/docs (API documentation)")
    uvicorn.run(app, host="0.0.0.0", port=8001)