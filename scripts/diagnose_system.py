#!/usr/bin/env python
"""
Comprehensive system diagnostic script for the AI Assistant.
Checks all dependencies, services, and connections.
Can run autonomously or be integrated into the application.
"""

import os
import sys
import platform
import subprocess
import json
import socket
import requests
from datetime import datetime
import importlib.util
import pkg_resources
from typing import Dict, List, Tuple, Any, Optional, Union, Callable

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
    "frontend_url": "http://localhost:5173",
    "database": {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "database": "assistant_db",
    },
    "required_python_packages": [
        "fastapi>=0.95.0",
        "uvicorn>=0.21.1",
        "sqlalchemy>=2.0.0",
        "pydantic>=1.10.7",
        "python-multipart>=0.0.6",
        "psycopg2-binary>=2.9.6",
        "python-dotenv>=1.0.0",
        "langchain>=0.0.200",
        "llama-index>=0.6.0",
        "pypdf>=3.8.1",
        "docx2txt>=0.8"
    ],
    "required_node_packages": [
        "react",
        "react-dom",
        "typescript",
        "tailwindcss",
        "@reduxjs/toolkit",
        "axios"
    ],
    "venv_name": "venv_nemo",
    "output_file": "diagnostic_results.json"
}

# Results storage
results = {
    "timestamp": datetime.now().isoformat(),
    "system_info": {},
    "python_environment": {},
    "node_environment": {},
    "database": {},
    "api_server": {},
    "frontend": {},
    "file_system": {},
    "services": {},
    "overall_status": "pending"
}

def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 50}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD} {title} {Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 50}{Colors.ENDC}")

def print_result(component: str, check: str, success: bool, details: Any, extra_info: Optional[Dict] = None) -> None:
    """Print a formatted result and store it in the results dictionary."""
    status = f"{Colors.GREEN}✓ PASS{Colors.ENDC}" if success else f"{Colors.RED}✗ FAIL{Colors.ENDC}"
    print(f"{Colors.BOLD}{component}:{Colors.ENDC} {check} - {status}")
    print(f"  {details}")
    
    # Store result
    category = component.split('.')[0] if '.' in component else "misc"
    if category not in results:
        results[category] = {}
    
    results[category][check] = {
        "success": success,
        "details": str(details) if not isinstance(details, (dict, list)) else details,
    }
    
    if extra_info:
        results[category][check]["extra_info"] = extra_info

def run_command(command: List[str]) -> Tuple[bool, str, int]:
    """Run a shell command and return success status, output, and return code."""
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.returncode == 0, result.stdout.strip(), result.returncode
    except Exception as e:
        return False, str(e), -1

