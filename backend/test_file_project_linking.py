import requests
import json
import os
import sys

# Configuration
API_BASE_URL = "http://localhost:8000/api"  # Replace with your actual API base URL

# Test helper functions
def print_header(message):
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except:
        print("Raw Response:", response.text)

def test_file_linking():
    print_header("TESTING FILE-PROJECT LINKING")
    
    # Step 1: Get available projects
    print("\n1. Getting available projects...")
    projects_response = requests.get(f"{API_BASE_URL}/projects")
    print_response(projects_response)
    
    if projects_response.status_code != 200 or not projects_response.json():
        print("Error: No projects available. Please create at least one project.")
        return False
    
    project = projects_response.json()[0]  # Use the first project
    project_id = project["id"]
    project_name = project["name"]
    print(f"Using project: {project_name} (ID: {project_id})")
    
    # Step 2: Get available files
    print("\n2. Getting available files...")
    files_response = requests.get(f"{API_BASE_URL}/files")
    print_response(files_response)
    
    if files_response.status_code != 200 or not files_response.json():
        print("Error: No files available. Please upload at least one file.")
        return False
    
    # Get files that are not already linked to this project
    available_files = [
        f for f in files_response.json() 
        if not f.get("project_id") or f.get("project_id") != project_id
    ]
    
    if not available_files:
        print("Error: No unlinked files available.")
        return False
    
    file_ids = [f["id"] for f in available_files[:2]]  # Use up to 2 files
    print(f"Using files: {', '.join([f['name'] for f in available_files[:2]])}")
    
    # Step 3: Link files to project
    print("\n3. Linking files to project...")
    link_data = {
        "file_ids": file_ids,
        "project_id": project_id
    }
    link_response = requests.post(f"{API_BASE_URL}/files/link", json=link_data)
    print_response(link_response)
    
    if link_response.status_code != 200:
        print("Error: Failed to link files to project.")
        return False
    
    # Verify project_name is in response
    if "project_name" in link_response.json():
        print(f"SUCCESS: Response includes project_name: {link_response.json()['project_name']}")
    else:
        print("WARNING: Response does not include project_name")
    
    # Step 4: Verify files are linked
    print("\n4. Verifying files are linked...")
    for file_id in file_ids:
        file_response = requests.get(f"{API_BASE_URL}/files/{file_id}")
        if file_response.status_code == 200:
            file_data = file_response.json()
            if file_data.get("project_id") == project_id:
                print(f"File {file_id} successfully linked to project")
                
                # Check for project_name
                if file_data.get("project_name") == project_name:
                    print(f"File has correct project_name: {file_data.get('project_name')}")
                else:
                    print(f"WARNING: File has incorrect or missing project_name: {file_data.get('project_name')}")
            else:
                print(f"ERROR: File {file_id} not linked to project")
        else:
            print(f"ERROR: Could not retrieve file {file_id}")
    
    # Step 5: Unlink files
    print("\n5. Unlinking files from project...")
    unlink_data = {
        "file_ids": file_ids,
        "project_id": project_id
    }
    unlink_response = requests.post(f"{API_BASE_URL}/files/unlink", json=unlink_data)
    print_response(unlink_response)
    
    if unlink_response.status_code != 200:
        print("Error: Failed to unlink files from project.")
        return False
    
    # Step 6: Verify files are unlinked
    print("\n6. Verifying files are unlinked...")
    for file_id in file_ids:
        file_response = requests.get(f"{API_BASE_URL}/files/{file_id}")
        if file_response.status_code == 200:
            file_data = file_response.json()
            if not file_data.get("project_id"):
                print(f"File {file_id} successfully unlinked from project")
                
                # Check for project_name
                if not file_data.get("project_name"):
                    print(f"File correctly has no project_name")
                else:
                    print(f"WARNING: File still has project_name: {file_data.get('project_name')}")
            else:
                print(f"ERROR: File {file_id} still linked to project")
        else:
            print(f"ERROR: Could not retrieve file {file_id}")
    
    return True

def test_search_results():
    print_header("TESTING FILE SEARCH WITH PROJECT NAMES")
    
    # Step 1: Perform a search that will return files
    print("\n1. Performing file search...")
    
    # Use a simple generic term that should match something
    search_data = {
        "query": "text"  # This should match some content in most text files
    }
    
    search_response = requests.post(f"{API_BASE_URL}/files/search", json=search_data)
    print_response(search_response)
    
    if search_response.status_code != 200:
        print("Error: Failed to perform search.")
        return False
    
    search_results = search_response.json()
    if not search_results:
        print("No search results found. This may be normal if no files match the query.")
        return True
    
    # Step 2: Check if search results include project_name
    print("\n2. Checking if search results include project_name...")
    
    for result in search_results:
        file_id = result.get("id")
        project_id = result.get("project_id")
        project_name = result.get("project_name")
        
        print(f"File: {result.get('name')} (ID: {file_id})")
        print(f"  - project_id: {project_id}")
        print(f"  - project_name: {project_name}")
        
        # Verify consistency
        if project_id and not project_name:
            print(f"  - WARNING: File has project_id but no project_name")
        elif not project_id and project_name:
            print(f"  - WARNING: File has project_name but no project_id")
        elif project_id and project_name:
            print(f"  - SUCCESS: File correctly has both project_id and project_name")
        else:
            print(f"  - File is not linked to any project")
    
    return True

if __name__ == "__main__":
    print("File Project Linking Test Script")
    print("This script will test file linking and unlinking with project name functionality")
    
    # Run tests
    print("\nStarting tests...")
    
    try:
        # Test file linking/unlinking
        test_file_linking()
        
        # Test search results
        test_search_results()
        
        print("\nAll tests completed.")
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)