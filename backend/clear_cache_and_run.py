"""
Script to forcefully clear Python's module cache and restart the application.
"""
import sys
import os
import importlib
import subprocess

def clear_module_cache():
    """Clear Python's module cache for our app modules."""
    modules_to_remove = []
    
    # Find all app-related modules in sys.modules
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('app.'):
            modules_to_remove.append(module_name)
    
    # Remove the modules from cache
    for module_name in modules_to_remove:
        del sys.modules[module_name]
    
    print(f"Cleared {len(modules_to_remove)} modules from cache")

def run_server():
    """Run the server with a clean environment."""
    # Clear the module cache
    clear_module_cache()
    
    # Set up environment to force Python not to use bytecode cache
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"  # Don't write .pyc files
    env["PYTHONUNBUFFERED"] = "1"  # Don't buffer stdout/stderr
    
    # Run the server with these settings
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"]
    print(f"Running command: {' '.join(cmd)}")
    
    # Use subprocess to run the server
    subprocess.run(cmd, env=env)

if __name__ == "__main__":
    print("Clearing module cache and starting server with clean environment...")
    run_server()