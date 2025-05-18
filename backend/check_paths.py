"""
Script to check if the Python module path is set up correctly
and to verify which files are actually being loaded.
"""
import os
import sys
import importlib.util
import inspect

def check_module_path():
    """Check Python's module search paths"""
    print("\n=== Python Module Search Paths ===")
    for i, path in enumerate(sys.path):
        print(f"{i}: {path}")

def check_file_exists(file_path):
    """Check if a file exists and print its details"""
    abs_path = os.path.abspath(file_path)
    if os.path.exists(abs_path):
        print(f"✅ File exists: {abs_path}")
        print(f"   Size: {os.path.getsize(abs_path)} bytes")
        print(f"   Modified: {os.path.getmtime(abs_path)}")
    else:
        print(f"❌ File not found: {abs_path}")

def check_main_module():
    """Try to import app.main and check its contents"""
    print("\n=== Checking app.main Module ===")
    try:
        # Try to find the module spec
        spec = importlib.util.find_spec("app.main")
        if spec:
            print(f"✅ Module app.main found at: {spec.origin}")
            
            # Try to import the module
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for direct endpoints
            direct_ping = getattr(module, "direct_ping", None)
            direct_health = getattr(module, "direct_health", None)
            
            if direct_ping:
                print(f"✅ Found direct_ping endpoint: {direct_ping}")
                print(f"   Defined in: {inspect.getfile(direct_ping)}")
            else:
                print("❌ direct_ping endpoint not found in app.main")
                
            if direct_health:
                print(f"✅ Found direct_health endpoint: {direct_health}")
                print(f"   Defined in: {inspect.getfile(direct_health)}")
            else:
                print("❌ direct_health endpoint not found in app.main")
        else:
            print("❌ Module app.main not found")
    except Exception as e:
        print(f"❌ Error importing app.main: {str(e)}")

def check_api_router():
    """Try to import app.api.api and check its contents"""
    print("\n=== Checking app.api.api Module ===")
    try:
        # Try to find the module spec
        spec = importlib.util.find_spec("app.api.api")
        if spec:
            print(f"✅ Module app.api.api found at: {spec.origin}")
            
            # Try to import the module
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for routers
            api_router = getattr(module, "api_router", None)
            
            if api_router:
                print(f"✅ Found api_router: {api_router}")
                print(f"   Routes: {len(api_router.routes)}")
                
                # Check if health2_router is included
                health2_imported = False
                fix_files_imported = False
                
                for line in inspect.getsourcelines(module)[0]:
                    if "health2_router" in line:
                        health2_imported = True
                    if "fix_files_router" in line:
                        fix_files_imported = True
                
                if health2_imported:
                    print("✅ health2_router import found in source")
                else:
                    print("❌ health2_router import not found in source")
                    
                if fix_files_imported:
                    print("✅ fix_files_router import found in source")
                else:
                    print("❌ fix_files_router import not found in source")
            else:
                print("❌ api_router not found in app.api.api")
        else:
            print("❌ Module app.api.api not found")
    except Exception as e:
        print(f"❌ Error importing app.api.api: {str(e)}")

def main():
    """Run all checks"""
    # Check Python path
    check_module_path()
    
    # Check critical files
    print("\n=== Checking Critical Files ===")
    check_file_exists("app/main.py")
    check_file_exists("app/api/api.py")
    check_file_exists("app/api/endpoints/health2.py")
    check_file_exists("app/api/endpoints/fix_files.py")
    
    # Check modules
    check_main_module()
    check_api_router()

if __name__ == "__main__":
    main()