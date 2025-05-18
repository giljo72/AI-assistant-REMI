import os
import requests
import json
import traceback

# Base URL for the API
base_url = "http://localhost:8000"

def test_file_upload():
    """Test the file upload API endpoint."""
    
    # Path to a test file
    # Create a simple text file for testing
    test_filepath = "test_upload.txt"
    with open(test_filepath, "w") as f:
        f.write("This is a test file for uploading.")
    
    # Prepare the request
    url = f"{base_url}/api/files/upload"
    
    try:
        # Open the file for reading
        with open(test_filepath, "rb") as f:
            # Prepare form data
            files = {"file": (os.path.basename(test_filepath), f, "text/plain")}
            data = {
                "filename": "Test File",  # Change from name to filename
                "description": "A test file for testing upload API",
            }
            
            print("Sending upload request with data:", data)
            print("And file:", files)
            
            # Make the request
            response = requests.post(url, files=files, data=data)
        
        # Check the response
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            print("File upload successful!")
            print(json.dumps(response.json(), indent=2))
            return response.json()
        else:
            print(f"File upload failed with status code {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print("Exception occurred during file upload:")
        print(traceback.format_exc())
        return None
    finally:
        # Delete the test file
        if os.path.exists(test_filepath):
            os.remove(test_filepath)

def test_simple_endpoints():
    """Test simple endpoints that should work without database dependencies."""
    print("\nTesting simple endpoints:")
    
    # Test the test-status endpoint
    print("\nTrying test endpoint: http://localhost:8000/api/files/test-status")
    try:
        response = requests.get(f"{base_url}/api/files/test-status")
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            print("✅ Test endpoint working!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Test endpoint failed with status code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception when calling test endpoint: {str(e)}")

def test_simple_upload():
    """Test the simplified upload endpoint."""
    print("\nTesting simple upload endpoint:")
    
    # Create a simple test file
    test_filepath = "test_upload.txt"
    with open(test_filepath, "w") as f:
        f.write("This is a test file for uploading.")
    
    try:
        # Open the file for reading
        with open(test_filepath, "rb") as f:
            # Prepare form data
            files = {"file": (os.path.basename(test_filepath), f, "text/plain")}
            
            # Make the request
            print("\nTrying simple upload endpoint: http://localhost:8000/api/files/simple-upload")
            response = requests.post(f"{base_url}/api/files/simple-upload", files=files)
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            if response.status_code == 200:
                print("✅ Simple upload endpoint working!")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"❌ Simple upload failed with status code {response.status_code}")
                print(response.text)
    except Exception as e:
        print(f"❌ Exception when calling simple upload: {str(e)}")
    finally:
        # Delete the test file
        if os.path.exists(test_filepath):
            os.remove(test_filepath)

def test_processing_status():
    """Test the processing status API endpoint."""
    
    # Try all versions of the endpoint
    endpoints = [
        "/api/files/processing-status", 
        "/api/files/processing_status",
        "/api/files/processing-stats",
        "/api/files/status"  # Added the simple URL endpoint
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTrying endpoint: {url}")
        
        try:
            response = requests.get(url)
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            if response.status_code == 200:
                print("Processing status retrieved successfully!")
                print(json.dumps(response.json(), indent=2))
                return response.json()
            else:
                print(f"Processing status retrieval failed with status code {response.status_code}")
                print(response.text)
        except Exception as e:
            print("Exception occurred during processing status retrieval:")
            print(traceback.format_exc())
    
    return None

def test_get_all_files():
    """Test retrieving all files."""
    
    url = f"{base_url}/api/files"
    
    try:
        response = requests.get(url)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            print("Files retrieved successfully!")
            print(f"Found {len(response.json())} files.")
            if response.json():
                # Print details of the first file
                print(json.dumps(response.json()[0], indent=2))
            return response.json()
        else:
            print(f"File retrieval failed with status code {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print("Exception occurred during file retrieval:")
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    print("Testing simple endpoints first...")
    test_simple_endpoints()
    
    print("\nTesting simple upload...")
    test_simple_upload()
    
    print("\nTesting processing status...")
    test_processing_status()
    
    print("\nTesting regular file upload...")
    uploaded_file = test_file_upload()
    
    print("\nTesting get all files...")
    test_get_all_files()