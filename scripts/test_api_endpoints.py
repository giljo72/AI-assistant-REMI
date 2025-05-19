#!/usr/bin/env python
"""
API endpoint testing script for the AI Assistant.
Tests all API endpoints to ensure they're working correctly.
Can run autonomously or be integrated into the application.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime

# Terminal colors for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Configuration
CONFIG = {
    "api_base_url": "http://localhost:8000",
    "timeout": 10,  # seconds
    "output_file": "api_test_results.json",
    "test_file_path": os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_upload.txt")
}

# Results storage
results = {
    "timestamp": datetime.now().isoformat(),
    "endpoints": {},
    "summary": {"success": 0, "failure": 0, "total": 0}
}

def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 50}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD} {title} {Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 50}{Colors.ENDC}")

def print_result(endpoint: str, method: str, success: bool, status_code: str, details: str, data: Any = None) -> None:
    """Print a formatted result and store it in the results dictionary."""
    status = f"{Colors.GREEN}✓ PASS{Colors.ENDC}" if success else f"{Colors.RED}✗ FAIL{Colors.ENDC}"
    print(f"{Colors.BOLD}{method} {endpoint}:{Colors.ENDC} {status} [{status_code}]")
    print(f"  {details}")
    
    # Store result
    if endpoint not in results["endpoints"]:
        results["endpoints"][endpoint] = {}
    
    results["endpoints"][endpoint][method] = {
        "success": success,
        "status_code": status_code,
        "details": details,
        "data": data
    }
    
    # Update summary
    if success:
        results["summary"]["success"] += 1
    else:
        results["summary"]["failure"] += 1
    
    results["summary"]["total"] += 1

def make_request(method: str, endpoint: str, data: Any = None, files: Any = None) -> Tuple[bool, Any, str]:
    """Make an HTTP request to the API and return success status, response data, and status code."""
    url = f"{CONFIG['api_base_url']}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=CONFIG["timeout"])
        elif method == "POST":
            response = requests.post(url, json=data, files=files, timeout=CONFIG["timeout"])
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=CONFIG["timeout"])
        elif method == "DELETE":
            response = requests.delete(url, timeout=CONFIG["timeout"])
        else:
            return False, f"Unsupported method: {method}", "ERROR"
        
        # Try to parse response as JSON
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = response.text
        
        # Determine success based on status code
        success = 200 <= response.status_code < 300
        
        return success, response_data, str(response.status_code)
    
    except requests.RequestException as e:
        return False, str(e), "ERROR"

def create_test_file() -> bool:
    """Create a test file for upload testing."""
    try:
        with open(CONFIG["test_file_path"], 'w') as f:
            f.write("This is a test file for API endpoint testing.\n")
            f.write(f"Created at: {datetime.now().isoformat()}\n")
        return True
    except Exception as e:
        print(f"Error creating test file: {str(e)}")
        return False

def test_health_endpoints() -> None:
    """Test health and status endpoints."""
    print_header("Health Endpoints")
    
    # Root health endpoint
    success, data, code = make_request("GET", "/api/health")
    print_result(
        "/api/health", 
        "GET", 
        success, 
        code,
        "Health endpoint is responding" if success else f"Health endpoint error: {data}"
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
        "name": f"Test Project {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Created by API endpoint test"
    }
    
    success, new_project, code = make_request("POST", "/api/projects", test_project)
    print_result(
        "/api/projects", 
        "POST", 
        success, 
        code,
        "Created test project" if success else f"Error creating project: {new_project}",
        new_project
    )
    
    # If project creation succeeded, test getting the project and then deleting it
    if success and isinstance(new_project, dict) and "id" in new_project:
        project_id = new_project.get("id")
        
        # Get project by ID
        success, project, code = make_request("GET", f"/api/projects/{project_id}")
        print_result(
            f"/api/projects/{project_id}", 
            "GET", 
            success, 
            code,
            "Retrieved test project" if success else f"Error getting project: {project}",
            project
        )
        
        # Update project
        update_data = {
            "name": f"Updated Test Project {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "Updated by API endpoint test"
        }
        
        success, updated_project, code = make_request("PUT", f"/api/projects/{project_id}", update_data)
        print_result(
            f"/api/projects/{project_id}", 
            "PUT", 
            success, 
            code,
            "Updated test project" if success else f"Error updating project: {updated_project}",
            updated_project
        )
        
        # Delete project
        success, delete_result, code = make_request("DELETE", f"/api/projects/{project_id}")
        print_result(
            f"/api/projects/{project_id}", 
            "DELETE", 
            success, 
            code,
            "Deleted test project" if success else f"Error deleting project: {delete_result}",
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
    
    # Create a test file for upload
    if create_test_file():
        # Upload a file
        with open(CONFIG["test_file_path"], 'rb') as f:
            file_data = {
                'file': (os.path.basename(CONFIG["test_file_path"]), f, 'text/plain')
            }
            
            form_data = {
                'tags': json.dumps(["test", "api"]),
                'project_id': None
            }
            
            # Make POST request with multipart/form-data
            url = f"{CONFIG['api_base_url']}/api/files/upload"
            try:
                response = requests.post(
                    url, 
                    files=file_data, 
                    data=form_data,
                    timeout=CONFIG["timeout"]
                )
                
                # Try to parse response as JSON
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = response.text
                
                success = 200 <= response.status_code < 300
                code = str(response.status_code)
                
                print_result(
                    "/api/files/upload", 
                    "POST", 
                    success, 
                    code,
                    "Uploaded test file" if success else f"Error uploading file: {response_data}",
                    response_data
                )
                
                # If upload succeeded, test file processing status
                if success and isinstance(response_data, dict) and "id" in response_data:
                    file_id = response_data.get("id")
                    
                    # Check processing status
                    success, status_data, code = make_request("GET", f"/api/files/processing-status/{file_id}")
                    print_result(
                        f"/api/files/processing-status/{file_id}", 
                        "GET", 
                        success, 
                        code,
                        "Retrieved file processing status" if success else f"Error getting status: {status_data}",
                        status_data
                    )
                    
                    # Get file content
                    success, content_data, code = make_request("GET", f"/api/files/{file_id}")
                    print_result(
                        f"/api/files/{file_id}", 
                        "GET", 
                        success, 
                        code,
                        "Retrieved file content" if success else f"Error getting file: {content_data}",
                        content_data
                    )
                
            except requests.RequestException as e:
                print_result(
                    "/api/files/upload", 
                    "POST", 
                    False, 
                    "ERROR",
                    f"Error uploading file: {str(e)}"
                )
    else:
        print_result(
            "/api/files/upload", 
            "POST", 
            False, 
            "ERROR",
            "Could not create test file for upload"
        )
    
    # Clean up test file
    try:
        if os.path.exists(CONFIG["test_file_path"]):
            os.remove(CONFIG["test_file_path"])
    except:
        pass

def test_search_endpoints() -> None:
    """Test semantic search endpoints."""
    print_header("Search Endpoints")
    
    # Test semantic search
    search_query = {
        "query": "test",
        "project_id": None,
        "limit": 5
    }
    
    success, search_results, code = make_request("POST", "/api/semantic-search", search_query)
    print_result(
        "/api/semantic-search", 
        "POST", 
        success, 
        code,
        f"Search returned {len(search_results)} results" if success and isinstance(search_results, list) else 
        f"Error performing search: {search_results}",
        search_results
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
        "name": f"Test Prompt {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "content": "This is a test prompt created by API endpoint test",
        "is_active": False,
        "project_id": None
    }
    
    success, new_prompt, code = make_request("POST", "/api/user-prompts", test_prompt)
    print_result(
        "/api/user-prompts", 
        "POST", 
        success, 
        code,
        "Created test user prompt" if success else f"Error creating user prompt: {new_prompt}",
        new_prompt
    )
    
    # If prompt creation succeeded, test updating and activating it
    if success and isinstance(new_prompt, dict) and "id" in new_prompt:
        prompt_id = new_prompt.get("id")
        
        # Update user prompt
        update_data = {
            "name": f"Updated Test Prompt {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "content": "This is an updated test prompt",
            "is_active": False,
            "project_id": None
        }
        
        success, updated_prompt, code = make_request("PUT", f"/api/user-prompts/{prompt_id}", update_data)
        print_result(
            f"/api/user-prompts/{prompt_id}", 
            "PUT", 
            success, 
            code,
            "Updated test user prompt" if success else f"Error updating user prompt: {updated_prompt}",
            updated_prompt
        )
        
        # Activate user prompt
        activate_data = {"is_active": True}
        success, activated_prompt, code = make_request("PUT", f"/api/user-prompts/{prompt_id}/activate", activate_data)
        print_result(
            f"/api/user-prompts/{prompt_id}/activate", 
            "PUT", 
            success, 
            code,
            "Activated test user prompt" if success else f"Error activating user prompt: {activated_prompt}",
            activated_prompt
        )
        
        # Clean up - if we managed to create the prompt, try to deactivate it
        deactivate_data = {"is_active": False}
        success, deactivated_prompt, code = make_request("PUT", f"/api/user-prompts/{prompt_id}/activate", deactivate_data)
        print_result(
            f"/api/user-prompts/{prompt_id}/deactivate", 
            "PUT", 
            success, 
            code,
            "Deactivated test user prompt" if success else f"Error deactivating user prompt: {deactivated_prompt}",
            deactivated_prompt
        )

def test_chat_endpoints() -> None:
    """Test chat-related endpoints."""
    print_header("Chat Endpoints")
    
    # First create a test project to associate chats with
    test_project = {
        "name": f"Chat Test Project {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Created for chat API endpoint test"
    }
    
    success, project, code = make_request("POST", "/api/projects", test_project)
    
    if success and isinstance(project, dict) and "id" in project:
        project_id = project.get("id")
        
        # Get chats for project
        success, chats, code = make_request("GET", f"/api/chats/project/{project_id}")
        print_result(
            f"/api/chats/project/{project_id}", 
            "GET", 
            success, 
            code,
            f"Found {len(chats)} chats" if success and isinstance(chats, list) else f"Error: {chats}",
            chats
        )
        
        # Create a test chat
        test_chat = {
            "name": f"Test Chat {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "project_id": project_id
        }
        
        success, new_chat, code = make_request("POST", "/api/chats", test_chat)
        print_result(
            "/api/chats", 
            "POST", 
            success, 
            code,
            "Created test chat" if success else f"Error creating chat: {new_chat}",
            new_chat
        )
        
        # If chat creation succeeded, test sending a message
        if success and isinstance(new_chat, dict) and "id" in new_chat:
            chat_id = new_chat.get("id")
            
            # Get chat by ID
            success, chat, code = make_request("GET", f"/api/chats/{chat_id}")
            print_result(
                f"/api/chats/{chat_id}", 
                "GET", 
                success, 
                code,
                "Retrieved test chat" if success else f"Error getting chat: {chat}",
                chat
            )
            
            # Send a test message
            test_message = {
                "content": "This is a test message sent by API endpoint test",
                "type": "user"
            }
            
            success, message_result, code = make_request("POST", f"/api/chats/{chat_id}/messages", test_message)
            print_result(
                f"/api/chats/{chat_id}/messages", 
                "POST", 
                success, 
                code,
                "Sent test message" if success else f"Error sending message: {message_result}",
                message_result
            )
            
            # Get chat messages
            success, messages, code = make_request("GET", f"/api/chats/{chat_id}/messages")
            print_result(
                f"/api/chats/{chat_id}/messages", 
                "GET", 
                success, 
                code,
                f"Retrieved {len(messages)} messages" if success and isinstance(messages, list) else 
                f"Error getting messages: {messages}",
                messages
            )
        
        # Clean up by deleting test project
        success, delete_result, code = make_request("DELETE", f"/api/projects/{project_id}")
        print(f"Cleaned up test project for chat tests: {'Success' if success else 'Failed'}")
    else:
        print_result(
            "/api/chats", 
            "TEST", 
            False, 
            "SKIPPED",
            "Skipped chat tests because test project creation failed"
        )

def save_results() -> None:
    """Save test results to a JSON file."""
    output_file = CONFIG["output_file"]
    
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n{Colors.CYAN}Results saved to {output_file}{Colors.ENDC}")
        
    except Exception as e:
        print(f"\n{Colors.RED}Failed to save results: {str(e)}{Colors.ENDC}")

def print_summary() -> None:
    """Print a summary of the test results."""
    total = results["summary"]["total"]
    success = results["summary"]["success"]
    failure = results["summary"]["failure"]
    success_rate = success / total if total > 0 else 0
    
    print_header("Test Summary")
    
    if success_rate == 1.0:
        color = Colors.GREEN
        status = "ALL TESTS PASSED"
    elif success_rate >= 0.8:
        color = Colors.YELLOW
        status = "MOST TESTS PASSED"
    elif success_rate >= 0.5:
        color = Colors.YELLOW
        status = "PARTIAL SUCCESS"
    else:
        color = Colors.RED
        status = "MOST TESTS FAILED"
    
    print(f"{color}{Colors.BOLD}{status}{Colors.ENDC}")
    print(f"Total endpoints tested: {total}")
    print(f"Successful tests: {Colors.GREEN}{success}{Colors.ENDC}")
    print(f"Failed tests: {Colors.RED}{failure}{Colors.ENDC}")
    print(f"Success rate: {color}{int(success_rate * 100)}%{Colors.ENDC}")
    
    # Group failures by HTTP status code for easier debugging
    failures_by_code = {}
    for endpoint, methods in results["endpoints"].items():
        for method, result in methods.items():
            if not result["success"]:
                code = result["status_code"]
                if code not in failures_by_code:
                    failures_by_code[code] = []
                failures_by_code[code].append(f"{method} {endpoint}")
    
    if failures_by_code:
        print(f"\n{Colors.BOLD}Failures by status code:{Colors.ENDC}")
        for code, endpoints in failures_by_code.items():
            print(f"  {Colors.RED}{code}:{Colors.ENDC} {', '.join(endpoints)}")

def main() -> None:
    """Main function to run all API endpoint tests."""
    print(f"{Colors.BLUE}{Colors.BOLD}AI Assistant API Endpoint Test Tool{Colors.ENDC}")
    print(f"{Colors.BLUE}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.ENDC}\n")
    
    # Ensure API is available before running tests
    try:
        requests.get(f"{CONFIG['api_base_url']}/api/health", timeout=5)
    except requests.RequestException:
        print(f"{Colors.RED}API server is not available at {CONFIG['api_base_url']}{Colors.ENDC}")
        print(f"{Colors.RED}Make sure the API server is running before running this test.{Colors.ENDC}")
        return
    
    try:
        # Run all tests
        test_health_endpoints()
        test_project_endpoints()
        test_file_endpoints()
        test_search_endpoints()
        test_user_prompt_endpoints()
        test_chat_endpoints()
        
        # Save results and print summary
        save_results()
        print_summary()
        
    except Exception as e:
        print(f"\n{Colors.RED}An unexpected error occurred: {str(e)}{Colors.ENDC}")
        
        # Try to save partial results
        try:
            results["error"] = str(e)
            with open(CONFIG["output_file"], 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n{Colors.CYAN}Partial results saved to {CONFIG['output_file']}{Colors.ENDC}")
        except:
            print(f"\n{Colors.RED}Failed to save partial results{Colors.ENDC}")

if __name__ == "__main__":
    main()