def check_system_info() -> None:
    """Gather basic system information."""
    print_header("System Information")
    
    # Operating system
    os_name = platform.system()
    os_version = platform.version()
    print_result(
        "system", 
        "Operating System", 
        True, 
        f"{os_name} {os_version}",
        {"os": os_name, "version": os_version}
    )
    
    # CPU
    if os_name == "Windows":
        success, cpu_info, _ = run_command(["wmic", "cpu", "get", "name"])
        if success:
            cpu_info = cpu_info.split("\n")[1].strip()
    else:
        success, cpu_info, _ = run_command(["cat", "/proc/cpuinfo"])
        if success:
            for line in cpu_info.split("\n"):
                if "model name" in line:
                    cpu_info = line.split(":")[1].strip()
                    break
    
    print_result(
        "system", 
        "CPU", 
        success, 
        cpu_info if success else "Could not determine CPU info",
        {"cpu": cpu_info if success else "unknown"}
    )
    
    # Memory
    if os_name == "Windows":
        success, mem_info, _ = run_command(["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize"])
        if success:
            lines = mem_info.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 2:
                    total_mem = int(parts[1]) // 1024  # Convert KB to MB
                    free_mem = int(parts[0]) // 1024   # Convert KB to MB
                    mem_info = f"Total: {total_mem} MB, Free: {free_mem} MB"
    else:
        success, mem_info, _ = run_command(["free", "-m"])
        if success:
            lines = mem_info.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 7:
                    total_mem = parts[1]
                    free_mem = parts[3]
                    mem_info = f"Total: {total_mem} MB, Free: {free_mem} MB"
    
    print_result(
        "system", 
        "Memory", 
        success, 
        mem_info if success else "Could not determine memory info",
        {"memory": mem_info if success else "unknown"}
    )
    
    # GPU
    if os_name == "Windows":
        success, gpu_info, _ = run_command(["wmic", "path", "win32_VideoController", "get", "name"])
        if success:
            gpu_info = gpu_info.split('\n')[1].strip()
    else:
        success, gpu_info, _ = run_command(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
        if not success:
            success, gpu_info, _ = run_command(["lspci", "|", "grep", "-i", "vga"])
    
    print_result(
        "system", 
        "GPU", 
        success, 
        gpu_info if success else "Could not determine GPU info",
        {"gpu": gpu_info if success else "unknown"}
    )
    
    # CUDA
    success, cuda_info, _ = run_command(["nvcc", "--version"])
    if not success:
        cuda_info = "CUDA not found or not in PATH"
    
    print_result(
        "system", 
        "CUDA", 
        success, 
        cuda_info,
        {"cuda": cuda_info if success else "not found"}
    )
    
    # Store system info
    results["system_info"] = {
        "os": f"{os_name} {os_version}",
        "cpu": cpu_info if success else "unknown",
        "memory": mem_info if success else "unknown",
        "gpu": gpu_info if success else "unknown",
        "cuda": cuda_info if success else "not found"
    }

def check_python_environment() -> None:
    """Check Python version and dependencies."""
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
    
    # Check virtual environment
    in_venv = sys.prefix != sys.base_prefix
    venv_path = sys.prefix
    print_result(
        "python", 
        "Virtual environment", 
        in_venv, 
        f"Using virtual environment at {venv_path}" if in_venv else "Not running in a virtual environment",
        {"in_venv": in_venv, "venv_path": venv_path if in_venv else None}
    )
    
    # Check if it's the expected venv
    expected_venv = CONFIG["venv_name"]
    correct_venv = expected_venv in venv_path if in_venv else False
    print_result(
        "python", 
        "Correct virtual environment", 
        correct_venv, 
        f"Using expected venv '{expected_venv}'" if correct_venv else f"Not using expected venv '{expected_venv}'",
        {"expected_venv": expected_venv, "correct_venv": correct_venv}
    )
    
    # Check required packages
    missing_packages = []
    outdated_packages = []
    
    for package_req in CONFIG["required_python_packages"]:
        package_name, required_version = package_req.split(">=") if ">=" in package_req else (package_req, None)
        
        try:
            package = pkg_resources.get_distribution(package_name)
            if required_version and pkg_resources.parse_version(package.version) < pkg_resources.parse_version(required_version):
                outdated_packages.append((package_name, package.version, required_version))
        except pkg_resources.DistributionNotFound:
            missing_packages.append(package_name)
    
    # Report missing packages
    print_result(
        "python", 
        "Required packages", 
        not missing_packages, 
        f"All required packages installed" if not missing_packages else f"Missing packages: {', '.join(missing_packages)}",
        {"missing_packages": missing_packages}
    )
    
    # Report outdated packages
    print_result(
        "python", 
        "Package versions", 
        not outdated_packages, 
        f"All packages meet version requirements" if not outdated_packages else 
        f"Outdated packages: {', '.join([f'{p[0]} (found: {p[1]}, required: {p[2]})' for p in outdated_packages])}",
        {"outdated_packages": [{"name": p[0], "found": p[1], "required": p[2]} for p in outdated_packages]}
    )
    
    # Store Python environment info
    results["python_environment"] = {
        "version": python_version,
        "version_ok": python_version_ok,
        "in_venv": in_venv,
        "venv_path": venv_path if in_venv else None,
        "correct_venv": correct_venv,
        "missing_packages": missing_packages,
        "outdated_packages": [{"name": p[0], "found": p[1], "required": p[2]} for p in outdated_packages]
    }

def check_node_environment() -> None:
    """Check Node.js and npm."""
    print_header("Node.js Environment Check")
    
    # Check Node.js version
    success, node_version, _ = run_command(["node", "-v"])
    node_version = node_version.strip("v") if success else "Not found"
    node_version_ok = success and tuple(map(int, node_version.split("."))) >= (18, 0)
    
    print_result(
        "node", 
        "Node.js version", 
        node_version_ok, 
        f"Found Node.js {node_version}" + ("" if node_version_ok else ", but 18.0+ is required"),
        {"version": node_version}
    )
    
    # Check npm version
    success, npm_version, _ = run_command(["npm", "-v"])
    npm_version_ok = success
    
    print_result(
        "node", 
        "npm version", 
        npm_version_ok, 
        f"Found npm {npm_version}" if npm_version_ok else "npm not found",
        {"version": npm_version if npm_version_ok else None}
    )
    
    # Check if frontend directory exists
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
    frontend_dir_exists = os.path.isdir(frontend_dir)
    
    print_result(
        "node", 
        "Frontend directory", 
        frontend_dir_exists, 
        f"Frontend directory found at {frontend_dir}" if frontend_dir_exists else "Frontend directory not found",
        {"path": frontend_dir if frontend_dir_exists else None}
    )
    
    # Check for package.json
    package_json_path = os.path.join(frontend_dir, "package.json") if frontend_dir_exists else None
    package_json_exists = package_json_path and os.path.isfile(package_json_path)
    
    print_result(
        "node", 
        "package.json", 
        package_json_exists, 
        f"package.json found at {package_json_path}" if package_json_exists else "package.json not found",
        {"path": package_json_path if package_json_exists else None}
    )
    
    # Check required packages in package.json
    missing_npm_packages = []
    
    if package_json_exists:
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
                
            installed_packages = {}
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in package_data:
                    installed_packages.update(package_data[dep_type])
            
            for package in CONFIG["required_node_packages"]:
                if package not in installed_packages:
                    missing_npm_packages.append(package)
        except Exception as e:
            print_result(
                "node", 
                "package.json parse", 
                False, 
                f"Error parsing package.json: {str(e)}",
                {"error": str(e)}
            )
    
    print_result(
        "node", 
        "Required npm packages", 
        not missing_npm_packages, 
        f"All required npm packages found in package.json" if not missing_npm_packages else 
        f"Missing npm packages: {', '.join(missing_npm_packages)}",
        {"missing_packages": missing_npm_packages}
    )
    
    # Check if node_modules directory exists
    node_modules_path = os.path.join(frontend_dir, "node_modules") if frontend_dir_exists else None
    node_modules_exists = node_modules_path and os.path.isdir(node_modules_path)
    
    print_result(
        "node", 
        "node_modules", 
        node_modules_exists, 
        f"node_modules directory found" if node_modules_exists else "node_modules directory not found",
        {"path": node_modules_path if node_modules_exists else None}
    )
    
    # Store Node.js environment info
    results["node_environment"] = {
        "node_version": node_version,
        "node_version_ok": node_version_ok,
        "npm_version": npm_version if npm_version_ok else None,
        "frontend_dir": frontend_dir if frontend_dir_exists else None,
        "package_json": package_json_path if package_json_exists else None,
        "missing_packages": missing_npm_packages,
        "node_modules": node_modules_path if node_modules_exists else None
    }

def check_database() -> None:
    """Check PostgreSQL database connection and pgvector extension."""
    print_header("Database Check")
    
    # Check if psycopg2 is installed
    psycopg2_installed = importlib.util.find_spec("psycopg2") is not None
    print_result(
        "database", 
        "psycopg2 module", 
        psycopg2_installed, 
        "psycopg2 module is installed" if psycopg2_installed else "psycopg2 module is not installed",
        {"installed": psycopg2_installed}
    )
    
    if not psycopg2_installed:
        print_result(
            "database", 
            "Database connection", 
            False, 
            "Cannot check database connection without psycopg2",
            {"error": "psycopg2 not installed"}
        )
        return
    
    # Import psycopg2 dynamically
    import psycopg2
    
    # Try to connect to the database
    db_config = CONFIG["database"]
    try:
        conn = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["user"],
            database=db_config["database"]
        )
        cursor = conn.cursor()
        
        # Check connection
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        print_result(
            "database", 
            "PostgreSQL connection", 
            True, 
            f"Connected to {db_version}",
            {"version": db_version}
        )
        
        # Check pgvector extension
        cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector';")
        pgvector_installed = cursor.fetchone() is not None
        print_result(
            "database", 
            "pgvector extension", 
            pgvector_installed, 
            "pgvector extension is installed" if pgvector_installed else "pgvector extension is not installed",
            {"installed": pgvector_installed}
        )
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = ["document", "project", "chat", "user_prompt"]
        missing_tables = [table for table in required_tables if table not in tables]
        
        print_result(
            "database", 
            "Required tables", 
            not missing_tables, 
            f"All required tables exist ({', '.join(required_tables)})" if not missing_tables else 
            f"Missing tables: {', '.join(missing_tables)}",
            {"tables": tables, "missing_tables": missing_tables}
        )
        
        # Close connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print_result(
            "database", 
            "PostgreSQL connection", 
            False, 
            f"Failed to connect to database: {str(e)}",
            {"error": str(e)}
        )
        
        # Mark subsequent checks as failed
        print_result(
            "database", 
            "pgvector extension", 
            False, 
            "Could not check pgvector extension (connection failed)",
            {"error": "connection failed"}
        )
        
        print_result(
            "database", 
            "Required tables", 
            False, 
            "Could not check tables (connection failed)",
            {"error": "connection failed"}
        )
    
    # Store database info
    results["database"] = {
        "psycopg2_installed": psycopg2_installed,
        "connection": {
            "success": "db_version" in locals(),
            "version": db_version if "db_version" in locals() else None,
            "error": str(e) if "e" in locals() else None
        },
        "pgvector": {
            "installed": pgvector_installed if "pgvector_installed" in locals() else None
        },
        "tables": {
            "available": tables if "tables" in locals() else None,
            "missing": missing_tables if "missing_tables" in locals() else required_tables
        }
    }

