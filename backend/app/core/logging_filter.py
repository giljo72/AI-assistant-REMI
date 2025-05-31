"""
Logging filter to suppress resource monitoring spam
"""
import logging
import os
from logging.handlers import RotatingFileHandler

# Create log directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Set up separate file handler for resource endpoints
resource_handler = RotatingFileHandler(
    os.path.join(log_dir, 'resource_monitoring.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=3
)
resource_handler.setLevel(logging.INFO)
resource_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

class ResourceEndpointFilter(logging.Filter):
    """Filter out resource monitoring endpoints from console"""
    
    def filter(self, record):
        # List of endpoints to suppress
        suppressed_endpoints = [
            '/api/models/status/quick',
            '/api/system/resources',
            '/api/models/memory',
            '/api/system/gpu-stats'
        ]
        
        message = record.getMessage()
        
        # Check if this message contains any suppressed endpoints
        for endpoint in suppressed_endpoints:
            if endpoint in message:
                # Log to file instead of console
                resource_handler.emit(record)
                return False  # Don't show in console
        
        return True  # Show in console