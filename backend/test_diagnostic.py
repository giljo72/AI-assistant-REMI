"""
Test script to check if our diagnostic endpoints are accessible.
"""
import requests
import json
import os
import traceback

# Base URL for the API
base_url = "http://localhost:8000"

def test_ping():
    """Test the ping endpoint."""
    print("Testing ping endpoint...")
    url = f"{base_url}/api/test/ping"
    
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Ping successful!")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Ping failed with status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error testing ping: {str(e)}")
        traceback.print_exc()
        return False

def test_db_connection():
    """Test the database connection endpoint."""
    print("\nTesting database connection...")
    url = f"{base_url}/api/test/db-test"
    
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Database connection successful!")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Database connection failed with status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error testing database connection: {str(e)}")
        traceback.print_exc()
        return False

def test_upload():
    """Test the test-upload endpoint."""
    print("\nTesting file upload endpoint...")
    url = f"{base_url}/api/test/test-upload"
    
    # Create a test file
    test_filepath = "test_diagnostic.txt"
    with open(test_filepath, "w") as f:
        f.write("This is a test file for uploading. Testing 1, 2, 3.")
    
    try:
        with open(test_filepath, "rb") as f:
            files = {"file": (os.path.basename(test_filepath), f, "text/plain")}
            data = {"name": "Test Name"}
            
            response = requests.post(url, files=files, data=data)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ File upload successful!")
                print(json.dumps(response.json(), indent=2))
                return True
            else:
                print(f"❌ File upload failed with status code {response.status_code}")
                print(response.text)
                return False
    except Exception as e:
        print(f"❌ Error testing file upload: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(test_filepath):
            os.remove(test_filepath)

if __name__ == "__main__":
    print("=" * 50)
    print("DIAGNOSTIC TESTS")
    print("=" * 50)
    
    ping_result = test_ping()
    db_result = test_db_connection()
    upload_result = test_upload()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Ping Test: {'✅ PASS' if ping_result else '❌ FAIL'}")
    print(f"Database Test: {'✅ PASS' if db_result else '❌ FAIL'}")
    print(f"Upload Test: {'✅ PASS' if upload_result else '❌ FAIL'}")
    print("=" * 50)