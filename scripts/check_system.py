import os
import sys
import subprocess
import importlib
import platform
from pathlib import Path
import json
from dotenv import load_dotenv

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def print_status(component, status, message=""):
    """Print a status message with color."""
    status_str = f"[ {'✓' if status else '✗'} ] {component}"
    if message:
        status_str += f": {message}"
    print(status_str)

def check_python_version():
    """Check Python version."""
    version = platform.python_version()
    major, minor, _ = map(int, version.split('.'))
    using_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    venv_path = sys.prefix
    
    print_status("Python Version", major == 3 and minor >= 10, f"Python {version}")
    print_status("Using Virtual Environment", using_venv, f"Path: {venv_path}")
    
    return major == 3 and minor >= 10 and using_venv

def check_packages():
    """Check required packages are installed."""
    required_packages = [
        # Core packages
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("sqlalchemy", "sqlalchemy"),
        ("pydantic", "pydantic"),
        ("alembic", "alembic"),
        ("psycopg2", "psycopg2"),
        ("python-dotenv", "dotenv"),
        ("httpx", "httpx"),
        
        # Document processing
        ("pypdf", "pypdf"),
        ("docx2txt", "docx2txt"),
        ("openpyxl", "openpyxl"),
        ("markdown", "markdown"),
        ("beautifulsoup4", "bs4"),
        
        # Utilities
        ("tqdm", "tqdm"),
        ("pytest", "pytest"),
        ("tenacity", "tenacity"),
        ("loguru", "loguru"),
        
        # PyTorch
        ("torch", "torch"),
    ]
    
    # Load environment variables to check if we're using mock NeMo
    env_path = Path("backend/.env")
    use_mock_nemo = False
    if env_path.exists():
        load_dotenv(env_path)
        use_mock_nemo = os.getenv("USE_MOCK_NEMO", "false").lower() == "true"
    
    if not use_mock_nemo:
        # Only add NeMo to required packages if we're not using mock
        required_packages.append(("nemo_toolkit", "nemo"))
    
    missing = []
    issues = []
    
    for package_name, import_name in required_packages:
        try:
            # Try to import the package
            importlib.import_module(import_name)
            print_status(package_name, True)
        except ImportError:
            missing.append(package_name)
            print_status(package_name, False, "Not installed")
        except Exception as e:
            issues.append((package_name, str(e)))
            print_status(package_name, False, f"Error: {str(e)}")
    
    # Check for mock NeMo if we're using it
    if use_mock_nemo:
        try:
            # Add the project root to the path to allow imports
            sys.path.append(os.getcwd())
            from backend.app.core.mock_nemo import load_model
            print_status("mock_nemo", True, "Mock NeMo implementation found")
        except ImportError:
            missing.append("mock_nemo")
            print_status("mock_nemo", False, "Mock NeMo implementation not found")
        except Exception as e:
            issues.append(("mock_nemo", str(e)))
            print_status("mock_nemo", False, f"Error: {str(e)}")
    
    if missing or issues:
        print("\nMissing packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        if issues:
            print("\nPackage issues:")
            for pkg, issue in issues:
                print(f"  - {pkg}: {issue}")
    
    return len(missing) == 0 and len(issues) == 0

def check_pytorch_cuda():
    """Check if PyTorch is using CUDA."""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        device_count = torch.cuda.device_count() if cuda_available else 0
        cuda_version = torch.version.cuda if cuda_available else "N/A"
        
        status = cuda_available and device_count > 0
        
        print_status("PyTorch CUDA Support", status, f"Devices: {device_count}, CUDA: {cuda_version}")
        
        if status:
            print("\nGPU Information:")
            for i in range(device_count):
                gpu_name = torch.cuda.get_device_name(i)
                print(f"  GPU {i}: {gpu_name}")
        
        return status
    except Exception as e:
        print_status("PyTorch CUDA Support", False, f"Error: {str(e)}")
        return False

def check_database():
    """Check PostgreSQL database connection."""
    try:
        # Check if psql is in PATH
        subprocess.run(["psql", "--version"], check=True, capture_output=True, text=True, shell=True)
        print_status("PostgreSQL Client", True, "psql found in PATH")
        
        # Load database connection from .env if it exists
        db_url = None
        env_path = Path("backend/.env")
        if env_path.exists():
            load_dotenv(env_path)
            db_url = os.getenv("DATABASE_URL")
        
        # Check database connection
        if db_url:
            # Extract credentials from the database URL
            # Format: postgresql://username:password@localhost/dbname
            db_conn_parts = db_url.replace("postgresql://", "").split("@")
            user_pass = db_conn_parts[0].split(":")
            username = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            
            host_db = db_conn_parts[1].split("/")
            host = host_db[0]
            dbname = host_db[1]
            
            # Set PGPASSWORD environment variable
            os.environ["PGPASSWORD"] = password
            
            # Check if database exists
            result = subprocess.run(
                ["psql", "-U", username, "-h", host, "-t", "-c", 
                 f"SELECT 1 FROM pg_database WHERE datname='{dbname}'"],
                check=True, capture_output=True, text=True, shell=True
            )
            db_exists = "1" in result.stdout
            
            print_status("Database Connection", db_exists, f"Database: {dbname}")
            
            # Check if pgvector extension is available
            try:
                result = subprocess.run(
                    ["psql", "-U", username, "-h", host, "-d", dbname, "-t", "-c", 
                     "SELECT 1 FROM pg_available_extensions WHERE name='vector'"],
                    check=True, capture_output=True, text=True, shell=True
                )
                pgvector_available = "1" in result.stdout
                
                # If available, check if it's installed in the database
                if pgvector_available:
                    result = subprocess.run(
                        ["psql", "-U", username, "-h", host, "-d", dbname, "-t", "-c", 
                         "SELECT 1 FROM pg_extension WHERE extname='vector'"],
                        check=True, capture_output=True, text=True, shell=True
                    )
                    pgvector_installed = "1" in result.stdout
                    
                    if pgvector_installed:
                        print_status("pgvector Extension", True, "Installed in database")
                    else:
                        print_status("pgvector Extension", False, "Available but not installed in database")
                else:
                    print_status("pgvector Extension", False, "Not available")
            except Exception as e:
                print_status("pgvector Extension", False, f"Error: {str(e)}")
            
            # Clear password from environment
            os.environ.pop("PGPASSWORD", None)
            
            return db_exists
        else:
            print_status("Database Configuration", False, "No DATABASE_URL found in .env file")
            return False
            
    except Exception as e:
        print_status("PostgreSQL Database", False, f"Error: {str(e)}")
        return False

def check_nemo_configuration():
    """Check NeMo configuration."""
    # Load environment variables
    env_path = Path("backend/.env")
    if env_path.exists():
        load_dotenv(env_path)
    
    use_mock_nemo = os.getenv("USE_MOCK_NEMO", "false").lower() == "true"
    
    if use_mock_nemo:
        try:
            # Check if mock NeMo module exists
            sys.path.append(os.getcwd())  # Add current directory to path
            from backend.app.core.mock_nemo import load_model
            
            # Try to load a model
            model = load_model("test-model")
            test_response = model.generate("Test prompt")
            
            print_status("Mock NeMo Configuration", True, "Using mock implementation")
            print(f"  Test generation: {test_response[:50]}...")
            return True
        except Exception as e:
            print_status("Mock NeMo Configuration", False, f"Error with mock implementation: {str(e)}")
            return False
    else:
        # Check for real NeMo
        try:
            import nemo
            nemo_version = nemo.__version__
            print_status("NeMo Version", True, f"Version: {nemo_version}")
            
            # Check if model directory exists
            model_dir = Path.home() / ".cache" / "nemo"
            model_exists = model_dir.exists() and any(model_dir.iterdir())
            
            print_status("NeMo Models Directory", model_dir.exists(), f"Path: {model_dir}")
            
            return True
        except ImportError:
            print_status("NeMo Configuration", False, "NeMo not installed")
            return False
        except Exception as e:
            print_status("NeMo Configuration", False, f"Error: {str(e)}")
            return False

def check_project_structure():
    """Check project directory structure."""
    required_dirs = [
        "backend",
        "backend/app",
        "backend/app/api",
        "backend/app/core",
        "backend/app/db",
        "backend/data",
        "frontend",
        "frontend/src"
    ]
    
    required_files = [
        "backend/.env",
        "backend/app/main.py",
        "start_services.bat",
        "stop_services.bat"
    ]
    
    missing_dirs = []
    missing_files = []
    
    for directory in required_dirs:
        if not os.path.isdir(directory):
            missing_dirs.append(directory)
            print_status(f"Directory: {directory}", False, "Not found")
        else:
            print_status(f"Directory: {directory}", True)
    
    for file in required_files:
        if not os.path.isfile(file):
            missing_files.append(file)
            print_status(f"File: {file}", False, "Not found")
        else:
            print_status(f"File: {file}", True)
    
    if missing_dirs or missing_files:
        if missing_dirs:
            print("\nMissing directories:")
            for d in missing_dirs:
                print(f"  - {d}")
        if missing_files:
            print("\nMissing files:")
            for f in missing_files:
                print(f"  - {f}")
    
    return len(missing_dirs) == 0 and len(missing_files) == 0

def check_mock_nemo_directory():
    """Check if mock_nemo directory exists and is properly set up."""
    mock_nemo_dir = Path("backend/app/core/mock_nemo")
    
    if not mock_nemo_dir.exists():
        print_status("Mock NeMo Directory", False, f"Directory not found: {mock_nemo_dir}")
        return False
    
    # Check for __init__.py
    init_file = mock_nemo_dir / "__init__.py"
    if not init_file.exists():
        print_status("Mock NeMo __init__.py", False, "File not found")
        return False
    
    print_status("Mock NeMo Directory", True, f"Path: {mock_nemo_dir}")
    print_status("Mock NeMo __init__.py", True)
    
    return True

def main():
    """Run all checks."""
    print_header("AI Assistant System Check")
    
    all_checks = [
        ("Python Environment", check_python_version),
        ("Required Packages", check_packages),
        ("PyTorch CUDA Support", check_pytorch_cuda),
        ("PostgreSQL Database", check_database),
        ("NeMo Configuration", check_nemo_configuration),
        ("Mock NeMo Directory", check_mock_nemo_directory),
        ("Project Structure", check_project_structure)
    ]
    
    successes = []
    failures = []
    
    for name, check_func in all_checks:
        print_header(name)
        result = check_func()
        if result:
            successes.append(name)
        else:
            failures.append(name)
    
    print_header("System Check Summary")
    print(f"Successes: {len(successes)}/{len(all_checks)}")
    for name in successes:
        print_status(name, True)
    
    if failures:
        print("\nFailures:")
        for name in failures:
            print_status(name, False)
        print("\nSome checks failed. Please address the issues before starting the project.")
    else:
        print("\nAll checks passed! Your system is ready to run the AI Assistant project.")

if __name__ == "__main__":
    main()