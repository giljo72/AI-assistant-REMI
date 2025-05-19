"""
Comprehensive diagnostic script for the AIbot application.
This script checks services, connections, and dependencies to ensure everything is properly set up.

It performs the following checks:
1. Python environment and dependencies
2. Node.js and frontend dependencies
3. PostgreSQL and pgvector extension
4. API server connectivity
5. Frontend server availability
6. File system permissions and directories
7. Database connectivity and schema
"""
import os
import sys
import subprocess
import platform
import importlib
import json
import socket
import requests
import time
import pkg_resources
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

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

# Define project directories
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
VENV_DIR = PROJECT_ROOT / "venv_nemo"

# Backend requirements (minimum versions)
BACKEND_REQUIREMENTS = {
    "fastapi": "0.100.0",
    "uvicorn": "0.22.0",
    "sqlalchemy": "2.0.0",
    "pydantic": "2.0.0",
    "python-multipart": "0.0.6",
    "psycopg2-binary": "2.9.6",
    "pgvector": "0.2.0",
    "python-dotenv": "1.0.0",
    "httpx": "0.24.1",
    "docx2txt": "0.8",
    "PyPDF2": "3.0.0"
}

# Frontend requirements (minimum versions)
FRONTEND_REQUIREMENTS = {
    "react": "18.0.0",
    "react-dom": "18.0.0",
    "@reduxjs/toolkit": "1.9.0",
    "typescript": "5.0.0",
    "vite": "4.0.0",
    "tailwindcss": "3.0.0"
}

# Service ports
API_PORT = 8000
FRONTEND_PORT = 5173

# Result collection
all_results = {
    "python": [],
    "node": [],
    "postgres": [],
    "services": [],
    "filesystem": [],
    "connectivity": []
}

