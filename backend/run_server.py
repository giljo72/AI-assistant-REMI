"""
Script to run the FastAPI server with correct Python module path setup.
This ensures the app module can be found regardless of where the script is run from.
"""
import os
import sys
import uvicorn
import logging
from datetime import datetime

# Make sure the backend directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the existing resource filter
try:
    from app.core.logging_filter import ResourceEndpointFilter
    has_resource_filter = True
except ImportError:
    has_resource_filter = False

# Custom formatter that transforms access logs - must be at module level for multiprocessing
class EnhancedAccessFormatter(logging.Formatter):
    # ANSI color codes
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record):
        # Get the formatted message from uvicorn
        msg = super().format(record)
        
        # Skip resource monitoring endpoints if filter available
        if has_resource_filter:
            if '/api/system/resources' in msg or '/api/models/status/quick' in msg:
                return ""  # Return empty to skip
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract parts from uvicorn message format: INFO:     127.0.0.1:52826 - "GET /api/... HTTP/1.1" 200 OK
        if ' - "' in msg and '" ' in msg:
            try:
                # Remove the INFO: prefix if present
                if msg.startswith('INFO:'):
                    msg = msg[5:].strip()
                
                parts = msg.split(' - "')
                client = parts[0].strip()
                request_and_status = parts[1].split('" ')
                request = request_and_status[0]
                status = request_and_status[1] if len(request_and_status) > 1 else ''
                
                # Extract just the path from the request
                request_parts = request.split(' ')
                method = request_parts[0] if request_parts else ''
                path = request_parts[1] if len(request_parts) > 1 else ''
                
                # Determine action name based on method and path
                action = "Request"
                if method == 'POST' and '/api/files/upload' in path:
                    action = "Upload Document"
                elif method == 'GET' and path == '/api/files':
                    action = "List Files"
                elif method == 'POST' and '/api/files/' in path and '/process' in path:
                    action = "Process Document"
                elif method == 'POST' and '/api/chats/' in path and '/generate' in path:
                    action = "Chat Message"
                elif method == 'GET' and '/api/chats' in path:
                    action = "Get Chats"
                elif method == 'POST' and path == '/api/projects':
                    action = "Create Project"
                elif method == 'GET' and path == '/api/projects':
                    action = "List Projects"
                elif method == 'GET' and '/api/system/' in path:
                    action = "System Check"
                elif method == 'POST' and '/api/semantic-search' in path:
                    action = "Search Documents"
                elif method == 'GET' and '/api/system-prompts' in path:
                    action = "Get System Prompts"
                elif method == 'GET' and '/api/user-prompts' in path:
                    action = "Get User Prompts"
                elif method == 'POST' and '/api/system-prompts/seed-defaults' in path:
                    action = "Initialize Prompts"
                elif method == 'GET' and path == '/':
                    action = "Home Page"
                elif method == 'GET' and '/docs' in path:
                    action = "API Documentation"
                elif method == 'GET' and '/api/models/' in path:
                    action = "Model Status"
                elif method == 'POST' and '/api/preferences' in path:
                    action = "Update Preferences"
                elif method == 'GET' and '/api/preferences' in path:
                    action = "Get Preferences"
                
                # Determine color and icon based on status
                if '200' in status or '201' in status:
                    icon = '✓'
                    color = self.GREEN
                elif '307' in status or '301' in status or '302' in status or '304' in status:
                    icon = '→'
                    color = self.CYAN  # Cyan for redirects/not modified
                elif '400' in status or '401' in status or '403' in status:
                    icon = '⚠'
                    color = self.YELLOW  # Yellow for client errors
                elif '404' in status:
                    icon = '✗'
                    color = self.YELLOW  # Yellow for not found
                elif '500' in status or '502' in status or '503' in status:
                    icon = '⚠'
                    color = self.RED  # Red for server errors
                else:
                    icon = '•'
                    color = self.RESET  # Normal color for unknown
                
                # Create enhanced message with color
                timestamp_colored = f"{color}[{timestamp}]{self.RESET}"
                icon_colored = f"{color}{icon}{self.RESET}"
                status_colored = f"{color}{status}{self.RESET}"
                
                # Add bold to action names for better visibility
                action_styled = f"{self.BOLD}{action}{self.RESET}"
                
                return f"{timestamp_colored} {icon_colored} {action_styled:<35} | {method:<6} {path:<45} | {status_colored}"
            except Exception:
                # If parsing fails, return original with timestamp in normal color
                return f"[{timestamp}] {msg}"
        else:
            # Not an access log format we recognize
            return f"[{timestamp}] {msg}"

if __name__ == "__main__":
    print("=" * 80)
    print(f"AI Assistant Backend - Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Access URL: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    
    # Add resource filter if available
    if has_resource_filter:
        print("Resource monitoring endpoints filtered to: backend/logs/resource_monitoring.log")
    
    print("Enhanced logging enabled with timestamps and action names")
    print("=" * 80)
    print()
    
    # Custom log config for uvicorn with our enhanced formatter
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
            "enhanced_access": {
                "()": EnhancedAccessFormatter,
                "fmt": "%(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "enhanced_access": {
                "formatter": "enhanced_access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["enhanced_access"], "level": "INFO", "propagate": False},
        },
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