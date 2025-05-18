"""
Direct endpoint tests that focus specifically on the endpoints that were giving issues.
This script tests each problematic endpoint in isolation with detailed error reporting.
"""
import requests
import json
import os
from pprint import pprint

# Base URL
BASE_URL = "http://localhost:8000/api"

def test_endpoint(url, method="GET", data=None, files=None):
    """Test a specific endpoint with detailed error reporting"""
    print(f"\n--- Testing {method} {url} ---")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, data=data, files=files)
        else:
            print(f"Unsupported method: {method}")
            return
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code >= 400:
            print("ERROR RESPONSE:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
            
            if response.status_code == 404:
                print(f"ENDPOINT NOT FOUND: {url}")
                print("Possible causes:")
                print("1. The endpoint is not defined in the router")
                print("2. The router is not included in the API router")
                print("3. The URL path is incorrect")
            
            elif response.status_code == 422:
                print(f"VALIDATION ERROR: Check parameter types and requirements")
                print("Possible causes:")
                print("1. Mismatch between expected and provided parameter types")
                print("2. Missing required parameters")
                print("3. Response model validation failure")
        else:
            print("SUCCESS RESPONSE:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"Error during request: {str(e)}")

def main():
    """Run all the direct endpoint tests"""
    print("TESTING DIRECT ENDPOINTS")
    print("========================")
    
    # Test health endpoints
    test_endpoint(f"{BASE_URL}/health/ping")
    test_endpoint(f"{BASE_URL}/health/status")
    test_endpoint(f"{BASE_URL}/health/processing-status")
    
    # Test test endpoints
    test_endpoint(f"{BASE_URL}/test/ping")
    test_endpoint(f"{BASE_URL}/test/status")
    
    # Test files endpoints
    test_endpoint(f"{BASE_URL}/files/processing-status")
    test_endpoint(f"{BASE_URL}/files/status")
    test_endpoint(f"{BASE_URL}/files/test-status")
    
    # Test file upload
    test_file_upload()
    
    print("\nDirect endpoint tests completed.")

def test_file_upload():
    """Test file upload with minimal form data"""
    # Create a test file
    test_file_path = "simple_test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a simple test file.")
    
    try:
        # Open the file for upload
        file_obj = open(test_file_path, "rb")
        
        # Prepare form data - ONLY include the bare minimum
        files = {
            "file": ("simple_test_upload.txt", file_obj, "text/plain")
        }
        data = {
            "name": "Simple Test Upload"
        }
        
        # Test upload endpoint with minimal data first
        test_endpoint(f"{BASE_URL}/files/upload", "POST", data=data, files=files)
        
        # Close the file object
        file_obj.close()
        
        # Try again with tags
        file_obj = open(test_file_path, "rb")
        files = {
            "file": ("simple_test_upload.txt", file_obj, "text/plain")
        }
        data = {
            "name": "Simple Test Upload",
            "tags": json.dumps(["test"]) 
        }
        
        # Test with tags included
        test_endpoint(f"{BASE_URL}/files/upload", "POST", data=data, files=files)
        
    finally:
        # Clean up
        if 'file_obj' in locals() and file_obj:
            file_obj.close()
        
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    main()