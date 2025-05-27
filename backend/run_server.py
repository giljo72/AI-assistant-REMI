"""
Script to run the FastAPI server with correct Python module path setup.
This ensures the app module can be found regardless of where the script is run from.
"""
import os
import sys
import uvicorn
import logging
from logging import Filter

# Make sure the backend directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the filter from the app after path is set
from app.core.logging_filter import ResourceEndpointFilter

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("Access at http://localhost:8000")
    print("Resource monitoring logs are filtered to: backend/logs/resource_monitoring.log")
    
    # Get uvicorn's logging config
    log_config = uvicorn.config.LOGGING_CONFIG
    
    # Apply our filter to the access logger
    log_config["loggers"]["uvicorn.access"]["filters"] = ["resource_filter"]
    log_config["filters"] = {
        "resource_filter": {
            "()": ResourceEndpointFilter
        }
    }
    
    # Run the server
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_config=log_config,
        access_log=True
    )