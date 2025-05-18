"""
Diagnostic FastAPI application to check routing issues.
"""
from fastapi import FastAPI, APIRouter
import uvicorn

# Create main app
app = FastAPI(title="Diagnostic API")

# Create routes
main_router = APIRouter()

@main_router.get("/ping")
async def ping():
    return {"message": "pong from main router"}

# Create a test router
test_router = APIRouter()

@test_router.get("/hello")
async def hello():
    return {"message": "hello from test router"}

@test_router.get("/check")
async def check():
    return {"status": "ok"}

# Include routers
app.include_router(main_router)
app.include_router(test_router, prefix="/test")

@app.get("/")
async def root():
    return {"message": "Diagnostic API is running"}

if __name__ == "__main__":
    print("Starting diagnostic API server...")
    print("Try accessing:")
    print("  - http://localhost:8002/ (Root endpoint)")
    print("  - http://localhost:8002/ping (Main router)")
    print("  - http://localhost:8002/test/hello (Test router)")
    print("  - http://localhost:8002/test/check (Test router)")
    print("  - http://localhost:8002/docs (API documentation)")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)