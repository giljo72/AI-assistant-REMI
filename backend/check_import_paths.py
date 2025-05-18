"""
Script to check Python import paths and module resolution.
"""
import sys
import os
import importlib.util
import inspect

def check_sys_path():
    """Check sys.path to see where Python is looking for modules."""
    print("Python sys.path:")
    print("===============")
    for i, path in enumerate(sys.path):
        print(f"{i}: {path}")
    print()

def check_module_location(module_name):
    """Check where a module is being loaded from."""
    print(f"Checking module: {module_name}")
    print("=====================" + "=" * len(module_name))
    
    try:
        # Try to import the module
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"Module {module_name} not found")
            return
        
        # Display module location
        print(f"Module found at: {spec.origin}")
        
        # Import the module
        module = importlib.import_module(module_name)
        print(f"Module loaded successfully")
        
        # Check if it's a package
        print(f"Is package: {spec.submodule_search_locations is not None}")
        
        # If it's a package, show submodules
        if spec.submodule_search_locations:
            print(f"Submodule locations: {spec.submodule_search_locations}")
            
        # Display metadata
        print(f"Module file: {module.__file__}")
        if hasattr(module, "__all__"):
            print(f"Exports (__all__): {module.__all__}")
        
        # Show router if present
        if hasattr(module, "router"):
            print(f"Has router: Yes")
            if hasattr(module.router, "routes"):
                routes = list(module.router.routes)
                print(f"Routes defined: {len(routes)}")
                for route in routes:
                    if hasattr(route, "path") and hasattr(route, "methods"):
                        print(f"  - {route.path} [{', '.join(route.methods)}]")
        else:
            print(f"Has router: No")
            
    except Exception as e:
        print(f"Error checking module {module_name}: {str(e)}")
    
    print()

if __name__ == "__main__":
    print("Python Import Path Checker")
    print("=========================")
    print()
    
    # Check sys.path
    check_sys_path()
    
    # Check important modules
    modules_to_check = [
        "app",
        "app.main",
        "app.api",
        "app.api.api",
        "app.api.endpoints",
        "app.api.endpoints.files",
        "app.api.endpoints.test_endpoints"
    ]
    
    for module_name in modules_to_check:
        check_module_location(module_name)