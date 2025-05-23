#!/usr/bin/env python3
"""
NVIDIA NIM Container Setup Helper
Helps set up and test NVIDIA NIM containers for the AI Assistant
"""

import subprocess
import os
import sys
import time
import requests
from pathlib import Path
from datetime import datetime

class NIMSetup:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.env_file = self.base_path / ".env"
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_prerequisites(self):
        """Check all prerequisites for NIM"""
        self.log("Checking prerequisites for NVIDIA NIM...")
        
        issues = []
        
        # Check Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✓ Docker is installed", "SUCCESS")
            else:
                issues.append("Docker is not installed")
        except FileNotFoundError:
            issues.append("Docker is not installed or not in PATH")
            
        # Check if Docker is running
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✓ Docker daemon is running", "SUCCESS")
            else:
                issues.append("Docker daemon is not running")
        except:
            issues.append("Cannot connect to Docker daemon")
            
        # Check docker-compose
        try:
            result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✓ Docker Compose is installed", "SUCCESS")
            else:
                issues.append("Docker Compose is not installed")
        except FileNotFoundError:
            issues.append("Docker Compose is not installed or not in PATH")
            
        # Check NVIDIA Docker runtime
        try:
            result = subprocess.run(["docker", "run", "--rm", "--gpus", "all", "nvidia/cuda:11.8.0-base-ubuntu22.04", "nvidia-smi"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✓ NVIDIA Docker runtime is working", "SUCCESS")
                self.log(f"  GPU detected: {self.extract_gpu_name(result.stdout)}", "INFO")
            else:
                issues.append("NVIDIA Docker runtime not working (install NVIDIA Container Toolkit)")
        except:
            issues.append("Cannot test NVIDIA Docker runtime")
            
        return issues
        
    def extract_gpu_name(self, nvidia_smi_output):
        """Extract GPU name from nvidia-smi output"""
        for line in nvidia_smi_output.split('\n'):
            if 'NVIDIA' in line and 'RTX' in line:
                return line.strip()
        return "GPU detected"
        
    def check_ngc_key(self):
        """Check and set up NGC API key"""
        self.log("\nChecking NGC API key configuration...")
        
        if not self.env_file.exists():
            self.log("Creating .env file...", "WARNING")
            with open(self.env_file, "w") as f:
                f.write("# NVIDIA NGC API Key for NIM containers\n")
                f.write("NGC_API_KEY=your_key_here\n")
                
        with open(self.env_file, "r") as f:
            content = f.read()
            
        if "NGC_API_KEY=your_key_here" in content or "NGC_API_KEY=" not in content:
            self.log("✗ NGC API key not configured", "WARNING")
            self.log("\nTo get your NGC API key:")
            self.log("1. Go to https://ngc.nvidia.com")
            self.log("2. Sign in or create a free account")
            self.log("3. Go to 'Setup' > 'Generate API Key'")
            self.log("4. Copy the key and paste it below")
            
            api_key = input("\nEnter your NGC API key (or press Enter to skip): ").strip()
            
            if api_key and api_key != "your_key_here":
                # Update .env file
                lines = content.split('\n')
                updated_lines = []
                for line in lines:
                    if line.startswith("NGC_API_KEY="):
                        updated_lines.append(f"NGC_API_KEY={api_key}")
                    else:
                        updated_lines.append(line)
                        
                with open(self.env_file, "w") as f:
                    f.write('\n'.join(updated_lines))
                    
                self.log("✓ NGC API key saved to .env file", "SUCCESS")
                return True
            else:
                self.log("Skipping NGC API key configuration", "WARNING")
                return False
        else:
            self.log("✓ NGC API key is already configured", "SUCCESS")
            return True
            
    def pull_nim_images(self):
        """Pull NIM Docker images"""
        self.log("\nPulling NVIDIA NIM Docker images...")
        self.log("This may take some time on first run as images are large (10-50GB)")
        
        images = [
            {
                "name": "nvcr.io/nim/nvidia/nv-embedqa-e5-v5:latest",
                "description": "Text embeddings for RAG (2GB VRAM)",
                "service": "nim-embeddings"
            },
            {
                "name": "nvcr.io/nim/meta/llama-3.1-70b-instruct:latest",
                "description": "Llama 70B for deep analysis (22GB VRAM)",
                "service": "nim-generation-70b"
            }
        ]
        
        for image in images:
            self.log(f"\nPulling {image['description']}...")
            self.log(f"Image: {image['name']}")
            
            try:
                # Check if image already exists
                check_result = subprocess.run(
                    ["docker", "images", "-q", image["name"]], 
                    capture_output=True, text=True
                )
                
                if check_result.stdout.strip():
                    self.log("✓ Image already downloaded", "SUCCESS")
                else:
                    # Pull the image
                    process = subprocess.Popen(
                        ["docker", "pull", image["name"]],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True
                    )
                    
                    for line in process.stdout:
                        if "Pulling from" in line or "Pull complete" in line or "%" in line:
                            print(f"  {line.strip()}")
                            
                    process.wait()
                    
                    if process.returncode == 0:
                        self.log("✓ Image pulled successfully", "SUCCESS")
                    else:
                        self.log(f"✗ Failed to pull image", "ERROR")
                        
            except Exception as e:
                self.log(f"✗ Error pulling image: {e}", "ERROR")
                
    def test_nim_containers(self):
        """Test NIM containers"""
        self.log("\nTesting NIM containers...")
        
        # Start embeddings container
        self.log("\nStarting embeddings container...")
        try:
            subprocess.run(
                ["docker-compose", "up", "-d", "nim-embeddings"],
                cwd=self.base_path,
                capture_output=True
            )
            
            # Wait for container to be ready
            self.log("Waiting for embeddings service to be ready...")
            ready = False
            for i in range(60):
                try:
                    response = requests.get("http://localhost:8001/v1/health/ready", timeout=2)
                    if response.status_code == 200:
                        ready = True
                        break
                except:
                    pass
                time.sleep(2)
                if i % 10 == 0:
                    print(".", end="", flush=True)
                    
            print()
            
            if ready:
                self.log("✓ Embeddings service is ready!", "SUCCESS")
                
                # Test embeddings
                self.log("\nTesting embeddings generation...")
                test_response = requests.post(
                    "http://localhost:8001/v1/embeddings",
                    json={
                        "input": ["Hello, this is a test"],
                        "model": "nvidia/nv-embedqa-e5-v5"
                    }
                )
                
                if test_response.status_code == 200:
                    data = test_response.json()
                    if "data" in data and len(data["data"]) > 0:
                        embedding_dim = len(data["data"][0]["embedding"])
                        self.log(f"✓ Embeddings working! Dimension: {embedding_dim}", "SUCCESS")
                    else:
                        self.log("✗ Unexpected response format", "ERROR")
                else:
                    self.log(f"✗ Embeddings test failed: {test_response.status_code}", "ERROR")
                    
            else:
                self.log("✗ Embeddings service failed to start", "ERROR")
                self.log("Check logs: docker logs nim-embeddings", "INFO")
                
        except Exception as e:
            self.log(f"✗ Error testing embeddings: {e}", "ERROR")
            
    def show_commands(self):
        """Show useful Docker commands"""
        self.log("\n" + "="*60)
        self.log("Useful Docker Commands")
        self.log("="*60)
        
        commands = [
            ("View running containers", "docker ps"),
            ("View all containers", "docker ps -a"),
            ("View container logs", "docker logs nim-embeddings"),
            ("Stop embeddings container", "docker-compose stop nim-embeddings"),
            ("Start embeddings container", "docker-compose up -d nim-embeddings"),
            ("Remove containers", "docker-compose down"),
            ("Start Llama 70B (22GB VRAM)", "docker-compose up nim-generation-70b"),
            ("View Docker disk usage", "docker system df"),
            ("Clean up unused images", "docker system prune -a")
        ]
        
        for desc, cmd in commands:
            self.log(f"{desc}:")
            self.log(f"  {cmd}", "INFO")
            
    def run(self):
        """Main setup process"""
        self.log("="*60)
        self.log("NVIDIA NIM Container Setup")
        self.log("="*60)
        
        # Check prerequisites
        issues = self.check_prerequisites()
        
        if issues:
            self.log("\n✗ Prerequisites not met:", "ERROR")
            for issue in issues:
                self.log(f"  - {issue}", "ERROR")
                
            if "Docker is not installed" in str(issues):
                self.log("\nTo install Docker Desktop:")
                self.log("1. Download from https://www.docker.com/products/docker-desktop")
                self.log("2. Install and restart your computer")
                self.log("3. Run this script again")
                
            return False
            
        # Check NGC key
        has_key = self.check_ngc_key()
        
        if not has_key:
            self.log("\nCannot proceed without NGC API key", "WARNING")
            self.log("You can add it later to .env file and run this script again")
            return False
            
        # Pull images
        response = input("\nDo you want to download NIM Docker images? (y/n): ").lower()
        if response == 'y':
            self.pull_nim_images()
            
        # Test containers
        response = input("\nDo you want to test the embeddings container? (y/n): ").lower()
        if response == 'y':
            self.test_nim_containers()
            
        # Show commands
        self.show_commands()
        
        self.log("\n" + "="*60)
        self.log("Setup complete!")
        self.log("="*60)
        self.log("\nNIM containers are ready to use with the AI Assistant")
        self.log("The startup script will automatically start the embeddings container")
        self.log("Llama 70B must be started manually due to high VRAM usage")
        
        return True

if __name__ == "__main__":
    setup = NIMSetup()
    setup.run()
    
    input("\nPress Enter to exit...")