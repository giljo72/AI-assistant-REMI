"""
Script to check which routes are actually registered in the FastAPI application.
This helps diagnose routing issues at runtime.
"""
import os
import sys
import importlib
import time

# Add the parent directory to the path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_section(title):
    """Print a section title with formatting."""
    print(f"\n{'=' * 50}")
    print(f" {title}")
    print(f"{'=' * 50}")

def import_and_check_module(module_name):
    """Import a module and check if it's loaded correctly."""
    print(f"Importing {module_name}...")
    try:
        module = importlib.import_module(module_name)
        print(f"✓ Successfully imported {module_name}")
        
        # Check if it has a router
        if hasattr(module, "router"):
            print(f"✓ Module has router with {len(list(module.router.routes))} routes")
            return module
        else:
            print(f"✗ Module doesn't have a router attribute")
            return None
    except Exception as e:
        print(f"✗ Failed to import {module_name}: {e}")
        return None

def check_api_router_includes():
    """Check that the API router is including all endpoint routers."""
    print_section("API Router Includes Check")
    
    try:
        # Import the API router
        api_module = importlib.import_module("app.api.api")
        api_router = getattr(api_module, "api_router", None)
        
        if not api_router:
            print("✗ api_router not found in app.api.api")
            return
            
        # Check the import statements
        with open(os.path.join(os.path.dirname(__file__), "app", "api", "api.py"), "r") as f:
            content = f.read()
            
        print("Import statements in api.py:")
        import_lines = [line for line in content.split("\n") if "import" in line]
        for line in import_lines:
            print(f"  {line}")
            
        print("\nRouter includes in api.py:")
        include_lines = [line for line in content.split("\n") if "include_router" in line]
        for line in include_lines:
            print(f"  {line}")
            
    except Exception as e:
        print(f"✗ Error checking API router includes: {e}")

def check_endpoint_routes(endpoint_name):
    """Check routes defined in an endpoint module."""
    print_section(f"{endpoint_name} Routes Check")
    
    try:
        # Import the module
        endpoint_module = importlib.import_module(f"app.api.endpoints.{endpoint_name}")
        router = getattr(endpoint_module, "router", None)
        
        if not router:
            print(f"✗ router not found in app.api.endpoints.{endpoint_name}")
            return
            
        # List all routes
        routes = list(router.routes)
        print(f"Found {len(routes)} routes in {endpoint_name}:")
        
        for route in routes:
            if hasattr(route, "path") and hasattr(route, "methods"):
                print(f"  {route.path} {route.methods}")
                # Check the endpoint function
                if hasattr(route, "endpoint"):
                    print(f"    Function: {route.endpoint.__name__}")
                    print(f"    Module: {route.endpoint.__module__}")
            else:
                print(f"  {route} (missing path or methods)")
                
    except Exception as e:
        print(f"✗ Error checking {endpoint_name} routes: {e}")

def run_health_check():
    """Test connection to the API server."""
    print_section("API Server Health Check")
    
    try:
        import urllib.request
        import json
        
        # Test connection to root endpoint
        print("Testing connection to root endpoint...")
        url = "http://localhost:8000/"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print(f"✓ Server responded: {data}")
            
        # Try a few test endpoints
        test_endpoints = [
            "/api/health/ping",
            "/api/health/status",
            "/api/test/ping",
            "/api/test/ping2",
            "/api/files/test-ping"
        ]
        
        for endpoint in test_endpoints:
            try:
                print(f"Testing {endpoint}...")
                url = f"http://localhost:8000{endpoint}"
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
                    print(f"✓ Endpoint responded: {data}")
            except Exception as e:
                print(f"✗ Failed to access {endpoint}: {e}")
                
    except Exception as e:
        print(f"✗ Health check failed: {e}")

def main():
    """Run all checks."""
    print_section("FastAPI Route Diagnostics")
    print(f"Running diagnostics at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check that modules are loaded correctly
    print_section("Module Loading Check")
    modules_to_check = [
        "app.api.api",
        "app.api.endpoints.files",
        "app.api.endpoints.test_endpoints",
        "app.api.endpoints.health"
    ]
    
    for module_name in modules_to_check:
        import_and_check_module(module_name)
        
    # Check API router includes
    check_api_router_includes()
    
    # Check specific endpoint routes
    check_endpoint_routes("files")
    check_endpoint_routes("test_endpoints")
    check_endpoint_routes("health")
    
    # Run health check if server is running
    run_health_check()

if __name__ == "__main__":
    main()