def check_api_server() -> None:
    """Check if the API server is running and responsive."""
    print_header("API Server Check")
    
    # Check if the API server is running
    api_url = CONFIG["api_base_url"]
    health_url = f"{api_url}/api/health"
    
    try:
        response = requests.get(health_url, timeout=5)
        api_running = response.status_code == 200
        api_status = response.json() if api_running else None
        
        print_result(
            "api", 
            "API server", 
            api_running, 
            f"API server is running at {api_url}" if api_running else f"API server is not responding at {api_url}",
            {"url": api_url, "status_code": response.status_code}
        )
        
    except requests.RequestException as e:
        api_running = False
        print_result(
            "api", 
            "API server", 
            False, 
            f"Failed to connect to API server: {str(e)}",
            {"url": api_url, "error": str(e)}
        )
    
    # Check if port 8000 is open
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    port_open = False
    try:
        sock.connect(('localhost', 8000))
        port_open = True
        sock.close()
    except:
        pass
    
    print_result(
        "api", 
        "Port 8000", 
        port_open, 
        "Port 8000 is open" if port_open else "Port 8000 is not open",
        {"open": port_open}
    )
    
    # Check for specific API endpoints only if the API is running
    if api_running:
        endpoints = [
            "/api/projects",
            "/api/files",
            "/api/chats",
            "/api/user-prompts",
            "/api/semantic-search"
        ]
        
        for endpoint in endpoints:
            full_url = f"{api_url}{endpoint}"
            try:
                response = requests.get(full_url, timeout=5)
                endpoint_ok = response.status_code in [200, 401, 403]  # Some endpoints might require auth
                
                print_result(
                    "api", 
                    f"Endpoint {endpoint}", 
                    endpoint_ok, 
                    f"Endpoint {endpoint} is responding (status {response.status_code})" if endpoint_ok else 
                    f"Endpoint {endpoint} is not responding properly (status {response.status_code})",
                    {"url": full_url, "status_code": response.status_code}
                )
                
            except requests.RequestException as e:
                print_result(
                    "api", 
                    f"Endpoint {endpoint}", 
                    False, 
                    f"Failed to connect to endpoint {endpoint}: {str(e)}",
                    {"url": full_url, "error": str(e)}
                )
    
    # Store API server info
    results["api_server"] = {
        "running": api_running,
        "url": api_url,
        "port_open": port_open,
        "status": api_status if "api_status" in locals() and api_status else None,
        "error": str(e) if "e" in locals() else None
    }

