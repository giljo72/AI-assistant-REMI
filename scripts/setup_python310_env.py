#!/usr/bin/env python
"""
Setup script for AI Assistant using Python 3.10.
Creates a virtual environment with Python 3.10 and installs dependencies.
"""

import os
import sys
import subprocess
import platform
import shutil

def find_python310():
    """Find Python 3.10 installation"""
    # Check common paths for Python 3.10
    possible_paths = [
        # Windows paths
        r"C:\Python310\python.exe",
        r"C:\Program Files\Python310\python.exe",
        r"C:\Program Files (x86)\Python310\python.exe",
        r"C:\Users\{}\AppData\Local\Programs\Python\Python310\python.exe".format(os.getenv("USERNAME")),
        # Add more paths as needed
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Try using 'py' launcher
    try:
        py_path = subprocess.check_output(["py", "-3.10", "-c", "import sys; print(sys.executable)"], 
                                         text=True).strip()
        if py_path and os.path.exists(py_path):
            return py_path
    except:
        pass
    
    # Try checking if 'python3.10' is in PATH
    try:
        if platform.system() == "Windows":
            python310_path = subprocess.check_output(["where", "python3.10"], text=True).strip().split("\r\n")[0]
        else:
            python310_path = subprocess.check_output(["which", "python3.10"], text=True).strip()
        
        if python310_path and os.path.exists(python310_path):
            return python310_path
    except:
        pass
    
    return None

def main():
    # Determine the project directory
    if os.path.exists('F:\\AIbot'):
        project_dir = 'F:\\AIbot'
    elif os.path.exists('/mnt/f/AIbot'):
        project_dir = '/mnt/f/AIbot'
    else:
        print("Error: AIbot directory not found")
        return 1
    
    # Paths
    venv_dir = os.path.join(project_dir, "venv_nemo")
    backend_dir = os.path.join(project_dir, "backend")
    frontend_dir = os.path.join(project_dir, "frontend")
    requirements_file = os.path.join(backend_dir, "requirements.txt")
    
    # Find Python 3.10
    python310_path = find_python310()
    
    if not python310_path:
        print("Error: Python 3.10 not found. Please install Python 3.10 and try again.")
        print("You can download it from: https://www.python.org/downloads/release/python-3106/")
        return 1
    
    print(f"Found Python 3.10 at: {python310_path}")
    
    # Remove existing venv if it exists
    if os.path.exists(venv_dir):
        print(f"Removing existing virtual environment at {venv_dir}")
        try:
            shutil.rmtree(venv_dir)
        except Exception as e:
            print(f"Warning: Could not remove existing virtual environment: {str(e)}")
            print("Please manually delete the directory and try again.")
            return 1
    
    # Create a new virtual environment using Python 3.10
    print(f"Creating virtual environment using Python 3.10...")
    try:
        subprocess.run([python310_path, "-m", "venv", venv_dir], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {str(e)}")
        return 1
    
    # Determine Python command in the virtual environment
    if platform.system() == "Windows":
        python_cmd = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_cmd = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        python_cmd = os.path.join(venv_dir, "bin", "python")
        pip_cmd = os.path.join(venv_dir, "bin", "pip")
    
    # Upgrade pip within the virtual environment
    print("Upgrading pip...")
    try:
        subprocess.run([python_cmd, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error upgrading pip: {str(e)}")
        return 1
    
    # Verify Python version in the virtual environment
    try:
        version_output = subprocess.check_output([python_cmd, "-V"], text=True).strip()
        print(f"Virtual environment is using: {version_output}")
        if "3.10" not in version_output:
            print("Warning: The virtual environment is not using Python 3.10 as expected.")
            print("This might cause compatibility issues with some dependencies.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking Python version: {str(e)}")
    
    # Install backend dependencies with pre-built wheels preferred
    print("Installing backend dependencies...")
    try:
        subprocess.run([
            python_cmd, "-m", "pip", "install", 
            "--prefer-binary",  # Prefer pre-built binaries
            "-r", requirements_file
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing backend dependencies: {str(e)}")
        print("\nTrying with modified requirements (to avoid Rust compilation)...")
        
        # Create a temporary modified requirements file
        temp_req_file = os.path.join(project_dir, "temp_requirements.txt")
        try:
            with open(requirements_file, 'r') as src, open(temp_req_file, 'w') as dst:
                for line in src:
                    if line.strip().startswith('pydantic=='):
                        dst.write('pydantic==1.10.8\n')  # Use older version without Rust
                    elif line.strip().startswith('fastapi=='):
                        dst.write(line)  # Keep FastAPI version
                    elif line.strip().startswith('psycopg2-binary=='):
                        dst.write('psycopg2-binary==2.9.5\n')  # Use older version with pre-built wheels
                    else:
                        dst.write(line)
            
            print(f"Created modified requirements file at {temp_req_file}")
            print("Installing dependencies with modified requirements...")
            
            try:
                subprocess.run([
                    python_cmd, "-m", "pip", "install", 
                    "--prefer-binary",
                    "-r", temp_req_file
                ], check=True)
                print("Successfully installed dependencies with modified requirements!")
            except subprocess.CalledProcessError as e2:
                print(f"Error installing dependencies with modified requirements: {str(e2)}")
                return 1
            
        except Exception as e:
            print(f"Error creating modified requirements file: {str(e)}")
            return 1
        finally:
            # Clean up temporary file
            if os.path.exists(temp_req_file):
                os.remove(temp_req_file)
    
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
    print(f"Python 3.10 virtual environment created at: {venv_dir}")
    print(f"Activate the virtual environment with:")
    if platform.system() == "Windows":
        print(f"{venv_dir}\\Scripts\\activate")
    else:
        print(f"source {venv_dir}/bin/activate")
    
    print("\nStart the backend with:")
    print("cd F:\\AIbot\\backend")
    print("..\\venv_nemo\\Scripts\\python -m uvicorn app.main:app --reload --port 8000")
    
    print("\nStart the frontend with:")
    print("cd F:\\AIbot\\frontend")
    print("npm run dev")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())