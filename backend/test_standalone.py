"""
Script to test the standalone FastAPI application.
"""
import requests
import json
import os

# Test app base URL (different port than main app)
base_url = "http://localhost:8001"

def test_root():
    """Test the root endpoint."""
    print("Testing root endpoint...")
    response = requests.get(f"{base_url}/")
    
    if response.status_code == 200:
        print("✅ Root endpoint works!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Root endpoint failed with status code {response.status_code}")
        print(response.text)

def test_ping():
    """Test the ping endpoint."""
    print("\nTesting ping endpoint...")
    response = requests.get(f"{base_url}/ping")
    
    if response.status_code == 200:
        print("✅ Ping endpoint works!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Ping endpoint failed with status code {response.status_code}")
        print(response.text)

def test_upload():
    """Test the upload endpoint."""
    print("\nTesting upload endpoint...")
    
    # Create a test file
    test_filepath = "test_standalone.txt"
    with open(test_filepath, "w") as f:
        f.write("This is a test file for standalone app upload testing.")
    
    try:
        with open(test_filepath, "rb") as f:
            files = {"file": (test_filepath, f, "text/plain")}
            data = {"name": "Test file name"}
            
            response = requests.post(f"{base_url}/upload", files=files, data=data)
            
            if response.status_code == 200:
                print("✅ Upload endpoint works!")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"❌ Upload endpoint failed with status code {response.status_code}")
                print(response.text)
    finally:
        # Clean up the test file
        if os.path.exists(test_filepath):
            os.remove(test_filepath)

if __name__ == "__main__":
    print("=" * 50)
    print("STANDALONE APP TESTS")
    print("=" * 50)
    
    # Run tests
    test_root()
    test_ping() 
    test_upload()
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)