"""
Script to list all registered routes in the FastAPI application.
"""
import sys
import importlib
from fastapi.openapi.utils import get_openapi

# Add the current directory to the path
sys.path.append('.')

try:
    # Import the main app
    from app.main import app
    
    print("Registered routes in the application:")
    print("====================================")
    
    # Get all routes
    for route in app.routes:
        if hasattr(route, "path"):
            methods = getattr(route, "methods", ["--"])
            print(f"{route.path} {methods}")
    
    # Try to get the API router directly
    try:
        from app.api.api import api_router
        
        print("\nRoutes in api_router:")
        print("====================")
        for route in api_router.routes:
            if hasattr(route, "path"):
                methods = getattr(route, "methods", ["--"])
                print(f"{route.path} {methods}")
    except Exception as e:
        print(f"\nError getting api_router routes: {str(e)}")
    
    # Try to get the specific endpoint routers
    try:
        endpoints = [
            ("files", "app.api.endpoints.files"),
            ("projects", "app.api.endpoints.projects"),
            ("test_endpoints", "app.api.endpoints.test_endpoints")
        ]
        
        for name, module_path in endpoints:
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, "router"):
                    print(f"\nRoutes in {name} router:")
                    print(f"{'=' * (len(name) + 14)}")
                    
                    routes = list(module.router.routes)
                    for route in routes:
                        if hasattr(route, "path"):
                            methods = getattr(route, "methods", ["--"])
                            print(f"{route.path} {methods}")
            except Exception as e:
                print(f"\nError getting {name} router: {str(e)}")
    
    except Exception as e:
        print(f"\nError analyzing endpoint routers: {str(e)}")
    
    # Get full OpenAPI schema
    try:
        schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )
        
        # List all paths from the schema
        print("\nPaths in OpenAPI schema:")
        print("========================")
        for path, path_item in schema.get("paths", {}).items():
            methods = list(path_item.keys())
            print(f"{path} {methods}")
            
    except Exception as e:
        print(f"\nError generating OpenAPI schema: {str(e)}")

except Exception as e:
    print(f"Error importing app: {str(e)}")
    import traceback
    traceback.print_exc()