def print_header(message: str) -> None:
    """Print a section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_result(category: str, test: str, result: bool, message: str = "", details: Any = None) -> None:
    """Print a test result and store it."""
    result_color = Colors.OKGREEN if result else Colors.FAIL
    result_text = "PASS" if result else "FAIL"
    
    print(f"{result_color}{result_text}{Colors.ENDC} - {test}")
    if message:
        print(f"     {message}")
    
    # Store result for summary
    all_results[category].append({
        "test": test,
        "result": result,
        "message": message,
        "details": details
    })

def run_command(command: List[str], cwd: Optional[Path] = None) -> Tuple[bool, str, str]:
    """Run a command and return success status, stdout, and stderr."""
    try:
        process = subprocess.run(
            command, 
            cwd=str(cwd) if cwd else None,
            check=False,
            capture_output=True,
            text=True
        )
        return (process.returncode == 0, process.stdout, process.stderr)
    except Exception as e:
        return (False, "", str(e))

def check_python_environment() -> None:
    """Check Python version and virtual environment."""
    print_header("Python Environment Check")
    
    # Check Python version
    python_version = platform.python_version()
    python_version_ok = tuple(map(int, python_version.split("."))) >= (3, 10)
    print_result(
        "python", 
        "Python version", 
        python_version_ok, 
        f"Found Python {python_version}" + ("" if python_version_ok else ", but 3.10+ is required"),
        {"version": python_version}
    )
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print_result(
        "python", 
        "Virtual environment", 
        in_venv, 
        "Running in a virtual environment" if in_venv else "Not running in a virtual environment",
        {"in_venv": in_venv}
    )
    
    # Check if the virtual environment exists
    venv_exists = VENV_DIR.exists()
    print_result(
        "python", 
        "Virtual environment directory", 
        venv_exists, 
        f"Found at {VENV_DIR}" if venv_exists else f"Not found at {VENV_DIR}",
        {"venv_path": str(VENV_DIR), "exists": venv_exists}
    )

def check_python_dependencies() -> None:
    """Check Python package dependencies."""
    print_header("Python Dependencies Check")
    
    # Get installed packages
    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    
    # Check each required package
    for package, min_version in BACKEND_REQUIREMENTS.items():
        installed_version = installed_packages.get(package)
        
        if not installed_version:
            print_result(
                "python", 
                f"Package: {package}", 
                False, 
                f"Not installed (required: {min_version}+)",
                {"required": min_version, "installed": None}
            )
            continue
        
        # Simple version comparison (not perfect but works for most cases)
        installed_parts = [int(part) for part in installed_version.split('.')]
        required_parts = [int(part) for part in min_version.split('.')]
        
        # Pad with zeros to make lengths equal
        max_length = max(len(installed_parts), len(required_parts))
        installed_parts.extend([0] * (max_length - len(installed_parts)))
        required_parts.extend([0] * (max_length - len(required_parts)))
        
        # Compare each part
        version_ok = False
        for i in range(max_length):
            if installed_parts[i] > required_parts[i]:
                version_ok = True
                break
            elif installed_parts[i] < required_parts[i]:
                version_ok = False
                break
            elif i == max_length - 1:  # All parts equal
                version_ok = True
        
        print_result(
            "python", 
            f"Package: {package}", 
            version_ok, 
            f"Installed: {installed_version}" + (f" (required: {min_version}+)" if not version_ok else ""),
            {"required": min_version, "installed": installed_version}
        )

def check_node_environment() -> None:
    """Check Node.js and npm versions."""
    print_header("Node.js Environment Check")
    
    # Check if Node.js is installed
    node_success, node_stdout, _ = run_command(["node", "--version"])
    if node_success:
        node_version = node_stdout.strip().replace('v', '')
        node_version_ok = node_version.split('.')[0] >= '18'
        print_result(
            "node", 
            "Node.js version", 
            node_version_ok, 
            f"Found Node.js {node_version}" + ("" if node_version_ok else ", but 18+ is required"),
            {"version": node_version}
        )
    else:
        print_result(
            "node", 
            "Node.js installation", 
            False, 
            "Node.js is not installed or not in PATH",
            {"installed": False}
        )
        # Skip other Node.js checks since it's not installed
        return
    
    # Check if npm is installed
    npm_success, npm_stdout, _ = run_command(["npm", "--version"])
    if npm_success:
        npm_version = npm_stdout.strip()
        print_result(
            "node", 
            "npm version", 
            True, 
            f"Found npm {npm_version}",
            {"version": npm_version}
        )
    else:
        print_result(
            "node", 
            "npm installation", 
            False, 
            "npm is not installed or not in PATH",
            {"installed": False}
        )
        # Skip other npm checks since it's not installed
        return
    
    # Check if node_modules exists in frontend directory
    node_modules_path = FRONTEND_DIR / "node_modules"
    node_modules_exists = node_modules_path.exists()
    print_result(
        "node", 
        "Frontend dependencies", 
        node_modules_exists, 
        f"node_modules found at {node_modules_path}" if node_modules_exists else f"node_modules not found at {node_modules_path}",
        {"path": str(node_modules_path), "exists": node_modules_exists}
    )
    
    # Check package.json for frontend dependencies
    package_json_path = FRONTEND_DIR / "package.json"
    if package_json_path.exists():
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            dependencies = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
            
            for package, min_version in FRONTEND_REQUIREMENTS.items():
                if package in dependencies:
                    installed_version = dependencies[package].replace('^', '').replace('~', '')
                    print_result(
                        "node", 
                        f"Frontend package: {package}", 
                        True, 
                        f"Found in package.json: {installed_version}",
                        {"required": min_version, "defined": installed_version}
                    )
                else:
                    print_result(
                        "node", 
                        f"Frontend package: {package}", 
                        False, 
                        f"Not found in package.json (required: {min_version}+)",
                        {"required": min_version, "defined": None}
                    )
        except Exception as e:
            print_result(
                "node", 
                "package.json parsing", 
                False, 
                f"Error parsing package.json: {str(e)}",
                {"error": str(e)}
            )
    else:
        print_result(
            "node", 
            "package.json", 
            False, 
            f"Not found at {package_json_path}",
            {"path": str(package_json_path), "exists": False}
        )

def check_postgres() -> None:
    """Check PostgreSQL connection and pgvector extension."""
    print_header("PostgreSQL Check")
    
    try:
        import psycopg2
        from psycopg2 import sql
        
        # Try to read connection info from .env file
        env_file = BACKEND_DIR / ".env"
        db_params = {}
        
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            if key == "DATABASE_URL":
                                # Parse DATABASE_URL
                                # Format: postgresql://username:password@host:port/dbname
                                value = value.replace('postgresql://', '')
                                user_pass, host_port_db = value.split('@', 1)
                                if ':' in user_pass:
                                    user, password = user_pass.split(':', 1)
                                else:
                                    user, password = user_pass, ""
                                
                                if '/' in host_port_db:
                                    host_port, dbname = host_port_db.split('/', 1)
                                else:
                                    host_port, dbname = host_port_db, "postgres"
                                
                                if ':' in host_port:
                                    host, port = host_port.split(':', 1)
                                else:
                                    host, port = host_port, "5432"
                                
                                db_params = {
                                    "dbname": dbname,
                                    "user": user,
                                    "password": password,
                                    "host": host,
                                    "port": port
                                }
                
                print_result(
                    "postgres", 
                    "Database configuration", 
                    bool(db_params), 
                    f"Found in .env file: {db_params}" if db_params else "Not found in .env file",
                    {"params": {k: ('*' * len(v) if k == 'password' else v) for k, v in db_params.items()}}
                )
            except Exception as e:
                print_result(
                    "postgres", 
                    "Parse .env file", 
                    False, 
                    f"Error parsing .env file: {str(e)}",
                    {"error": str(e)}
                )
        else:
            print_result(
                "postgres", 
                ".env file", 
                False, 
                f"Not found at {env_file}",
                {"path": str(env_file), "exists": False}
            )
            
            # Use default connection parameters for testing
            db_params = {
                "dbname": "aibot",
                "user": "postgres",
                "password": "",
                "host": "localhost",
                "port": "5432"
            }
            
            print("Using default database parameters for testing:")
            print(f"  Host: {db_params['host']}")
            print(f"  Port: {db_params['port']}")
            print(f"  Database: {db_params['dbname']}")
            print(f"  User: {db_params['user']}")
                
        # Try to connect to PostgreSQL
        try:
            conn = psycopg2.connect(**db_params)
            conn.autocommit = True
            cursor = conn.cursor()
            
            print_result(
                "postgres", 
                "Database connection", 
                True, 
                f"Connected to {db_params['dbname']} on {db_params['host']}:{db_params['port']}",
                {"connected": True}
            )
            
            # Check pgvector extension
            cursor.execute("SELECT count(*) FROM pg_extension WHERE extname = 'vector';")
            has_vector = cursor.fetchone()[0] > 0
            
            print_result(
                "postgres", 
                "pgvector extension", 
                has_vector, 
                "Installed" if has_vector else "Not installed",
                {"installed": has_vector}
            )
            
            # Check database tables
            expected_tables = ["documents", "projects", "document_chunks", "chats", "messages", "project_documents", "user_prompts"]
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in expected_tables:
                table_exists = table in tables
                print_result(
                    "postgres", 
                    f"Table: {table}", 
                    table_exists, 
                    "Found" if table_exists else "Not found",
                    {"exists": table_exists}
                )
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print_result(
                "postgres", 
                "Database connection", 
                False, 
                f"Failed to connect: {str(e)}",
                {"error": str(e)}
            )
    
    except ImportError:
        print_result(
            "postgres", 
            "psycopg2 library", 
            False, 
            "psycopg2 is not installed",
            {"installed": False}
        )

def check_services() -> None:
    """Check if required services are running."""
    print_header("Services Check")
    
    # Check API server
    api_running = False
    try:
        response = requests.get(f"http://localhost:{API_PORT}/health", timeout=2)
        api_running = response.status_code == 200
        api_info = response.json() if api_running else {}
        
        print_result(
            "services", 
            "API server", 
            api_running, 
            f"Running on port {API_PORT}" if api_running else f"Not running on port {API_PORT}",
            {"running": api_running, "response": api_info}
        )
    except requests.RequestException:
        print_result(
            "services", 
            "API server", 
            False, 
            f"Not responding on port {API_PORT}",
            {"running": False}
        )
    
    # Check frontend server
    frontend_running = False
    try:
        response = requests.get(f"http://localhost:{FRONTEND_PORT}", timeout=2)
        frontend_running = response.status_code == 200
        
        print_result(
            "services", 
            "Frontend server", 
            frontend_running, 
            f"Running on port {FRONTEND_PORT}" if frontend_running else f"Not running on port {FRONTEND_PORT}",
            {"running": frontend_running}
        )
    except requests.RequestException:
        print_result(
            "services", 
            "Frontend server", 
            False, 
            f"Not responding on port {FRONTEND_PORT}",
            {"running": False}
        )

def check_filesystem() -> None:
    """Check file system directories and permissions."""
    print_header("File System Check")
    
    # Check data directories
    data_dirs = [
        BACKEND_DIR / "data" / "uploads",
        BACKEND_DIR / "data" / "processed",
        BACKEND_DIR / "data" / "hierarchy",
        BACKEND_DIR / "data" / "logs"
    ]
    
    for dir_path in data_dirs:
        dir_exists = dir_path.exists()
        
        if dir_exists:
            # Check if directory is writable
            write_test_path = dir_path / "writetest.tmp"
            writable = False
            
            try:
                with open(write_test_path, 'w') as f:
                    f.write("test")
                writable = True
                os.remove(write_test_path)
            except Exception:
                writable = False
            
            print_result(
                "filesystem", 
                f"Directory: {dir_path.relative_to(PROJECT_ROOT)}", 
                writable, 
                "Exists and writable" if writable else "Exists but not writable",
                {"exists": True, "writable": writable}
            )
        else:
            print_result(
                "filesystem", 
                f"Directory: {dir_path.relative_to(PROJECT_ROOT)}", 
                False, 
                "Does not exist",
                {"exists": False}
            )

def check_connectivity() -> None:
    """Check connectivity between components."""
    print_header("Connectivity Check")
    
    # Only check connectivity if both services are running
    api_running = False
    try:
        response = requests.get(f"http://localhost:{API_PORT}/health", timeout=2)
        api_running = response.status_code == 200
    except:
        pass
    
    if not api_running:
        print_result(
            "connectivity", 
            "API to database", 
            False, 
            "API server not running, skipping connectivity check",
            {"skipped": True}
        )
        return
        
    # Check API server can connect to database
    try:
        response = requests.get(f"http://localhost:{API_PORT}/api/test/db-check", timeout=2)
        db_connected = response.status_code == 200
        
        print_result(
            "connectivity", 
            "API to database", 
            db_connected, 
            "API server can connect to database" if db_connected else "API server cannot connect to database",
            {"connected": db_connected, "response": response.json() if db_connected else {}}
        )
    except requests.RequestException:
        print_result(
            "connectivity", 
            "API to database", 
            False, 
            "Failed to check API-database connectivity",
            {"error": "Request failed"}
        )
    
    # Check if file upload works end-to-end
    try:
        test_file_path = PROJECT_ROOT / "test_upload.txt"
        with open(test_file_path, 'w') as f:
            f.write("This is a test file for upload.\nIt contains some text content.\n")
        
        files = {"file": open(test_file_path, 'rb')}
        data = {"name": "Test Upload", "description": "A test file"}
        
        response = requests.post(f"http://localhost:{API_PORT}/api/files/upload", files=files, data=data)
        upload_works = response.status_code == 200
        
        # Close and remove the file
        files["file"].close()
        os.remove(test_file_path)
        
        print_result(
            "connectivity", 
            "File upload", 
            upload_works, 
            "File upload works end-to-end" if upload_works else f"File upload failed: {response.text}",
            {"works": upload_works, "response": response.json() if upload_works else {}}
        )
    except Exception as e:
        print_result(
            "connectivity", 
            "File upload", 
            False, 
            f"Error testing file upload: {str(e)}",
            {"error": str(e)}
        )

def print_summary() -> None:
    """Print a summary of all test results."""
    print_header("Diagnostic Summary")
    
    # Count passed and failed tests for each category
    summary = {}
    all_passed = True
    
    for category, results in all_results.items():
        passed = sum(1 for r in results if r["result"])
        failed = sum(1 for r in results if not r["result"])
        success_rate = passed / (passed + failed) * 100 if passed + failed > 0 else 0
        
        summary[category] = {
            "passed": passed,
            "failed": failed,
            "total": passed + failed,
            "success_rate": success_rate
        }
        
        if failed > 0:
            all_passed = False
    
    # Print summary table
    print(f"{'Category':<15} {'Passed':<8} {'Failed':<8} {'Total':<8} {'Success':<8}")
    print("-" * 50)
    
    for category, data in summary.items():
        success_color = Colors.OKGREEN if data["success_rate"] == 100 else (Colors.WARNING if data["success_rate"] >= 70 else Colors.FAIL)
        print(f"{category:<15} {data['passed']:<8} {data['failed']:<8} {data['total']:<8} {success_color}{data['success_rate']:.1f}%{Colors.ENDC}")
    
    print("\n")
    if all_passed:
        print(f"{Colors.OKGREEN}{Colors.BOLD}All tests passed! The system is properly configured.{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}Some tests failed. Please check the detailed results above.{Colors.ENDC}")
        
        # List the failed tests
        print("\nFailed tests:")
        for category, results in all_results.items():
            for result in results:
                if not result["result"]:
                    print(f"{Colors.FAIL}- {category}: {result['test']}{Colors.ENDC}")
                    if result["message"]:
                        print(f"  {result['message']}")

def save_results_to_file() -> None:
    """Save diagnostic results to a JSON file."""
    results_file = PROJECT_ROOT / "system_diagnostics.json"
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "system": {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "hostname": socket.gethostname()
        },
        "results": all_results
    }
    
    with open(results_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")

def main() -> None:
    """Main function to run all checks."""
    print(f"{Colors.BOLD}AIbot System Diagnostics{Colors.ENDC}")
    print(f"Running diagnostics on {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project root: {PROJECT_ROOT}")
    
    # Run all checks
    check_python_environment()
    check_python_dependencies()
    check_node_environment()
    check_postgres()
    check_services()
    check_filesystem()
    check_connectivity()
    
    # Print summary
    print_summary()
    
    # Save results to file
    save_results_to_file()

if __name__ == "__main__":
    main()