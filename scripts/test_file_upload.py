"""
Test script for file upload functionality
"""
import os
import sys
import requests

def test_file_upload():
    """Test the file upload endpoint directly"""
    
    # Create a simple test file
    test_file_path = "test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for upload testing.")
    
    try:
        print(f"Created test file: {test_file_path}")
        
        # Prepare the file for upload
        files = {
            'file': open(test_file_path, 'rb')
        }
        
        # Prepare the form data
        data = {
            'name': 'Test Upload File',
            'description': 'This is a test upload',
        }
        
        # Make the request to the upload endpoint
        print("Sending upload request to http://localhost:8000/api/files/upload")
        response = requests.post(
            'http://localhost:8000/api/files/upload',
            files=files,
            data=data
        )
        
        # Check the response
        if response.status_code == 200:
            print("Upload successful!")
            print(f"Response: {response.json()}")
            
            # Check if the file exists in the uploads directory
            expected_path = os.path.join("F:", "Assistant", "backend", "data", "uploads")
            print(f"Checking uploads directory: {expected_path}")
            if os.path.exists(expected_path):
                files_in_dir = os.listdir(expected_path)
                print(f"Files in uploads directory: {files_in_dir}")
            else:
                print(f"Uploads directory does not exist: {expected_path}")
            
            return True
        else:
            print(f"Upload failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"Error during file upload test: {e}")
        return False
    finally:
        # Clean up the test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"Removed test file: {test_file_path}")

if __name__ == "__main__":
    success = test_file_upload()
    sys.exit(0 if success else 1)