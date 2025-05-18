"""
Script to run the FastAPI server with correct Python module path setup.
This ensures the app module can be found regardless of where the script is run from.
"""
import os
import sys
import uvicorn

# Make sure the backend directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("Access at http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)