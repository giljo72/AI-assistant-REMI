#!/usr/bin/env python
"""
Diagnostic script to identify backend startup issues
Run this from Windows with: venv_nemo\Scripts\python diagnose_backend_startup.py
"""
import sys
import os
import traceback

print("=== AI Assistant Backend Diagnostic ===\n")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print(f"PYTHONPATH: {sys.path}\n")

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
    print(f"Added {backend_path} to PYTHONPATH\n")

# Test critical imports
def test_import(module_name, package=None):
    print(f"Testing import: {module_name}")
    try:
        if package:
            __import__(package + '.' + module_name)
        else:
            __import__(module_name)
        print(f"  ✓ Success\n")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {type(e).__name__}: {e}")
        if hasattr(e, '__cause__') and e.__cause__:
            print(f"    Caused by: {type(e.__cause__).__name__}: {e.__cause__}")
        print("")
        return False

print("=== Testing Core Dependencies ===\n")
test_import('fastapi')
test_import('uvicorn')
test_import('sqlalchemy')
test_import('psycopg2')
test_import('pydantic')
test_import('httpx')
test_import('aiohttp')
test_import('psutil')
test_import('GPUtil')

print("\n=== Testing Pydantic Settings ===\n")
if test_import('pydantic_settings'):
    print("  Using pydantic v2 with pydantic_settings")
else:
    if test_import('pydantic'):
        import pydantic
        print(f"  Pydantic version: {pydantic.VERSION}")
        if pydantic.VERSION.startswith('1.'):
            print("  Note: Using pydantic v1 - may need to update config.py imports")

print("\n=== Testing Application Imports ===\n")
os.chdir('backend')  # Change to backend directory
test_import('database', 'app.db')
test_import('config', 'app.core')
test_import('models', 'app.db')

print("\n=== Testing Service Imports ===\n")
# Test orchestrator specifically
print("Testing ModelOrchestrator import:")
try:
    from app.services.model_orchestrator import ModelOrchestrator
    print("  ✓ Import successful")
    
    print("\nTesting orchestrator instantiation:")
    orchestrator = ModelOrchestrator()
    print("  ✓ Instantiation successful")
    print(f"  Models configured: {len(orchestrator.models)}")
    
except Exception as e:
    print(f"  ✗ Failed: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

print("\n=== Testing Main App ===\n")
try:
    from app.main import app
    print("  ✓ FastAPI app imported successfully")
    print(f"  App title: {app.title}")
    print(f"  App version: {app.version}")
except Exception as e:
    print(f"  ✗ Failed to import app: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

print("\n=== Diagnostic Complete ===")
print("\nTo fix issues:")
print("1. Install missing dependencies: pip install <package>")
print("2. Check import paths and module structure")
print("3. Verify database connection settings")
print("4. Run from correct directory with correct Python environment")