def check_frontend() -> None:
    """Check if the frontend is running."""
    print_header("Frontend Check")
    
    # Check if the frontend server is running
    frontend_url = CONFIG["frontend_url"]
    
    try:
        response = requests.get(frontend_url, timeout=5)
        frontend_running = response.status_code == 200
        
        print_result(
            "frontend", 
            "Frontend server", 
            frontend_running, 
            f"Frontend server is running at {frontend_url}" if frontend_running else 
            f"Frontend server is not responding at {frontend_url} (status {response.status_code})",
            {"url": frontend_url, "status_code": response.status_code}
        )
        
    except requests.RequestException as e:
        frontend_running = False
        print_result(
            "frontend", 
            "Frontend server", 
            False, 
            f"Failed to connect to frontend server: {str(e)}",
            {"url": frontend_url, "error": str(e)}
        )
    
    # Check if port 5173 is open
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    port_open = False
    try:
        sock.connect(('localhost', 5173))
        port_open = True
        sock.close()
    except:
        pass
    
    print_result(
        "frontend", 
        "Port 5173", 
        port_open, 
        "Port 5173 is open" if port_open else "Port 5173 is not open",
        {"open": port_open}
    )
    
    # Check if production build exists
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
    dist_dir = os.path.join(frontend_dir, "dist")
    build_exists = os.path.isdir(dist_dir)
    
    print_result(
        "frontend", 
        "Production build", 
        build_exists, 
        f"Production build found at {dist_dir}" if build_exists else "Production build not found",
        {"path": dist_dir if build_exists else None}
    )
    
    # Store frontend info
    results["frontend"] = {
        "running": frontend_running,
        "url": frontend_url,
        "port_open": port_open,
        "build_exists": build_exists,
        "build_path": dist_dir if build_exists else None,
        "error": str(e) if "e" in locals() and not frontend_running else None
    }

