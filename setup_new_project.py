"""
Setup script for creating a new clean AIbot project.
This script creates the directory structure and copies essential files.
"""
import os
import shutil
import sys
import subprocess

# Define source and destination directories
SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))
DEST_DIR = "F:/AIbot"

# Documentation files to copy
DOC_FILES = [
    "Scope.md",
    "Readme.MD",
    "CLAUDE.md",
    "Devlog.md",
    "implementation.md",
    "File Management Navigation Guide.md"
]

# Define the project structure
PROJECT_STRUCTURE = {
    "": [],  # Root directory
    "backend": [],
    "backend/app": [],
    "backend/app/api": [],
    "backend/app/api/endpoints": [],
    "backend/app/core": [],
    "backend/app/core/mock_nemo": [],
    "backend/app/db": [],
    "backend/app/db/models": [],
    "backend/app/db/repositories": [],
    "backend/app/document_processing": [],
    "backend/app/rag": [],
    "backend/app/schemas": [],
    "backend/data": [],
    "backend/data/uploads": [],
    "backend/data/processed": [],
    "backend/data/hierarchy": [],
    "backend/data/logs": [],
    "backend/scripts": [],
    "frontend": [],
    "frontend/src": [],
    "frontend/src/components": [],
    "frontend/src/components/chat": [],
    "frontend/src/components/document": [],
    "frontend/src/components/file": [],
    "frontend/src/components/layout": [],
    "frontend/src/components/modals": [],
    "frontend/src/components/project": [],
    "frontend/src/components/sidebar": [],
    "frontend/src/context": [],
    "frontend/src/hooks": [],
    "frontend/src/services": [],
    "frontend/src/store": [],
    "frontend/public": [],
    "docs": [],
    "scripts": [],
    "logs": []
}

def create_directory_structure():
    """Create the directory structure for the new project."""
    print("Creating directory structure...")
    
    # Create all directories
    for dir_path in PROJECT_STRUCTURE.keys():
        full_path = os.path.join(DEST_DIR, dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"  Created directory: {full_path}")

def copy_documentation():
    """Copy documentation files to the new project."""
    print("\nCopying documentation files...")
    
    for doc_file in DOC_FILES:
        source_file = os.path.join(SOURCE_DIR, doc_file)
        dest_file = os.path.join(DEST_DIR, "docs", doc_file)
        
        if os.path.exists(source_file):
            shutil.copy2(source_file, dest_file)
            print(f"  Copied: {doc_file}")
        else:
            print(f"  Warning: Could not find {source_file}")

def copy_backend_files():
    """Copy backend files to the new project."""
    print("\nCopying backend files...")
    
    # Copy cleaned versions to new project
    backend_files = [
        ("backend/app/cleaned_main.py", "backend/app/main.py"),
        ("backend/app/api/cleaned_api.py", "backend/app/api/api.py"),
        ("backend/app/api/endpoints/cleaned_files.py", "backend/app/api/endpoints/files.py")
    ]
    
    for source_rel, dest_rel in backend_files:
        source_file = os.path.join(SOURCE_DIR, source_rel)
        dest_file = os.path.join(DEST_DIR, dest_rel)
        
        if os.path.exists(source_file):
            shutil.copy2(source_file, dest_file)
            print(f"  Copied: {dest_rel}")
        else:
            print(f"  Warning: Could not find {source_file}")
    
    # Copy other backend files that don't need cleaning
    core_backend_dirs = [
        "backend/app/api/endpoints",
        "backend/app/core", 
        "backend/app/core/mock_nemo",
        "backend/app/db",
        "backend/app/db/models",
        "backend/app/db/repositories",
        "backend/app/document_processing",
        "backend/app/rag",
        "backend/app/schemas"
    ]
    
    for dir_path in core_backend_dirs:
        source_dir = os.path.join(SOURCE_DIR, dir_path)
        dest_dir = os.path.join(DEST_DIR, dir_path)
        
        if os.path.isdir(source_dir):
            # Copy all .py files but exclude the cleaned versions and test files
            for file in os.listdir(source_dir):
                if file.endswith(".py") and not file.startswith("test_") and not file.startswith("cleaned_"):
                    source_file = os.path.join(source_dir, file)
                    dest_file = os.path.join(dest_dir, file)
                    shutil.copy2(source_file, dest_file)
                    print(f"  Copied: {dir_path}/{file}")
    
    # Copy requirements.txt
    source_req = os.path.join(SOURCE_DIR, "backend/requirements.txt")
    dest_req = os.path.join(DEST_DIR, "backend/requirements.txt")
    if os.path.exists(source_req):
        shutil.copy2(source_req, dest_req)
        print(f"  Copied: backend/requirements.txt")

