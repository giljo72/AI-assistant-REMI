#!/usr/bin/env python
"""
Setup script for the AI Assistant project.
Creates virtual environment and installs dependencies.
"""

import os
import sys
import subprocess
import platform

def main():
    # Determine the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Paths
    venv_dir = os.path.join(current_dir, "venv_nemo")
    backend_dir = os.path.join(current_dir, "backend")
    frontend_dir = os.path.join(current_dir, "frontend")
    requirements_file = os.path.join(backend_dir, "requirements.txt")
    
    # Determine Python command
    if platform.system() == "Windows":
        python_cmd = os.path.join(venv_dir, "Scripts", "python")
        pip_cmd = os.path.join(venv_dir, "Scripts", "pip")
    else:
        python_cmd = os.path.join(venv_dir, "bin", "python")
        pip_cmd = os.path.join(venv_dir, "bin", "pip")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    
    # Upgrade pip using the Python interpreter (more reliable than using pip directly)
    print("Upgrading pip...")
    subprocess.run([python_cmd, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # Install backend dependencies with option to prefer binary packages
    print("Installing backend dependencies...")
    subprocess.run([
        python_cmd, "-m", "pip", "install", 
        "--prefer-binary",  # Prefer pre-built binaries over source
        "-r", requirements_file
    ], check=True)
    
    # Check if Node.js and npm are installed
    try:
        subprocess.run(["node", "--version"], check=True, stdout=subprocess.PIPE)
        subprocess.run(["npm", "--version"], check=True, stdout=subprocess.PIPE)
        
        # Install frontend dependencies
        if os.path.exists(frontend_dir):
            print("Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Node.js or npm not found. Please install Node.js and npm to set up the frontend.")
    
    print("\nEnvironment setup complete!")
    print(f"Activate the virtual environment with: {venv_dir}\\Scripts\\activate (Windows) or source {venv_dir}/bin/activate (Linux/Mac)")
    print("Start the backend with: uvicorn app.main:app --reload --port 8000")
    print("Start the frontend with: npm run dev")

if __name__ == "__main__":
    main()