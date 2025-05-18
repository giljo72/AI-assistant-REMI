"""
Test script for verifying the fixed API endpoints with correct URLs.
This script tests the endpoints with the proper URL structure.
"""
import requests
import os
import sys
import json
from pprint import pprint

# Base URL for API requests
BASE_URL = "http://localhost:8000/api"

def test_health_endpoints():
    """Test health check endpoints"""
    print("\n=== Testing Health Check Endpoints ===")
    
    # Test health ping endpoint
    response = requests.get(f"{BASE_URL}/health/ping")
    print(f"GET /api/health/ping: Status {response.status_code}")
    if response.status_code == 200:
        pprint(response.json())
    else:
        print(response.text)
    
    # Test global processing status endpoint
    response = requests.get(f"{BASE_URL}/health/processing-status")
    print(f"GET /api/health/processing-status: Status {response.status_code}")
    if response.status_code == 200:
        pprint(response.json())
    else:
        print(response.text)

def test_test_endpoints():
    """Test the test endpoints in test_endpoints.py"""
    print("\n=== Testing Test Endpoints ===")
    
    # Test ping endpoint
    response = requests.get(f"{BASE_URL}/test/ping")
    print(f"GET /api/test/ping: Status {response.status_code}")
    if response.status_code == 200:
        pprint(response.json())
    else:
        print(response.text)
    
    # Test status endpoint
    response = requests.get(f"{BASE_URL}/test/status")
    print(f"GET /api/test/status: Status {response.status_code}")
    if response.status_code == 200:
        pprint(response.json())
    else:
        print(response.text)

def test_files_endpoints():
    """Test file-related endpoints with correct URLs"""
    print("\n=== Testing Files Endpoints ===")
    
    # Test file listing endpoint
    response = requests.get(f"{BASE_URL}/files")
    print(f"GET /api/files: Status {response.status_code}")
    if response.status_code == 200:
        files = response.json()
        print(f"Found {len(files)} files")
        if files and len(files) > 0:
            print("First file:")
            pprint(files[0])
    else:
        print(response.text)
    
    # Test processing status with correct URL
    response = requests.get(f"{BASE_URL}/files/processing-status")
    print(f"GET /api/files/processing-status: Status {response.status_code}")
    if response.status_code == 200:
        pprint(response.json())
    else:
        print(response.text)
    
    # Test alternative processing status URL
    response = requests.get(f"{BASE_URL}/files/status")
    print(f"GET /api/files/status: Status {response.status_code}")
    if response.status_code == 200:
        pprint(response.json())
    else:
        print(response.text)
    
    # Test test-status endpoint in files.py
    response = requests.get(f"{BASE_URL}/files/test-status")
    print(f"GET /api/files/test-status: Status {response.status_code}")
    if response.status_code == 200:
        pprint(response.json())
    else:
        print(response.text)

def test_file_upload():
    """Test file upload with JSON tags"""
    print("\n=== Testing File Upload with JSON Tags ===")
    
    # Create a temporary test file
    test_file_path = "test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for upload.\nIt contains some text content.\n")
    
    # Prepare tags as a JSON string
    tags_json = json.dumps(["test", "document", "upload"])
    
    file_obj = None
    try:
        # Prepare the file and form data
        file_obj = open(test_file_path, 'rb')
        files = {
            'file': ('test_upload.txt', file_obj, 'text/plain')
        }
        data = {
            'name': 'Test Upload File',
            'description': 'A file uploaded through the test script',
            'tags': tags_json
        }
        
        # Make the upload request to the correct URL
        response = requests.post(f"{BASE_URL}/files/upload", files=files, data=data)
        print(f"POST /api/files/upload: Status {response.status_code}")
        
        # Print detailed info about the request
        print(f"Request info:")
        print(f"  URL: {response.request.url}")
        print(f"  Method: {response.request.method}")
        print(f"  Headers: {response.request.headers}")
        print(f"  Data keys: {list(data.keys())}")
        
        if response.status_code in (200, 201, 202):
            upload_result = response.json()
            print("Upload successful:")
            pprint(upload_result)
            
            # If upload was successful, also test getting the file by ID
            if 'id' in upload_result:
                file_id = upload_result['id']
                response = requests.get(f"{BASE_URL}/files/{file_id}")
                print(f"GET /api/files/{file_id}: Status {response.status_code}")
                if response.status_code == 200:
                    pprint(response.json())
                else:
                    print(response.text)
        else:
            print("Upload failed:")
            try:
                pprint(response.json())
            except:
                print(response.text)
    
    finally:
        # Properly close the file before trying to remove it
        if file_obj:
            file_obj.close()
            
        # Clean up the test file
        if os.path.exists(test_file_path):
            try:
                os.remove(test_file_path)
            except Exception as e:
                print(f"Warning: Could not remove test file: {e}")

if __name__ == "__main__":
    print("Testing API endpoints with correct URLs...")
    print("Make sure the server is running at http://localhost:8000")
    
    try:
        # Run tests in sequence
        test_health_endpoints()
        test_test_endpoints()
        test_files_endpoints()
        test_file_upload()
        
        print("\n=== All tests completed ===")
    
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API server.")
        print("Make sure the server is running at http://localhost:8000")
    
    except Exception as e:
        print(f"ERROR: Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()