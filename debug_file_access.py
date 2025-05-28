#!/usr/bin/env python3
"""
Debug script to test the file access in chat endpoint
"""
import requests
import json
import sys

def test_chat_file_request(chat_id, message):
    """Test sending a file request through chat"""
    url = f"http://localhost:8000/api/chats/{chat_id}/generate"
    
    payload = {
        "message": message,
        "context_mode": "self-aware",  # Try with self-aware
        "include_context": True,
        "include_project_docs": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # This is a streaming response
            print("Response received (first 500 chars):")
            print(response.text[:500])
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

def test_direct_file_reader():
    """Test the file reader service directly"""
    print("\n" + "="*60)
    print("Testing direct file reader service:")
    
    import sys
    sys.path.insert(0, 'backend')
    
    from app.services.file_reader_service import get_file_reader
    from app.api.endpoints.simple_file_access import inject_file_content_if_requested
    
    # Test the simple file access
    test_messages = [
        "show stop_assistant.py",
        "read test.md",
        "can you display backend/app/main.py"
    ]
    
    for msg in test_messages:
        print(f"\nTesting: '{msg}'")
        content = inject_file_content_if_requested(msg)
        if content:
            print(f"✓ Got content: {len(content)} chars")
            print(f"First 200 chars: {content[:200]}...")
        else:
            print("✗ No content returned")

if __name__ == "__main__":
    # You need to provide a valid chat ID
    if len(sys.argv) > 1:
        chat_id = sys.argv[1]
        print(f"Using chat ID: {chat_id}")
        
        # Test with a file request
        test_chat_file_request(chat_id, "show stop_assistant.py")
    else:
        print("Usage: python debug_file_access.py <chat_id>")
        print("Skipping chat test, running direct file reader test only")
    
    # Test direct file reader
    test_direct_file_reader()