def check_file_system() -> None:
    """Check file system permissions and directories."""
    print_header("File System Check")
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if important directories exist
    directories = {
        "backend": os.path.join(project_root, "backend"),
        "frontend": os.path.join(project_root, "frontend"),
        "data": os.path.join(project_root, "backend", "data"),
        "uploads": os.path.join(project_root, "backend", "data", "uploads"),
        "processed": os.path.join(project_root, "backend", "data", "processed"),
        "hierarchy": os.path.join(project_root, "backend", "data", "hierarchy"),
        "logs": os.path.join(project_root, "backend", "data", "logs")
    }
    
    for dir_name, dir_path in directories.items():
        dir_exists = os.path.isdir(dir_path)
        print_result(
            "filesystem", 
            f"{dir_name} directory", 
            dir_exists, 
            f"{dir_name} directory exists at {dir_path}" if dir_exists else f"{dir_name} directory not found",
            {"path": dir_path, "exists": dir_exists}
        )
        
        if dir_exists:
            # Check write permissions
            writable = os.access(dir_path, os.W_OK)
            print_result(
                "filesystem", 
                f"{dir_name} write access", 
                writable, 
                f"{dir_name} directory is writable" if writable else f"{dir_name} directory is not writable",
                {"writable": writable}
            )
    
    # Check for config files
    config_files = {
        "frontend package.json": os.path.join(project_root, "frontend", "package.json"),
        "backend requirements.txt": os.path.join(project_root, "backend", "requirements.txt"),
        "README": os.path.join(project_root, "Readme.MD")
    }
    
    for file_name, file_path in config_files.items():
        file_exists = os.path.isfile(file_path)
        print_result(
            "filesystem", 
            f"{file_name}", 
            file_exists, 
            f"{file_name} exists at {file_path}" if file_exists else f"{file_name} not found",
            {"path": file_path, "exists": file_exists}
        )
    
    # Check disk space
    try:
        if platform.system() == "Windows":
            success, output, _ = run_command(["wmic", "logicaldisk", "get", "deviceid,freespace,size"])
            disk_info = "Could not determine disk space"
            
            if success:
                disks = []
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) >= 3:
                            try:
                                free_space_gb = round(int(parts[1]) / (1024**3), 2)
                                total_space_gb = round(int(parts[2]) / (1024**3), 2)
                                disks.append(f"{parts[0]} {free_space_gb}GB free of {total_space_gb}GB")
                            except (ValueError, IndexError):
                                continue
                
                if disks:
                    disk_info = ", ".join(disks)
        else:
            success, output, _ = run_command(["df", "-h", project_root])
            
            if success:
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    disk_info = lines[1]
            else:
                disk_info = "Could not determine disk space"
        
        print_result(
            "filesystem", 
            "Disk space", 
            success, 
            disk_info,
            {"disk_info": disk_info}
        )
        
    except Exception as e:
        print_result(
            "filesystem", 
            "Disk space", 
            False, 
            f"Error checking disk space: {str(e)}",
            {"error": str(e)}
        )
    
    # Store file system info
    results["file_system"] = {
        "directories": {name: {"path": path, "exists": os.path.isdir(path), 
                              "writable": os.access(path, os.W_OK) if os.path.isdir(path) else False} 
                      for name, path in directories.items()},
        "config_files": {name: {"path": path, "exists": os.path.isfile(path)} 
                       for name, path in config_files.items()},
        "disk_space": disk_info if "disk_info" in locals() else "Unknown"
    }

