"""
Script to run the simplified direct FastAPI server.
This bypasses all the complex routing structure.
"""
import os
import sys
import uvicorn

# Make sure the backend directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("Starting Direct FastAPI server...")
    print("This version uses a simplified app without complex routing")
    print("Access at http://localhost:8000")
    uvicorn.run("app.direct_main:app", host="0.0.0.0", port=8000, reload=True)