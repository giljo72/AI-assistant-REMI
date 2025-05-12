import os
import sys
import subprocess
import platform
import time

def print_step(step, message):
    """Print a formatted step message."""
    print(f"\n[STEP {step}] {message}")
    print("=" * 80)

def run_command(command, description=None):
    """Run a command and print its output."""
    if description:
        print(f"\n>> {description}")
    
    print(f"Running: {' '.join(command)}")
    
    try:
        # Add shell=True to fix Windows command execution
        process = subprocess.run(command, check=True, text=True, capture_output=True, shell=True)
        if process.stdout:
            print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required software is installed."""
    print_step(1, "Checking prerequisites")
    
    prereqs = {
        "Python": ["python", "--version"],
        "PostgreSQL": ["psql", "--version"],
        "Node.js": ["node", "--version"],
        "npm": ["npm", "--version"],
        "Docker": ["docker", "--version"],
        "Ollama": ["ollama", "--version"]
    }
    
    missing = []
    
    for name, command in prereqs.items():
        try:
            # Add shell=True for Windows command resolution
            subprocess.run(command, check=True, capture_output=True, text=True, shell=True)
            print(f"✓ {name} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"✗ {name} is NOT installed")
            missing.append(name)
    
    if missing:
        print("\nMissing prerequisites:")
        for item in missing:
            print(f"- {item}")
        print("\nPlease install missing components before continuing.")
        return False
    
    return True

def create_directories():
    """Create project directory structure."""
    print_step(2, "Creating directory structure")
    
    directories = [
        "backend/app/api/endpoints",
        "backend/app/core",
        "backend/app/db/models",
        "backend/app/db/repositories",
        "backend/app/schemas",
        "backend/app/services",
        "backend/app/document_processing",
        "backend/app/rag",
        "backend/app/reasoning",
        "backend/app/external",
        "backend/static",
        "backend/data/uploads",
        "backend/data/processed",
        "backend/data/hierarchy",
        "backend/data/logs",
        "backend/migrations",
        "backend/tests",
        "frontend/public",
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/services",
        "frontend/src/hooks",
        "frontend/src/store",
        "frontend/src/utils",
        "frontend/src/types",
        "frontend/src/styles",
        "scripts",
        "docker",
        "docs"
    ]
    
    for directory in directories:
        dir_path = os.path.join(os.getcwd(), directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created: {dir_path}")
    
    return True

def setup_python_environment():
    """Set up the Python virtual environment."""
    print_step(3, "Setting up Python virtual environment")
    
    # Create virtual environment
    venv_path = os.path.join(os.getcwd(), "venv")
    if os.path.exists(venv_path):
        print(f"Virtual environment already exists at {venv_path}")
    else:
        if not run_command(["python", "-m", "venv", "venv"], "Creating virtual environment"):
            return False
    
    # Determine the python command to use
    python_cmd = os.path.join(venv_path, "Scripts", "python") if platform.system() == "Windows" else os.path.join(venv_path, "bin", "python")
    
    # Upgrade pip using python -m pip (recommended approach)
    if not run_command([python_cmd, "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip"):
        return False
    
    # Install requirements
    pip_cmd = os.path.join(venv_path, "Scripts", "pip") if platform.system() == "Windows" else os.path.join(venv_path, "bin", "pip")
    if not run_command([pip_cmd, "install", "-r", "requirements.txt"], "Installing Python requirements"):
        return False
    
    return True

def setup_nodejs_environment():
    """Set up the Node.js environment."""
    print_step(4, "Setting up Node.js environment")
    
    os.chdir(os.path.join(os.getcwd(), "frontend"))
    
    # Create package.json if it doesn't exist
    if not os.path.exists("package.json"):
        if not run_command(["npm", "init", "-y"], "Initializing npm package"):
            return False
    
    # Install React and required dependencies
    packages = [
        "react", 
        "react-dom", 
        "react-router-dom", 
        "@reduxjs/toolkit", 
        "react-redux", 
        "axios", 
        "typescript", 
        "@types/react", 
        "@types/react-dom",
        "tailwindcss"
    ]
    
    if not run_command(["npm", "install"] + packages, "Installing Node.js packages"):
        return False
    
    # Install development dependencies
    dev_packages = [
        "@typescript-eslint/eslint-plugin",
        "@typescript-eslint/parser",
        "eslint",
        "eslint-plugin-react",
        "eslint-plugin-react-hooks"
    ]
    
    if not run_command(["npm", "install", "--save-dev"] + dev_packages, "Installing development packages"):
        return False
    
    os.chdir("..")
    return True

def setup_database():
    """Set up the PostgreSQL database."""
    print_step(5, "Setting up PostgreSQL database")
    
    db_name = "ai_assistant"
    db_user = input("Enter PostgreSQL username (default: postgres): ") or "postgres"
    db_password = input("Enter PostgreSQL password: ")
    
    # Try to create database
    try:
        cmd = ["psql", "-U", db_user, "-c", f"CREATE DATABASE {db_name};"]
        subprocess.run(cmd, check=True, input=db_password, text=True, capture_output=True, shell=True)
        print(f"Created database: {db_name}")
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e.stderr):
            print(f"Database '{db_name}' already exists. Using existing database.")
        else:
            print(f"Error creating database: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False
    
    # Try to create pgvector extension, but don't fail if it's not available
    pgvector_available = False
    try:
        cmd = ["psql", "-U", db_user, "-d", db_name, "-c", "CREATE EXTENSION IF NOT EXISTS vector;"]
        subprocess.run(cmd, check=True, input=db_password, text=True, capture_output=True, shell=True)
        print("Created pgvector extension")
        pgvector_available = True
    except subprocess.CalledProcessError as e:
        print("Warning: pgvector extension is not available.")
        print("You'll need to install it later for vector search capabilities.")
        print("For now, we'll continue with the setup.")
    
    # Create .env file with database connection details
    env_content = f"""
