"""
Logging filter to suppress resource monitoring spam
"""
import logging

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
        
        # Check if this is a uvicorn access log
        if record.name == 'uvicorn.access':
            message = record.getMessage()
            # Suppress if it contains any of our resource endpoints
            for endpoint in suppressed_endpoints:
                if endpoint in message and '200 OK' in message:
                    return False
        
        return True