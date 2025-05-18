"""
Script to scan API endpoints and check what routes are actually registered.
"""
import sys
import os
import importlib.util
import inspect
from pprint import pprint

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main app
try:
    from app.main import app
    print("Successfully imported the main app")
except Exception as e:
    print(f"Error importing main app: {str(e)}")
    sys.exit(1)

def scan_routes():
    """Scan all registered routes in the FastAPI app."""
    print("\nRegistered Routes:")
    print("================")
    
    # Get all routes
    routes = app.routes
    
    # Display information for each route
    for route in routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            print(f"{route.path} [{', '.join(route.methods)}]")
            
            # Get the endpoint function
            endpoint = route.endpoint
            if hasattr(endpoint, "__module__"):
                print(f"  - Module: {endpoint.__module__}")
            if hasattr(endpoint, "__name__"):
                print(f"  - Function: {endpoint.__name__}")
            print()

def scan_endpoint_modules():
    """Scan API endpoint modules."""
    print("\nAPI Endpoint Modules:")
    print("===================")
    
    # Try to import endpoint modules
    endpoint_modules = [
        "app.api.endpoints.files",
        "app.api.endpoints.projects",
        "app.api.endpoints.chats",
        "app.api.endpoints.user_prompts",
        "app.api.endpoints.semantic_search",
        "app.api.endpoints.admin",
        "app.api.endpoints.test_endpoints"
    ]
    
    for module_name in endpoint_modules:
        try:
            # Import the module
            module = importlib.import_module(module_name)
            print(f"Module {module_name}:")
            
            # Check if it has a router
            if hasattr(module, "router"):
                print(f"  - Has router: Yes")
                
                # Count the routes
                routes = [r for r in module.router.routes]
                print(f"  - Routes defined: {len(routes)}")
                
                # List route paths
                for route in routes:
                    if hasattr(route, "path") and hasattr(route, "methods"):
                        print(f"    - {route.path} [{', '.join(route.methods)}]")
            else:
                print(f"  - Has router: No")
            
            print()
        except Exception as e:
            print(f"Error importing {module_name}: {str(e)}")
            print()

if __name__ == "__main__":
    print("API Route Scanner")
    print("================")
    
    # Scan registered routes
    scan_routes()
    
    # Scan endpoint modules
    scan_endpoint_modules()