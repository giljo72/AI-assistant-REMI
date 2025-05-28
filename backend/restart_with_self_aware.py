#!/usr/bin/env python3
"""
Quick script to verify self-aware module imports correctly
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing self-aware imports...")

try:
    # Test basic imports
    from app.api.endpoints import self_aware
    print("✓ self_aware module imported successfully")
    
    # Test router exists
    print(f"✓ Router prefix: {self_aware.router.prefix}")
    print(f"✓ Number of routes: {len(self_aware.router.routes)}")
    
    # List routes
    print("\nAvailable self-aware routes:")
    for route in self_aware.router.routes:
        if hasattr(route, 'path'):
            print(f"  - {route.methods} {route.path}")
    
    # Test enhanced chat import
    from app.api.endpoints.enhanced_chat import enhance_self_aware_context
    print("\n✓ enhanced_chat module imported successfully")
    
    # Test enhanced file reader
    from app.services.enhanced_file_reader import get_enhanced_file_reader
    reader = get_enhanced_file_reader()
    print("✓ Enhanced file reader initialized")
    
    # Test reading a file
    result = reader.read_file_with_context("Readme.MD")
    if result['success']:
        print(f"✓ Successfully read Readme.MD: {result['lines']} lines")
    else:
        print(f"✗ Failed to read Readme.MD: {result['error']}")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMake sure you're in the backend directory and have activated the virtual environment")
except Exception as e:
    print(f"✗ Error: {e}")

print("\nIf all tests pass, the backend should work correctly when restarted.")