import os
import requests
import json

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
    
    # Open the file for reading
    with open(test_filepath, "rb") as f:
        # Prepare form data
        files = {"file": (os.path.basename(test_filepath), f, "text/plain")}
        data = {
            "name": "Test File",
            "description": "A test file for testing upload API",
        }
        
        # Make the request
        response = requests.post(url, files=files, data=data)
    
    # Delete the test file
    os.remove(test_filepath)
    
    # Check the response
    if response.status_code == 200:
        print("File upload successful!")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    else:
        print(f"File upload failed with status code {response.status_code}")
        print(response.text)
        return None

def test_processing_status():
    """Test the processing status API endpoint."""
    
    url = f"{base_url}/api/files/processing-status"
    response = requests.get(url)
    
    if response.status_code == 200:
        print("Processing status retrieved successfully!")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    else:
        print(f"Processing status retrieval failed with status code {response.status_code}")
        print(response.text)
        return None

def test_get_all_files():
    """Test retrieving all files."""
    
    url = f"{base_url}/api/files"
    response = requests.get(url)
    
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

if __name__ == "__main__":
    print("Testing file upload...")
    uploaded_file = test_file_upload()
    
    print("\nTesting processing status...")
    test_processing_status()
    
    print("\nTesting get all files...")
    test_get_all_files()