"""
Test script for verifying the new routing approaches.
This script tests both direct routes and routes registered through the API router.
"""
import requests
import json
import os
from pprint import pprint

BASE_URL = "http://localhost:8000"

def test_direct_routes():
    """Test the direct routes added to main.py"""
    print("\n--- Testing Direct Routes ---")
    
    # Test direct ping
    response = requests.get(f"{BASE_URL}/direct-ping")
    print(f"GET /direct-ping: Status {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    
    # Test direct health
    response = requests.get(f"{BASE_URL}/api/direct-health")
    print(f"GET /api/direct-health: Status {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    
    # Test direct status
    response = requests.get(f"{BASE_URL}/api/direct-status")
    print(f"GET /api/direct-status: Status {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

def test_health2_routes():
    """Test the health2 routes"""
    print("\n--- Testing Health2 Routes ---")
    
    # Test ping2
    response = requests.get(f"{BASE_URL}/api/health2/ping2")
    print(f"GET /api/health2/ping2: Status {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    
    # Test status2
    response = requests.get(f"{BASE_URL}/api/health2/status2")
    print(f"GET /api/health2/status2: Status {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

def test_fix_files_routes():
    """Test the fix-files routes"""
    print("\n--- Testing Fix Files Routes ---")
    
    # Test ping
    response = requests.get(f"{BASE_URL}/api/fix-files/ping")
    print(f"GET /api/fix-files/ping: Status {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    
    # Test processing-status
    response = requests.get(f"{BASE_URL}/api/fix-files/processing-status")
    print(f"GET /api/fix-files/processing-status: Status {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    
    # Test simple-upload
    test_file_path = "test_simple_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for simple upload")
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": (os.path.basename(test_file_path), f, "text/plain")}
            data = {
                "filename": "Test Simple Upload",
                "description": "Testing the simplified upload endpoint"
            }
            
            response = requests.post(f"{BASE_URL}/api/fix-files/simple-upload", files=files, data=data)
            print(f"POST /api/fix-files/simple-upload: Status {response.status_code}")
            
            if response.status_code == 200:
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"Error: {response.text}")
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_direct_upload():
    """Test the direct upload endpoint in main.py"""
    print("\n--- Testing Direct Upload ---")
    
    test_file_path = "test_direct_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for direct upload")
    
    file_obj = None
    try:
        file_obj = open(test_file_path, "rb")
        files = {"file": (os.path.basename(test_file_path), file_obj, "text/plain")}
        data = {
            "name": "Test Direct Upload",
            "description": "Testing the direct upload endpoint"
        }
        
        response = requests.post(f"{BASE_URL}/api/direct-upload", files=files, data=data)
        print(f"POST /api/direct-upload: Status {response.status_code}")
        
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    
    finally:
        if file_obj:
            file_obj.close()
        
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    print("Testing API routing approaches...")
    print("Make sure the server is running at http://localhost:8000")
    
    try:
        # Run tests in sequence to diagnose which approaches work
        test_direct_routes()
        test_health2_routes()
        test_fix_files_routes()
        test_direct_upload()
        
        print("\n=== All tests completed ===")
    
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API server.")
        print("Make sure the server is running at http://localhost:8000")
    
    except Exception as e:
        print(f"ERROR: Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()