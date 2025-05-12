from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Use mock NeMo if specified or if NeMo import fails
use_mock_nemo = os.getenv("USE_MOCK_NEMO", "false").lower() == "true"

if use_mock_nemo:
    try:
        from backend.app.core.mock_nemo import load_model
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
            from backend.app.core.mock_nemo import load_model
            nemo_model = load_model(os.getenv("MODEL_NAME", "nvidia/nemo-1"))
        except ImportError:
            print("Mock NeMo module not found. Please create the mock module first.")

app = FastAPI(title="AI Assistant API")

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if we're using NeMo
use_nemo = os.getenv("USE_NEMO", "false").lower() == "true"
model_name = os.getenv("MODEL_NAME", "nvidia/nemo-1")

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