#!/usr/bin/env python3
"""
AI Assistant Comprehensive Startup Script
Launches all required services with proper error handling and logging
"""

import os
import sys
import subprocess
import time
import webbrowser
import psutil
import requests
from pathlib import Path
from datetime import datetime

class AIAssistantLauncher:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.log_file = self.base_path / "logs" / f"startup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file.parent.mkdir(exist_ok=True)
        
        self.services = {
            "PostgreSQL": {
                "check": self.check_postgres,
                "start": self.start_postgres,
                "port": 5432
            },
            "Ollama": {
                "check": self.check_ollama,
                "start": self.start_ollama,
                "port": 11434
            },
            "Backend": {
                "check": self.check_backend,
                "start": self.start_backend,
                "port": 8000
            },
            "Frontend": {
                "check": self.check_frontend,
                "start": self.start_frontend,
                "port": 5173
            }
        }
        
        self.processes = []
        
    def log(self, message, level="INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        with open(self.log_file, "a") as f:
            f.write(log_message + "\n")
            
    def check_port(self, port):
        """Check if a port is in use"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False
        
    def check_postgres(self):
        """Check if PostgreSQL is running"""
        try:
            # Check if postgres process is running
            for proc in psutil.process_iter(['name']):
                if 'postgres' in proc.info['name'].lower():
                    return True
            return False
        except:
            return False
            
    def start_postgres(self):
        """Start PostgreSQL service"""
        self.log("Starting PostgreSQL...")
        try:
            # Windows service command
            subprocess.run(["net", "start", "postgresql-x64-17"], check=True)
            time.sleep(3)
            return True
        except subprocess.CalledProcessError:
            # Try alternative service name
            try:
                subprocess.run(["net", "start", "postgresql"], check=True)
                time.sleep(3)
                return True
            except:
                self.log("Failed to start PostgreSQL. Please start it manually.", "ERROR")
                return False
                
    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def start_ollama(self):
        """Start Ollama service"""
        self.log("Starting Ollama...")
        try:
            # Start Ollama in a new window
            if sys.platform == "win32":
                process = subprocess.Popen(
                    ["cmd", "/c", "start", "Ollama", "ollama", "serve"],
                    shell=True
                )
            else:
                process = subprocess.Popen(["ollama", "serve"])
            
            self.processes.append(process)
            
            # Wait for Ollama to start
            for i in range(30):
                if self.check_ollama():
                    self.log("Ollama started successfully")
                    return True
                time.sleep(1)
                
            self.log("Ollama failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"Failed to start Ollama: {e}", "ERROR")
            return False
            
    def check_backend(self):
        """Check if backend is running"""
        try:
            response = requests.get("http://localhost:8000/api/health/ping", timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def start_backend(self):
        """Start FastAPI backend"""
        self.log("Starting Backend API...")
        
        backend_path = self.base_path / "backend"
        venv_python = self.base_path / "venv_nemo" / "Scripts" / "python.exe"
        
        if not venv_python.exists():
            self.log("Virtual environment not found at: " + str(venv_python), "ERROR")
            self.log("Please ensure venv_nemo exists in the project root.", "ERROR")
            return False
            
        try:
            # Start backend in a new window
            if sys.platform == "win32":
                # Convert Path objects to strings and ensure proper escaping
                backend_str = str(backend_path.absolute()).replace("/", "\\")
                venv_python_str = str(venv_python.absolute()).replace("/", "\\")
                
                # Use run_server.py which properly sets up the Python path
                run_server_path = backend_path / "run_server.py"
                cmd_parts = [
                    "cmd", "/c", "start", '"Backend API"', "cmd", "/k",
                    f'cd /d "{backend_str}" && "{venv_python_str}" "{run_server_path}"'
                ]
                
                process = subprocess.Popen(
                    ' '.join(cmd_parts),
                    shell=True
                )
            else:
                process = subprocess.Popen(
                    [str(venv_python), "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
                    cwd=str(backend_path)
                )
                
            self.processes.append(process)
            
            # Wait for backend to start
            for i in range(60):
                if self.check_backend():
                    self.log("Backend API started successfully")
                    return True
                time.sleep(1)
                
            self.log("Backend failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"Failed to start backend: {e}", "ERROR")
            return False
            
    def check_frontend(self):
        """Check if frontend is running"""
        return self.check_port(5173)
        
    def start_frontend(self):
        """Start React frontend"""
        self.log("Starting Frontend...")
        
        frontend_path = self.base_path / "frontend"
        
        try:
            # Start frontend in a new window
            if sys.platform == "win32":
                # Convert Path object to string and ensure proper escaping
                frontend_str = str(frontend_path.absolute()).replace("/", "\\")
                
                # Use explicit command construction to avoid issues
                cmd_parts = [
                    "cmd", "/c", "start", '"Frontend"', "cmd", "/k",
                    f'cd /d "{frontend_str}" && npm run dev'
                ]
                
                process = subprocess.Popen(
                    ' '.join(cmd_parts),
                    shell=True
                )
            else:
                process = subprocess.Popen(
                    ["npm", "run", "dev"],
                    cwd=str(frontend_path)
                )
                
            self.processes.append(process)
            
            # Wait for frontend to start
            for i in range(30):
                if self.check_frontend():
                    self.log("Frontend started successfully")
                    return True
                time.sleep(1)
                
            self.log("Frontend failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"Failed to start frontend: {e}", "ERROR")
            return False
            
    def check_models(self):
        """Check installed Ollama models"""
        self.log("\nChecking installed models...")
        
        required_models = [
            "mistral-nemo:latest",
            "deepseek-coder-v2:16b-lite-instruct-q4_K_M",
            "qwen2.5:32b-instruct-q4_K_M"
        ]
        
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                installed = [m["name"] for m in response.json().get("models", [])]
                
                for model in required_models:
                    if any(model in inst for inst in installed):
                        self.log(f"[OK] {model} - Installed", "SUCCESS")
                    else:
                        self.log(f"[X] {model} - Not installed", "WARNING")
                        self.log(f"  Run: ollama pull {model}")
            else:
                self.log("Could not check models - Ollama not responding", "WARNING")
                
        except Exception as e:
            self.log(f"Error checking models: {e}", "ERROR")
            
    def check_docker(self):
        """Check if Docker is running"""
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
            
    def start_docker(self):
        """Start Docker Desktop if not running"""
        if self.check_docker():
            return True
            
        self.log("Starting Docker Desktop...")
        try:
            if sys.platform == "win32":
                # Try to start Docker Desktop
                docker_paths = [
                    r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
                    r"C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"
                ]
                
                for path in docker_paths:
                    if Path(path).exists():
                        subprocess.Popen([path])
                        break
                
                # Wait for Docker to start
                for i in range(60):
                    if self.check_docker():
                        self.log("Docker Desktop started successfully")
                        return True
                    time.sleep(2)
                    
            self.log("Docker Desktop failed to start or is not installed", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Error starting Docker: {e}", "WARNING")
            return False
    
    def check_nim_containers(self):
        """Check and optionally start NVIDIA NIM Docker containers"""
        self.log("\nChecking NVIDIA NIM containers...")
        
        if not self.check_docker():
            self.log("Docker is not running. Attempting to start...", "WARNING")
            if not self.start_docker():
                self.log("Cannot use NIM models without Docker", "WARNING")
                return
        
        try:
            # Check if .env file has NGC_API_KEY
            env_path = self.base_path / ".env"
            if not env_path.exists():
                self.log("No .env file found. Creating one...", "WARNING")
                with open(env_path, "w") as f:
                    f.write("# NVIDIA NGC API Key for NIM containers\n")
                    f.write("NGC_API_KEY=your_key_here\n")
                self.log("Please add your NGC API key to .env file", "WARNING")
                return
                
            # Check if NGC_API_KEY is set
            with open(env_path, "r") as f:
                content = f.read()
                if "NGC_API_KEY=your_key_here" in content or "NGC_API_KEY=" not in content:
                    self.log("NGC API key not configured in .env file", "WARNING")
                    self.log("NIM containers will not be started", "WARNING")
                    return
            
            # Check existing containers
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}:{{.State}}"],
                capture_output=True,
                text=True
            )
            
            containers = {}
            for line in result.stdout.strip().split('\n'):
                if ':' in line and line.strip():
                    name, state = line.split(':', 1)
                    containers[name] = state
            
            # Start embeddings container (always needed for RAG)
            if "nim-embeddings" in containers:
                if containers["nim-embeddings"] == "running":
                    self.log("[OK] nim-embeddings - Already running", "SUCCESS")
                else:
                    self.log("Starting nim-embeddings container...")
                    subprocess.run(["docker-compose", "up", "-d", "nim-embeddings"], 
                                 capture_output=True, cwd=str(self.base_path))
                    time.sleep(5)
                    self.log("[OK] nim-embeddings - Started", "SUCCESS")
            else:
                self.log("Creating and starting nim-embeddings container...")
                subprocess.run(["docker-compose", "up", "-d", "nim-embeddings"], 
                             capture_output=True, cwd=str(self.base_path))
                time.sleep(10)
                self.log("[OK] nim-embeddings - Created and started", "SUCCESS")
                
            # Check but don't auto-start 70B model (high VRAM usage)
            if "nim-generation-70b" in containers:
                if containers["nim-generation-70b"] == "running":
                    self.log("[OK] nim-generation-70b - Already running (22GB VRAM)", "SUCCESS")
                else:
                    self.log("[X] nim-generation-70b - Not running", "INFO")
                    self.log("  To start: docker-compose up nim-generation-70b", "INFO")
            else:
                self.log("[X] nim-generation-70b - Not created", "INFO")
                self.log("  To create and start: docker-compose up nim-generation-70b", "INFO")
                self.log("  Note: Requires 22GB VRAM, will unload other models", "INFO")
                
        except FileNotFoundError:
            self.log("Docker or docker-compose not found", "WARNING")
        except Exception as e:
            self.log(f"Error with NIM containers: {e}", "ERROR")
            
    def launch_browser(self):
        """Open the application in browser"""
        self.log("\nOpening application in browser...")
        time.sleep(2)
        webbrowser.open("http://localhost:5173")
        
    def run(self):
        """Main launch sequence"""
        self.log("=" * 60)
        self.log("AI Assistant Startup Sequence")
        self.log("=" * 60)
        
        # Check and start each service
        for service_name, service_config in self.services.items():
            self.log(f"\nChecking {service_name}...")
            
            if service_config["check"]():
                self.log(f"{service_name} is already running on port {service_config['port']}")
            else:
                if service_config["start"]():
                    self.log(f"{service_name} started successfully")
                else:
                    self.log(f"Failed to start {service_name}", "ERROR")
                    if service_name in ["PostgreSQL", "Ollama"]:
                        self.log("Cannot continue without core services", "ERROR")
                        return False
                        
        # Additional checks
        self.check_models()
        self.check_nim_containers()
        
        # Launch browser
        self.launch_browser()
        
        self.log("\n" + "=" * 60)
        self.log("AI Assistant is ready!")
        self.log(f"Frontend: http://localhost:5173")
        self.log(f"Backend API: http://localhost:8000/docs")
        self.log(f"Logs saved to: {self.log_file}")
        self.log("=" * 60)
        
        self.log("\nPress Ctrl+C to stop all services...")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log("\nShutting down services...")
            self.shutdown()
            
    def shutdown(self):
        """Shutdown all started processes"""
        for process in self.processes:
            try:
                process.terminate()
                self.log(f"Terminated process {process.pid}")
            except:
                pass
                
        self.log("Shutdown complete")

if __name__ == "__main__":
    launcher = AIAssistantLauncher()
    launcher.run()