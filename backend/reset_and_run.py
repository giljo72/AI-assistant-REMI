"""
Script to completely reset Python's module cache and run the server.
This helps ensure all changes are picked up.
"""
import os
import sys
import importlib
import uvicorn

def reset_modules():
    """Reset all imported modules to force reloading"""
    print("Resetting Python module cache...")
    
    # Clear modules that might be cached
    modules_to_remove = []
    for module_name in sys.modules:
        if module_name.startswith('app.'):
            modules_to_remove.append(module_name)
    
    # Actually remove the modules
    for module_name in modules_to_remove:
        print(f"Removing module from cache: {module_name}")
        del sys.modules[module_name]
    
    print(f"Removed {len(modules_to_remove)} cached modules")

# Make sure backend directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    # Reset module cache
    reset_modules()
    
    # Choose which server to run
    print("\nWhich server would you like to run?")
    print("1. Original server (app.main:app)")
    print("2. Direct server (app.direct_main:app)")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        # Verify main.py exists
        main_path = os.path.join(current_dir, "app", "main.py")
        if not os.path.exists(main_path):
            print(f"Error: Cannot find {main_path}")
            sys.exit(1)
            
        print("\nStarting original server...")
        print("Access at http://localhost:8000")
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    
    elif choice == "2":
        # Verify direct_main.py exists
        direct_path = os.path.join(current_dir, "app", "direct_main.py")
        if not os.path.exists(direct_path):
            print(f"Error: Cannot find {direct_path}")
            sys.exit(1)
            
        print("\nStarting direct server...")
        print("Access at http://localhost:8000")
        uvicorn.run("app.direct_main:app", host="0.0.0.0", port=8000, reload=True)
    
    else:
        print("Invalid choice. Please run again and enter 1 or 2.")
        sys.exit(1)