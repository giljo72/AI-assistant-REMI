#!/usr/bin/env python3
"""
This script runs the FastAPI server and then executes the file project linking tests.
It will:
1. Start the FastAPI server in the background
2. Wait for it to be ready
3. Run the test_file_project_linking.py script
4. Shut down the server
"""

import os
import sys
import subprocess
import time
import signal
import requests

# Configuration
API_BASE_URL = "http://localhost:8000"
SERVER_STARTUP_TIMEOUT = 45  # seconds

def wait_for_server(timeout=SERVER_STARTUP_TIMEOUT):
    """Wait for the server to be ready to accept connections"""
    print(f"Waiting for server to start (timeout: {timeout}s)...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Try multiple health endpoints to see which one responds
            for health_path in ["/api/health", "/health", "/api/health/ping"]:
                try:
                    response = requests.get(f"{API_BASE_URL}{health_path}")
                    if response.status_code == 200:
                        print(f"\nServer is up and running! (Health endpoint: {health_path})")
                        return True
                except:
                    pass
        except requests.ConnectionError:
            pass
            
        # Wait a bit before retrying
        time.sleep(0.5)
        sys.stdout.write(".")
        sys.stdout.flush()
    
    print("\nServer startup timed out!")
    return False

def run_tests():
    """Run the file linking test script"""
    print("\nRunning file linking tests...")
    test_script = os.path.join(os.path.dirname(__file__), "test_file_project_linking.py")
    
    result = subprocess.run([sys.executable, test_script], capture_output=False)
    return result.returncode == 0

def main():
    # Start the server
    print("Starting FastAPI server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
        cwd=os.path.dirname(__file__),
        # Show server output for debugging
        stdout=None,
        stderr=None,
    )
    
    try:
        # Wait for server to be ready
        if not wait_for_server():
            print("Failed to start server within timeout period.")
            server_process.terminate()
            return 1
        
        # Run tests
        test_success = run_tests()
        
        if test_success:
            print("\nTests completed successfully!")
            return 0
        else:
            print("\nTests failed!")
            return 1
            
    finally:
        # Clean up - make sure to terminate the server
        print("\nShutting down server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Server didn't terminate gracefully, forcing...")
            server_process.kill()
        
        print("Server shutdown complete.")

if __name__ == "__main__":
    sys.exit(main())