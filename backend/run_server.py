"""
Script to run the FastAPI server with correct Python module path setup.
This ensures the app module can be found regardless of where the script is run from.
"""
import os
import sys
import uvicorn
import logging
from logging.handlers import RotatingFileHandler

# Make sure the backend directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Custom logging filter to exclude resource polling endpoints
class ExcludeResourceEndpointsFilter(logging.Filter):
    """Filter out resource polling endpoints from console logs"""
    
    def filter(self, record):
        # Check if this is an access log
        if hasattr(record, 'args') and record.args:
            # For uvicorn access logs, the path is in args[2]
            if len(record.args) >= 3:
                path = str(record.args[2])
                # Exclude resource and model status endpoints
                if '/api/system/resources' in path or '/api/models/status/quick' in path:
                    return False
        
        # Also check the message directly
        message = record.getMessage()
        if '/api/system/resources' in message or '/api/models/status/quick' in message:
            return False
            
        return True

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("Access at http://localhost:8000")
    print("Resource polling logs are filtered from console output")
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create a separate log file for resource polling
    resource_handler = RotatingFileHandler(
        'resource_polling.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3
    )
    resource_handler.setLevel(logging.INFO)
    
    # Set up filter for console output
    console_filter = ExcludeResourceEndpointsFilter()
    
    # Apply filter to all console handlers
    for handler in logging.root.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
            handler.addFilter(console_filter)
    
    # Configure uvicorn logging
    log_config = uvicorn.config.LOGGING_CONFIG
    
    # Add filter to uvicorn's access logger
    uvicorn_logger = logging.getLogger("uvicorn.access")
    for handler in uvicorn_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.addFilter(console_filter)
    
    # Run the server
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_config=log_config,
        access_log=True
    )