def check_running_services() -> None:
    """Check if required services are running."""
    print_header("Services Check")
    
    # Check for PostgreSQL process
    if platform.system() == "Windows":
        success, postgres_output, _ = run_command(["tasklist", "/FI", "IMAGENAME eq postgres.exe"])
        postgres_running = "postgres.exe" in postgres_output
    else:
        success, postgres_output, _ = run_command(["pgrep", "-f", "postgres"])
        postgres_running = bool(postgres_output.strip())
    
    print_result(
        "services", 
        "PostgreSQL", 
        postgres_running, 
        "PostgreSQL service is running" if postgres_running else "PostgreSQL service is not running",
        {"running": postgres_running}
    )
    
    # Check for backend API server (uvicorn/FastAPI)
    if platform.system() == "Windows":
        success, uvicorn_output, _ = run_command(["tasklist", "/FI", "IMAGENAME eq python.exe"])
        uvicorn_running = "uvicorn" in uvicorn_output or "FastAPI" in uvicorn_output or "app.main" in uvicorn_output
    else:
        success, uvicorn_output, _ = run_command(["pgrep", "-f", "uvicorn"])
        uvicorn_running = bool(uvicorn_output.strip())
    
    print_result(
        "services", 
        "Backend API (uvicorn)", 
        uvicorn_running, 
        "Backend API service is running" if uvicorn_running else "Backend API service is not running",
        {"running": uvicorn_running}
    )
    
    # Check for frontend service (npm/vite)
    if platform.system() == "Windows":
        success, npm_output, _ = run_command(["tasklist", "/FI", "IMAGENAME eq node.exe"])
        frontend_running = "npm" in npm_output or "vite" in npm_output
    else:
        success, npm_output, _ = run_command(["pgrep", "-f", "npm run dev"])
        if not success or not npm_output.strip():
            success, npm_output, _ = run_command(["pgrep", "-f", "vite"])
        frontend_running = bool(npm_output.strip())
    
    print_result(
        "services", 
        "Frontend (npm/vite)", 
        frontend_running, 
        "Frontend service is running" if frontend_running else "Frontend service is not running",
        {"running": frontend_running}
    )
    
    # Store services info
    results["services"] = {
        "postgresql": {
            "running": postgres_running
        },
        "backend_api": {
            "running": uvicorn_running
        },
        "frontend": {
            "running": frontend_running
        }
    }

def determine_overall_status() -> str:
    """Determine the overall system status based on results."""
    critical_checks = [
        ("python_environment", ["Python version", "Required packages"]),
        ("database", ["PostgreSQL connection", "pgvector extension", "Required tables"]),
        ("api_server", ["API server"]),
        ("file_system", ["uploads directory", "processed directory"])
    ]
    
    # Check if any critical checks failed
    critical_failure = False
    for category, checks in critical_checks:
        if category in results:
            for check in checks:
                if check in results[category] and isinstance(results[category][check], dict) and "success" in results[category][check]:
                    if not results[category][check]["success"]:
                        critical_failure = True
                        break
    
    # Count overall successes and failures
    total_checks = 0
    successful_checks = 0
    
    for category, category_results in results.items():
        if isinstance(category_results, dict):
            for check, check_result in category_results.items():
                if isinstance(check_result, dict) and "success" in check_result:
                    total_checks += 1
                    if check_result["success"]:
                        successful_checks += 1
    
    success_rate = successful_checks / total_checks if total_checks > 0 else 0
    
    if critical_failure:
        return "critical_failure"
    elif success_rate == 1.0:
        return "all_systems_go"
    elif success_rate >= 0.8:
        return "minor_issues"
    elif success_rate >= 0.5:
        return "significant_issues"
    else:
        return "major_issues"

def save_results() -> None:
    """Save diagnostic results to a JSON file."""
    output_file = CONFIG["output_file"]
    
    try:
        # Add overall status
        status = determine_overall_status()
        results["overall_status"] = status
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n{Colors.CYAN}Results saved to {output_file}{Colors.ENDC}")
        
        # Print summary
        print_summary(status)
        
    except Exception as e:
        print(f"\n{Colors.RED}Failed to save results: {str(e)}{Colors.ENDC}")

