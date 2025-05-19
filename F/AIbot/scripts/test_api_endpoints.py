"""
API endpoint testing script for AIbot application.
This script performs tests on all API endpoints to verify they are working correctly.
"""
import requests
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from pprint import pprint

# Color coding for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# API configuration
API_HOST = "http://localhost:8000"
TEST_TIMEOUT = 5  # seconds

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Store test results
test_results = {}

def print_header(message: str) -> None:
    """Print a section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_result(endpoint: str, method: str, status: bool, response_code: int = None, message: str = "", data: Any = None) -> None:
    """Print a test result."""
    status_color = Colors.OKGREEN if status else Colors.FAIL
    status_text = "PASS" if status else "FAIL"
    
    code_text = f" [{response_code}]" if response_code else ""
    print(f"{status_color}{status_text}{Colors.ENDC}{code_text} - {method} {endpoint}")
    if message:
        print(f"     {message}")
    
    # Store result
    if endpoint not in test_results:
        test_results[endpoint] = {}
    
    test_results[endpoint][method] = {
        "status": status,
        "response_code": response_code,
        "message": message,
        "data": data
    }

def make_request(method: str, endpoint: str, data: Any = None, files: Any = None, expected_code: int = 200) -> Tuple[bool, Any, int]:
    """Make an HTTP request to the API."""
    url = f"{API_HOST}{endpoint}"
    response = None
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=TEST_TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, files=files, timeout=TEST_TIMEOUT)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=TEST_TIMEOUT)
        elif method == "PATCH":
            response = requests.patch(url, json=data, timeout=TEST_TIMEOUT)
        elif method == "DELETE":
            response = requests.delete(url, timeout=TEST_TIMEOUT)
        else:
            return False, f"Unsupported method: {method}", 0
        
        # Get response data
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        # Check response code
        success = response.status_code == expected_code
        return success, response_data, response.status_code
    
    except requests.RequestException as e:
        return False, str(e), 0

def test_health_endpoints() -> None:
    """Test health check endpoints."""
    print_header("Health Endpoints")
    
    # Root health endpoint
    success, data, code = make_request("GET", "/health")
    print_result(
        "/health", 
        "GET", 
        success, 
        code,
        f"Response: {data}" if success else f"Error: {data}",
        data
    )
    
    # API health endpoints
    success, data, code = make_request("GET", "/api/health/ping")
    print_result(
        "/api/health/ping", 
        "GET", 
        success, 
        code,
        f"Response: {data}" if success else f"Error: {data}",
        data
    )
    
    success, data, code = make_request("GET", "/api/health/status")
    print_result(
        "/api/health/status", 
        "GET", 
        success, 
        code,
        f"Response: {data}" if success else f"Error: {data}",
        data
    )

def test_project_endpoints() -> None:
    """Test project-related endpoints."""
    print_header("Project Endpoints")
    
    # Get all projects
    success, projects, code = make_request("GET", "/api/projects")
    print_result(
        "/api/projects", 
        "GET", 
        success, 
        code,
        f"Found {len(projects)} projects" if success and isinstance(projects, list) else f"Error: {projects}",
        projects
    )
    
    # Create a test project
    test_project = {
        "name": f"Test Project {int(time.time())}",
        "description": "Created by the API testing script"
    }
    
    success, project, code = make_request("POST", "/api/projects", test_project)
    print_result(
        "/api/projects", 
        "POST", 
        success, 
        code,
        f"Created project with ID: {project.get('id')}" if success else f"Error: {project}",
        project
    )
    
    # If project creation succeeded, test other project endpoints
    if success and isinstance(project, dict) and 'id' in project:
        project_id = project['id']
        
        # Get project by ID
        success, project_detail, code = make_request("GET", f"/api/projects/{project_id}")
        print_result(
            f"/api/projects/{project_id}", 
            "GET", 
            success, 
            code,
            f"Retrieved project: {project_detail.get('name')}" if success else f"Error: {project_detail}",
            project_detail
        )
        
        # Update project
        update_data = {
            "name": f"Updated Test Project {int(time.time())}",
            "description": "Updated by the API testing script"
        }
        
        success, updated_project, code = make_request("PUT", f"/api/projects/{project_id}", update_data)
        print_result(
            f"/api/projects/{project_id}", 
            "PUT", 
            success, 
            code,
            f"Updated project: {updated_project.get('name')}" if success else f"Error: {updated_project}",
            updated_project
        )
        
        # Clean up by deleting the test project
        success, delete_result, code = make_request("DELETE", f"/api/projects/{project_id}")
        print_result(
            f"/api/projects/{project_id}", 
            "DELETE", 
            success, 
            code,
            "Project deleted successfully" if success else f"Error: {delete_result}",
            delete_result
        )

def test_file_endpoints() -> None:
    """Test file-related endpoints."""
    print_header("File Endpoints")
    
    # Get all files
    success, files, code = make_request("GET", "/api/files")
    print_result(
        "/api/files", 
        "GET", 
        success, 
        code,
        f"Found {len(files)} files" if success and isinstance(files, list) else f"Error: {files}",
        files
    )
    
    # Test file upload
    test_file_path = PROJECT_ROOT / "test_upload.txt"
    with open(test_file_path, 'w') as f:
        f.write("This is a test file for upload.\nIt contains some text content.\n")
    
    file_obj = None
    try:
        file_obj = open(test_file_path, 'rb')
        files = {"file": file_obj}
        data = {"name": "Test Upload", "description": "A test file"}
        
        success, upload_result, code = make_request("POST", "/api/files/upload", data=None, files=files, expected_code=200)
        print_result(
            "/api/files/upload", 
            "POST", 
            success, 
            code,
            f"Uploaded file with ID: {upload_result.get('id')}" if success else f"Error: {upload_result}",
            upload_result
        )
        
        # If upload succeeded, test other file endpoints
        if success and isinstance(upload_result, dict) and 'id' in upload_result:
            file_id = upload_result['id']
            
            # Get file by ID
            success, file_detail, code = make_request("GET", f"/api/files/{file_id}")
            print_result(
                f"/api/files/{file_id}", 
                "GET", 
                success, 
                code,
                f"Retrieved file: {file_detail.get('name')}" if success else f"Error: {file_detail}",
                file_detail
            )
            
            # Get file processing status
            success, status, code = make_request("GET", "/api/files/processing-status")
            print_result(
                "/api/files/processing-status", 
                "GET", 
                success, 
                code,
                f"Processing status: {status}" if success else f"Error: {status}",
                status
            )
            
            # Get file preview
            success, preview, code = make_request("GET", f"/api/files/{file_id}/preview")
            print_result(
                f"/api/files/{file_id}/preview", 
                "GET", 
                success, 
                code,
                f"Preview content length: {len(preview.get('content', ''))}" if success else f"Error: {preview}",
                {"content_length": len(preview.get('content', ''))} if success else preview
            )
            
            # Update file
            update_data = {
                "filename": f"Updated Test File {int(time.time())}",
                "description": "Updated by the API testing script"
            }
            
            success, updated_file, code = make_request("PATCH", f"/api/files/{file_id}", update_data)
            print_result(
                f"/api/files/{file_id}", 
                "PATCH", 
                success, 
                code,
                f"Updated file: {updated_file.get('name')}" if success else f"Error: {updated_file}",
                updated_file
            )
            
            # Clean up by deleting the test file
            success, delete_result, code = make_request("DELETE", f"/api/files/{file_id}")
            print_result(
                f"/api/files/{file_id}", 
                "DELETE", 
                success, 
                code,
                "File deleted successfully" if success else f"Error: {delete_result}",
                delete_result
            )
            
    finally:
        if file_obj:
            file_obj.close()
        
        if os.path.exists(test_file_path):
            try:
                os.remove(test_file_path)
            except Exception as e:
                print(f"Warning: Could not remove test file: {e}")

def test_search_endpoints() -> None:
    """Test search-related endpoints."""
    print_header("Search Endpoints")
    
    # Test semantic search
    search_request = {
        "query": "test",
        "limit": 5
    }
    
    success, search_results, code = make_request("POST", "/api/semantic-search/search", search_request)
    print_result(
        "/api/semantic-search/search", 
        "POST", 
        success, 
        code,
        f"Found {len(search_results)} results" if success and isinstance(search_results, list) else f"Error: {search_results}",
        search_results
    )
    
    # Test file search
    file_search_request = {
        "query": "test",
        "limit": 5
    }
    
    success, file_results, code = make_request("POST", "/api/files/search", file_search_request)
    print_result(
        "/api/files/search", 
        "POST", 
        success, 
        code,
        f"Found {len(file_results)} results" if success and isinstance(file_results, list) else f"Error: {file_results}",
        file_results
    )

def test_user_prompt_endpoints() -> None:
    """Test user prompt endpoints."""
    print_header("User Prompt Endpoints")
    
    # Get all user prompts
    success, prompts, code = make_request("GET", "/api/user-prompts")
    print_result(
        "/api/user-prompts", 
        "GET", 
        success, 
        code,
        f"Found {len(prompts)} user prompts" if success and isinstance(prompts, list) else f"Error: {prompts}",
        prompts
    )
    
    # Create a test user prompt
    test_prompt = {
        "name": f"Test Prompt {int(time.time())}",
        "content": "This is a test prompt created by the API testing script",
        "is_active": False
    }
    
    success, prompt, code = make_request("POST", "/api/user-prompts", test_prompt)
    print_result(
        "/api/user-prompts", 
        "POST", 
        success, 
        code,
        f"Created prompt with ID: {prompt.get('id')}" if success else f"Error: {prompt}",
        prompt
    )
    
    # If prompt creation succeeded, test other prompt endpoints
    if success and isinstance(prompt, dict) and 'id' in prompt:
        prompt_id = prompt['id']
        
        # Update user prompt
        update_data = {
            "name": f"Updated Test Prompt {int(time.time())}",
            "content": "Updated by the API testing script",
            "is_active": True
        }
        
        success, updated_prompt, code = make_request("PUT", f"/api/user-prompts/{prompt_id}", update_data)
        print_result(
            f"/api/user-prompts/{prompt_id}", 
            "PUT", 
            success, 
            code,
            f"Updated prompt: {updated_prompt.get('name')}" if success else f"Error: {updated_prompt}",
            updated_prompt
        )
        
        # Activate/deactivate user prompt
        activate_data = {"is_active": False}
        
        success, activation_result, code = make_request("PUT", f"/api/user-prompts/{prompt_id}/activate", activate_data)
        print_result(
            f"/api/user-prompts/{prompt_id}/activate", 
            "PUT", 
            success, 
            code,
            f"Updated activation to: {activation_result.get('is_active')}" if success else f"Error: {activation_result}",
            activation_result
        )
        
        # Clean up by deleting the test prompt
        success, delete_result, code = make_request("DELETE", f"/api/user-prompts/{prompt_id}")
        print_result(
            f"/api/user-prompts/{prompt_id}", 
            "DELETE", 
            success, 
            code,
            "User prompt deleted successfully" if success else f"Error: {delete_result}",
            delete_result
        )

def save_results_to_file() -> None:
    """Save test results to a JSON file."""
    results_file = PROJECT_ROOT / "api_test_results.json"
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "api_host": API_HOST,
        "results": test_results,
        "summary": {
            "total_tests": sum(len(endpoints) for endpoints in test_results.values()),
            "passed_tests": sum(sum(1 for method in endpoints.values() if method["status"]) for endpoints in test_results.values()),
            "failed_tests": sum(sum(1 for method in endpoints.values() if not method["status"]) for endpoints in test_results.values())
        }
    }
    
    with open(results_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nTest results saved to: {results_file}")

def print_summary() -> None:
    """Print a summary of the test results."""
    print_header("Test Summary")
    
    # Count passed and failed tests
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for endpoint, methods in test_results.items():
        for method, result in methods.items():
            total_tests += 1
            if result["status"]:
                passed_tests += 1
            else:
                failed_tests += 1
    
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Print summary
    print(f"Total tests: {total_tests}")
    print(f"Passed tests: {Colors.OKGREEN}{passed_tests}{Colors.ENDC}")
    print(f"Failed tests: {Colors.FAIL if failed_tests > 0 else ''}{failed_tests}{Colors.ENDC}")
    print(f"Pass rate: {Colors.OKGREEN if pass_rate == 100 else Colors.WARNING if pass_rate >= 70 else Colors.FAIL}{pass_rate:.1f}%{Colors.ENDC}")
    
    # If there are failures, list them
    if failed_tests > 0:
        print("\nFailed tests:")
        for endpoint, methods in test_results.items():
            for method, result in methods.items():
                if not result["status"]:
                    print(f"{Colors.FAIL}- {method} {endpoint} [{result.get('response_code', 'N/A')}]{Colors.ENDC}")
                    if result["message"]:
                        print(f"  {result['message']}")

def main() -> None:
    """Main function to run all tests."""
    print(f"{Colors.BOLD}AIbot API Endpoint Tests{Colors.ENDC}")
    print(f"Running tests against {API_HOST} on {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if API is available
    try:
        requests.get(f"{API_HOST}/health", timeout=TEST_TIMEOUT)
    except requests.RequestException:
        print(f"{Colors.FAIL}Error: Cannot connect to API at {API_HOST}{Colors.ENDC}")
        print("Make sure the API server is running before executing this script.")
        return
    
    # Run all tests
    test_health_endpoints()
    test_project_endpoints()
    test_file_endpoints()
    test_search_endpoints()
    test_user_prompt_endpoints()
    
    # Print summary and save results
    print_summary()
    save_results_to_file()

if __name__ == "__main__":
    main()