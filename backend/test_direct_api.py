"""
Test script for the direct API implementation.
This verifies the simplified API works without the complex router structure.
"""
import requests

BASE_URL = "http://localhost:8000"
ENDPOINTS = [
    "/",
    "/health",
    "/api/ping",
    "/api/status"
]

def test_endpoints():
    """Test all direct endpoints"""
    print("Testing direct API endpoints...")
    
    for endpoint in ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            status = response.status_code
            
            # Print result with color based on status
            if status == 200:
                print(f"✅ GET {url}: Status {status}")
            else:
                print(f"❌ GET {url}: Status {status}")
                
            if status == 200:
                try:
                    # Try to print JSON response
                    print(f"   Response: {response.json()}")
                except:
                    # Fallback to text response
                    print(f"   Response: {response.text[:100]}...")
        except requests.RequestException as e:
            print(f"❌ GET {url}: Error - {str(e)}")
    
    # Test file upload
    test_upload()

def test_upload():
    """Test the upload endpoint"""
    import os
    
    # Create a test file
    test_file_path = "test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for direct upload")
    
    file_obj = None
    try:
        file_obj = open(test_file_path, "rb")
        files = {"file": (os.path.basename(test_file_path), file_obj, "text/plain")}
        data = {
            "name": "Test Upload",
            "description": "Testing the direct upload endpoint"
        }
        
        url = f"{BASE_URL}/api/upload"
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            print(f"✅ POST {url}: Status {response.status_code}")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ POST {url}: Status {response.status_code}")
            print(f"   Error: {response.text}")
    
    finally:
        if file_obj:
            file_obj.close()
        
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_endpoints()