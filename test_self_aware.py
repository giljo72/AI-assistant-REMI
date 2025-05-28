#!/usr/bin/env python3
"""
Test script to verify self-aware mode file reading functionality
"""
import requests
import json
import sys

# API endpoint
BASE_URL = "http://localhost:8000/api"

def test_api_routes():
    """First check what routes are available"""
    print("0. Checking available API routes:")
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            openapi = response.json()
            paths = list(openapi.get('paths', {}).keys())
            self_aware_paths = [p for p in paths if 'self-aware' in p]
            if self_aware_paths:
                print(f"✓ Found self-aware endpoints: {self_aware_paths}")
            else:
                print("✗ No self-aware endpoints found in API")
                print("  Available endpoints sample:")
                for p in paths[:10]:
                    print(f"    - {p}")
        else:
            print(f"✗ Could not fetch OpenAPI spec: {response.status_code}")
    except Exception as e:
        print(f"✗ Error checking routes: {e}")

def test_self_aware_endpoints():
    """Test the self-aware API endpoints directly"""
    print("\nTesting Self-Aware API Endpoints...\n")
    
    # Test 1: List files in root directory
    print("1. Testing file listing:")
    try:
        response = requests.get(f"{BASE_URL}/self-aware/files")
        if response.status_code == 200:
            files = response.json()
            print(f"✓ Found {len(files)} files/directories")
            for f in files[:5]:
                print(f"  - {f['name']} ({'directory' if f['is_directory'] else 'file'})")
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Connection error: {e}")
    
    # Test 2: Read a specific file
    print("\n2. Testing file reading (Readme.MD):")
    try:
        response = requests.get(f"{BASE_URL}/self-aware/read", params={"path": "Readme.MD"})
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Successfully read file: {data['path']}")
            print(f"  Size: {data['size']} bytes")
            print(f"  First 200 chars: {data['content'][:200]}...")
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Connection error: {e}")
    
    # Test 3: Test enhanced file reader service
    print("\n3. Testing enhanced file reader (backend/app/main.py):")
    try:
        # Import and test directly
        import sys
        sys.path.append('backend')
        from app.services.enhanced_file_reader import get_enhanced_file_reader
        
        reader = get_enhanced_file_reader()
        result = reader.read_file_with_context("backend/app/main.py")
        
        if result['success']:
            print(f"✓ Successfully read file via service")
            print(f"  Language: {result['language']}")
            print(f"  Lines: {result['lines']}")
            print(f"  Has line numbers: {'1 |' in result['numbered_content']}")
        else:
            print(f"✗ Error: {result['error']}")
    except Exception as e:
        print(f"✗ Import error: {e}")

def test_chat_with_self_aware():
    """Test chat endpoint with self-aware mode"""
    print("\n\n4. Testing chat with self-aware mode:")
    
    # Assuming there's a chat already created
    chat_id = "test-chat-id"  # You'll need to replace with actual chat ID
    
    payload = {
        "message": "Can you read the file Readme.MD and show me its contents?",
        "context_mode": "self-aware",  # This is the key!
        "include_context": True,
        "include_project_docs": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chats/{chat_id}/generate",
            json=payload
        )
        
        if response.status_code == 200:
            print("✓ Chat request successful")
            # Note: This returns a streaming response
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"  Details: {response.text}")
    except Exception as e:
        print(f"✗ Connection error: {e}")

def check_context_modes():
    """Check what context modes are available"""
    print("\n5. Checking available context modes:")
    
    # Try to find context mode info
    print("Note: You need to ensure 'self-aware' is an available context mode in the frontend")
    print("The context_mode must be set to 'self-aware' in the chat request")

if __name__ == "__main__":
    print("Self-Aware Mode Test Script")
    print("=" * 50)
    
    # Run tests
    test_api_routes()  # Check routes first
    test_self_aware_endpoints()
    test_chat_with_self_aware()
    check_context_modes()
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print("\nIMPORTANT: Make sure:")
    print("1. Backend has been restarted after code changes")
    print("2. Frontend is sending context_mode='self-aware' in requests")
    print("3. You're using the self-aware context mode in the UI")