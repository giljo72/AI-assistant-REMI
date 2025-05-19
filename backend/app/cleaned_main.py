"""
FastAPI application for AI Assistant API.
This is the cleaned, production-ready version with unnecessary test endpoints removed.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.api import api_router
from app.db.database import Base, engine

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)