def copy_frontend_files():
    """Copy frontend files to the new project."""
    print("\nCopying frontend files...")
    
    # Copy entire frontend directory
    source_frontend = os.path.join(SOURCE_DIR, "frontend")
    dest_frontend = os.path.join(DEST_DIR, "frontend")
    
    if os.path.isdir(source_frontend):
        # Copy src directory recursively
        source_src = os.path.join(source_frontend, "src")
        dest_src = os.path.join(dest_frontend, "src")
        shutil.copytree(source_src, dest_src, dirs_exist_ok=True)
        print(f"  Copied: frontend/src directory")
        
        # Copy config files
        for file in os.listdir(source_frontend):
            if file.endswith((".json", ".js", ".html", ".md")):
                source_file = os.path.join(source_frontend, file)
                dest_file = os.path.join(dest_frontend, file)
                shutil.copy2(source_file, dest_file)
                print(f"  Copied: frontend/{file}")
    else:
        print(f"  Warning: Could not find {source_frontend}")

def create_scripts():
    """Create essential scripts for the new project."""
    print("\nCreating utility scripts...")
    
    # Define scripts content
    scripts = {
        "setup_environment.py": """
'''
Setup script for creating the Python virtual environment and installing dependencies.
'''
import os
import subprocess
import sys
import platform

def main():
    # Determine the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_root, "backend")
    venv_dir = os.path.join(project_root, "venv_nemo")
    
    # Check if we're on Windows or Unix
    is_windows = platform.system() == "Windows"
    
    # Create virtual environment
    print("Creating virtual environment...")
    if is_windows:
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        python_cmd = os.path.join(venv_dir, "Scripts", "python")
    else:
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        python_cmd = os.path.join(venv_dir, "bin", "python")
    
    # Upgrade pip using the Python interpreter (more reliable than using pip directly)
    print("Upgrading pip...")
    subprocess.run([python_cmd, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # Install backend dependencies
    print("Installing backend dependencies...")
    requirements_file = os.path.join(backend_dir, "requirements.txt")
    if os.path.exists(requirements_file):
        subprocess.run([python_cmd, "-m", "pip", "install", "-r", requirements_file], check=True)
    else:
        print(f"Warning: Could not find {requirements_file}")
    
    # Install frontend dependencies
    print("Installing frontend dependencies...")
    frontend_dir = os.path.join(project_root, "frontend")
    if os.path.exists(frontend_dir):
        npm_cmd = "npm.cmd" if is_windows else "npm"
        # Check if npm is installed
        try:
            subprocess.run([npm_cmd, "--version"], check=True, capture_output=True)
            subprocess.run([npm_cmd, "install"], cwd=frontend_dir, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: npm not found. Please install Node.js and npm.")
    
    print("Environment setup complete!")

if __name__ == "__main__":
    main()
""",
        
        "start_services.bat": """
@echo off
echo Starting AI Assistant services...

REM Start backend
start cmd /k "cd backend && ..\\venv_nemo\\Scripts\\activate && uvicorn app.main:app --reload --port 8000"

REM Start frontend
start cmd /k "cd frontend && npm run dev"

echo Services started!
""",
        
        "stop_services.bat": """
@echo off
echo Stopping AI Assistant services...

REM Find and kill uvicorn process
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a
)

REM Find and kill npm dev server
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    taskkill /F /PID %%a
)

echo Services stopped!
""",
        
        "scripts/setup_database.py": """
'''
Script for setting up the PostgreSQL database with pgvector extension.
'''
import os
import sys
import subprocess
import psycopg2
from psycopg2 import sql

def main():
    # Database connection parameters
    dbname = "postgres"  # Connect to default db first
    user = input("Enter PostgreSQL username: ")
    password = input("Enter PostgreSQL password: ")
    host = input("Enter PostgreSQL host (default: localhost): ") or "localhost"
    port = input("Enter PostgreSQL port (default: 5432): ") or "5432"
    
    # New database name
    new_dbname = "aibot"
    
    # Connect to default database
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (new_dbname,))
        exists = cursor.fetchone()
        
        if not exists:
            # Create new database
            print(f"Creating database {new_dbname}...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_dbname)))
        else:
            print(f"Database {new_dbname} already exists.")
        
        # Close connection to default database
        conn.close()
        
        # Connect to new database
        conn = psycopg2.connect(
            dbname=new_dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create pgvector extension
        print("Creating pgvector extension...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Save connection info to .env file
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env")
        with open(env_file, "w") as f:
            f.write(f"DATABASE_URL=postgresql://{user}:{password}@{host}:{port}/{new_dbname}\\n")
            f.write("UPLOAD_DIR=./data/uploads\\n")
            f.write("PROCESSED_DIR=./data/processed\\n")
            f.write("LOG_LEVEL=INFO\\n")
            f.write("USE_MOCK_NEMO=true\\n")
            f.write("MODEL_NAME=nvidia/nemo-1\\n")
        
        print("Database setup complete!")
        print(f"Connection information saved to {env_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

if __name__ == "__main__":
    main()
""",
    
        "scripts/reset_database.py": """
'''
Script for resetting the database - drops and recreates all tables.
'''
import os
import sys
import importlib.util
from pathlib import Path

def main():
    # Add backend directory to Python path
    backend_dir = Path(__file__).parent.parent / "backend"
    sys.path.append(str(backend_dir))
    
    # Import database modules
    try:
        from app.db.database import Base, engine
        
        # Confirm with user
        confirm = input("This will delete all data in the database. Continue? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
        
        # Drop and recreate all tables
        print("Dropping all tables...")
        Base.metadata.drop_all(engine)
        
        print("Recreating all tables...")
        Base.metadata.create_all(engine)
        
        print("Database reset complete!")
        
    except ImportError as e:
        print(f"Error importing modules: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    }
    
    # Create each script
    for script_path, content in scripts.items():
        dest_file = os.path.join(DEST_DIR, script_path)
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        
        with open(dest_file, "w") as f:
            f.write(content.strip())
        
        print(f"  Created: {script_path}")

def create_gitignore():
    """Create a .gitignore file for the new project."""
    print("\nCreating .gitignore...")
    
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv_nemo/
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Node.js
node_modules/
npm-debug.log
yarn-error.log
yarn-debug.log
.pnp/
.pnp.js
.yarn/
.npm/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Data directories
/backend/data/uploads/*
/backend/data/processed/*
/backend/data/logs/*
!/backend/data/uploads/.gitkeep
!/backend/data/processed/.gitkeep
!/backend/data/logs/.gitkeep

# IDE files
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Build outputs
/frontend/dist/
/frontend/build/
"""
    
    gitignore_path = os.path.join(DEST_DIR, ".gitignore")
    with open(gitignore_path, "w") as f:
        f.write(gitignore_content.strip())
    
    print(f"  Created: .gitignore")

def main():
    """Main function to set up the new project."""
    # Check if destination directory exists
    if os.path.exists(DEST_DIR):
        confirm = input(f"Directory {DEST_DIR} already exists. Contents may be overwritten. Continue? (y/n): ")
        if confirm.lower() != 'y':
            print("Setup aborted.")
            return
    
    # Create directory structure
    create_directory_structure()
    
    # Copy documentation
    copy_documentation()
    
    # Copy backend files
    copy_backend_files()
    
    # Copy frontend files
    copy_frontend_files()
    
    # Create scripts
    create_scripts()
    
    # Create .gitignore
    create_gitignore()
    
    print("\nProject setup complete!")
    print(f"New project created at: {DEST_DIR}")
    print("\nNext steps:")
    print("1. Run F:/AIbot/setup_environment.py to create the virtual environment")
    print("2. Run F:/AIbot/scripts/setup_database.py to configure the database")
    print("3. Run F:/AIbot/start_services.bat to start the application")

if __name__ == "__main__":
    main()