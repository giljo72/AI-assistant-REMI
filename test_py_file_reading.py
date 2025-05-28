#!/usr/bin/env python3
"""
Test script to debug why .py files aren't being read in self-aware mode
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from app.services.file_reader_service import get_file_reader
from pathlib import Path

def test_file_reading():
    """Test reading different file types"""
    file_reader = get_file_reader()
    
    test_files = [
        "Readme.MD",           # Works
        "TODO.md",            # Should work
        "stop_assistant.py",  # Not working?
        "backend/app/main.py", # Not working?
        "requirements.txt"    # Should work
    ]
    
    print("Testing File Reader Service")
    print("=" * 60)
    print(f"Base path: {file_reader.base_path}")
    print(f"Allowed extensions: {file_reader.allowed_extensions}")
    print("=" * 60)
    
    for file_path in test_files:
        print(f"\n--- Testing: {file_path} ---")
        
        # Check if file exists
        full_path = file_reader.base_path / file_path
        print(f"Full path: {full_path}")
        print(f"Exists: {full_path.exists()}")
        
        if full_path.exists():
            print(f"Is file: {full_path.is_file()}")
            print(f"Extension: {full_path.suffix}")
            print(f"Size: {full_path.stat().st_size} bytes")
            print(f"Extension allowed: {full_path.suffix.lower() in file_reader.allowed_extensions}")
        
        # Try to read it
        result = file_reader.read_file(file_path)
        
        if result["success"]:
            print(f"✓ Successfully read file")
            print(f"  Content length: {len(result['content'])} chars")
            print(f"  First 100 chars: {result['content'][:100]}...")
        else:
            print(f"✗ Failed to read file")
            print(f"  Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_file_reading()