def print_summary(status: str) -> None:
    """Print a summary of the diagnostic results."""
    status_messages = {
        "all_systems_go": f"{Colors.GREEN}All systems operational! All checks passed successfully.{Colors.ENDC}",
        "minor_issues": f"{Colors.YELLOW}System is operational with minor issues. Most checks passed.{Colors.ENDC}",
        "significant_issues": f"{Colors.YELLOW}System has significant issues but may be partially functional.{Colors.ENDC}",
        "major_issues": f"{Colors.RED}System has major issues and is likely not functional.{Colors.ENDC}",
        "critical_failure": f"{Colors.RED}Critical failure! Core components are not working.{Colors.ENDC}"
    }
    
    print_header("Diagnostic Summary")
    print(status_messages.get(status, f"Unknown status: {status}"))
    
    # Count successes and failures by category
    category_stats = {}
    for category, category_results in results.items():
        if isinstance(category_results, dict) and category not in ["timestamp", "system_info", "overall_status"]:
            successes = 0
            failures = 0
            for check, check_result in category_results.items():
                if isinstance(check_result, dict) and "success" in check_result:
                    if check_result["success"]:
                        successes += 1
                    else:
                        failures += 1
            
            if successes + failures > 0:
                category_stats[category] = (successes, failures, successes + failures)
    
    # Print stats by category
    for category, (successes, failures, total) in category_stats.items():
        success_rate = successes / total if total > 0 else 0
        color = Colors.GREEN if success_rate == 1.0 else Colors.YELLOW if success_rate >= 0.5 else Colors.RED
        print(f"{Colors.BOLD}{category.replace('_', ' ').title()}:{Colors.ENDC} {color}{successes}/{total} checks passed ({int(success_rate * 100)}%){Colors.ENDC}")
    
    # Print recommendations based on status
    print(f"\n{Colors.BOLD}Recommendations:{Colors.ENDC}")
    
    if status == "all_systems_go":
        print("- System is fully operational. No action needed.")
    else:
        # Generate specific recommendations
        if "python_environment" in results:
            if "missing_packages" in results["python_environment"] and results["python_environment"]["missing_packages"]:
                packages = results["python_environment"]["missing_packages"]
                print(f"- Install missing Python packages: {', '.join(packages)}")
            
            if "outdated_packages" in results["python_environment"] and results["python_environment"]["outdated_packages"]:
                packages = [f"{p['name']} (>= {p['required']})" for p in results["python_environment"]["outdated_packages"]]
                print(f"- Update outdated Python packages: {', '.join(packages)}")
        
        if "database" in results and "connection" in results["database"] and not results["database"]["connection"].get("success", False):
            print("- Ensure PostgreSQL is running and properly configured.")
            
            if "pgvector" in results["database"] and not results["database"]["pgvector"].get("installed", False):
                print("- Install pgvector extension in PostgreSQL.")
        
        if "api_server" in results and "running" in results["api_server"] and not results["api_server"]["running"]:
            print("- Start the backend API server using 'uvicorn app.main:app --reload --port 8000'")
        
        if "frontend" in results and "running" in results["frontend"] and not results["frontend"]["running"]:
            print("- Start the frontend server using 'npm run dev' in the frontend directory")
        
        if "file_system" in results and "directories" in results["file_system"]:
            missing_dirs = [name for name, info in results["file_system"]["directories"].items() 
                           if not info.get("exists", False)]
            
            if missing_dirs:
                print(f"- Create missing directories: {', '.join(missing_dirs)}")
            
            non_writable_dirs = [name for name, info in results["file_system"]["directories"].items() 
                               if info.get("exists", False) and not info.get("writable", False)]
            
            if non_writable_dirs:
                print(f"- Fix permissions for non-writable directories: {', '.join(non_writable_dirs)}")

def main() -> None:
    """Main function to run all diagnostic checks."""
    print(f"{Colors.BLUE}{Colors.BOLD}AI Assistant System Diagnostic Tool{Colors.ENDC}")
    print(f"{Colors.BLUE}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.ENDC}\n")
    
    try:
        # Run all checks
        check_system_info()
        check_python_environment()
        check_node_environment()
        check_database()
        check_api_server()
        check_frontend()
        check_file_system()
        check_running_services()
        
        # Save results and print summary
        save_results()
        
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