DATABASE_URL=postgresql://{db_user}:{db_password}@localhost/{db_name}
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3
EMBEDDINGS_MODEL=all-MiniLM-L6-v2
UPLOAD_FOLDER=./data/uploads
PROCESSED_FOLDER=./data/processed
LOG_LEVEL=INFO
PGVECTOR_AVAILABLE={'true' if pgvector_available else 'false'}
"""
    with open(os.path.join(os.getcwd(), "backend", ".env"), "w") as f:
        f.write(env_content.strip())
    print("Created .env file with database connection details")
    
    return True

def setup_ollama():
    """Pull necessary Ollama models."""
    print_step(6, "Setting up Ollama models")
    
    try:
        # Check if Ollama is running
        subprocess.run(["ollama", "list"], check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Ollama is not running or not installed. Please start Ollama and run this script again.")
        return False
    
    # Pull the Llama3 model
    if not run_command(["ollama", "pull", "llama3"], "Pulling Llama3 model"):
        print("Warning: Failed to pull Llama3 model. You can do this manually later.")
    
    return True

def main():
    """Main setup function."""
    print("=" * 80)
    print("AI Assistant Setup Script")
    print("=" * 80)
    
    if not check_prerequisites():
        sys.exit(1)
    
    steps = [
        create_directories,
        setup_python_environment,
        setup_nodejs_environment,
        setup_database,
        setup_ollama
    ]
    
    for i, step_func in enumerate(steps, start=2):
        if not step_func():
            print(f"\nSetup failed at step {i}. Please fix the issues and run the script again.")
            sys.exit(1)
    
    print("\n" + "=" * 80)
    print("Setup completed successfully!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Start the backend: run 'start_services.bat'")
    print("2. Start the frontend: run 'npm start' in the frontend directory")
    print("3. Access the application at http://localhost:3000")

if __name__ == "__main__":
    main()

## Run manually:
## F:\Assistant\venv_nemo\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
## F:\Assistant\venv_nemo\Scripts\pip install nemo_toolkit[all] --extra-index-url https://pypi.ngc.nvidia.com