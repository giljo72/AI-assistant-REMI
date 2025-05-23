#!/usr/bin/env python3
"""
AI Assistant Model Installation Helper
Installs all required Ollama models and checks Docker containers
"""

import subprocess
import requests
import time
import sys
from datetime import datetime

class ModelInstaller:
    def __init__(self):
        self.ollama_models = [
            {
                "name": "mistral-nemo:latest",
                "size": "7GB",
                "purpose": "Quick chat and drafting"
            },
            {
                "name": "qwen2.5:32b-instruct-q4_K_M",
                "size": "19GB",
                "purpose": "Advanced reasoning and analysis"
            },
            {
                "name": "llama3.1:70b-instruct-q4_K_M",
                "size": "40GB",
                "purpose": "Complex queries and deep analysis"
            }
        ]
        
        self.nim_containers = [
            {
                "name": "nim-embeddings",
                "image": "nvcr.io/nim/nvidia/nv-embedqa-e5-v5:latest",
                "port": 8001,
                "purpose": "Document embeddings and RAG"
            },
            {
                "name": "nim-generation-70b",
                "image": "nvcr.io/nim/meta/llama-3.1-70b-instruct:latest",
                "port": 8000,
                "purpose": "Deep business analysis (22GB VRAM)"
            }
        ]
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def get_installed_models(self):
        """Get list of installed Ollama models"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                return [m["name"] for m in response.json().get("models", [])]
        except:
            pass
        return []
        
    def pull_model(self, model_name):
        """Pull an Ollama model"""
        self.log(f"Pulling {model_name}...")
        
        try:
            # Start the pull
            response = requests.post(
                "http://localhost:11434/api/pull",
                json={"name": model_name},
                stream=True
            )
            
            last_percent = -1
            for line in response.iter_lines():
                if line:
                    try:
                        data = line.decode('utf-8')
                        import json
                        status = json.loads(data)
                        
                        if "status" in status:
                            if "total" in status and "completed" in status:
                                percent = int((status["completed"] / status["total"]) * 100)
                                if percent != last_percent and percent % 10 == 0:
                                    print(f"  Progress: {percent}%")
                                    last_percent = percent
                            elif status["status"] == "success":
                                self.log(f"✓ Successfully pulled {model_name}", "SUCCESS")
                                return True
                    except:
                        pass
                        
        except Exception as e:
            self.log(f"✗ Failed to pull {model_name}: {e}", "ERROR")
            return False
            
    def check_docker(self):
        """Check if Docker is available"""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True)
            return result.returncode == 0
        except:
            return False
            
    def check_ngc_key(self):
        """Check if NGC API key is configured"""
        try:
            with open(".env", "r") as f:
                content = f.read()
                return "NGC_API_KEY=" in content and "your_key_here" not in content
        except:
            return False
            
    def run(self):
        """Main installation process"""
        self.log("=" * 60)
        self.log("AI Assistant Model Installation")
        self.log("=" * 60)
        
        # Check Ollama
        self.log("\nChecking Ollama service...")
        if not self.check_ollama():
            self.log("✗ Ollama is not running!", "ERROR")
            self.log("Please start Ollama first: ollama serve", "ERROR")
            return False
            
        self.log("✓ Ollama is running", "SUCCESS")
        
        # Check and install Ollama models
        self.log("\nChecking Ollama models...")
        installed = self.get_installed_models()
        
        for model in self.ollama_models:
            model_name = model["name"]
            if any(model_name in inst for inst in installed):
                self.log(f"✓ {model_name} - Already installed ({model['purpose']})", "SUCCESS")
            else:
                self.log(f"✗ {model_name} - Not installed ({model['size']}, {model['purpose']})", "WARNING")
                
                response = input(f"\nInstall {model_name}? (y/n): ").lower()
                if response == 'y':
                    if self.pull_model(model_name):
                        self.log(f"Installation of {model_name} completed", "SUCCESS")
                    else:
                        self.log(f"Installation of {model_name} failed", "ERROR")
                        
        # Check Docker and NIM
        self.log("\n" + "=" * 60)
        self.log("NVIDIA NIM Container Setup")
        self.log("=" * 60)
        
        if not self.check_docker():
            self.log("✗ Docker is not installed or not running", "ERROR")
            self.log("Please install Docker Desktop from https://www.docker.com/products/docker-desktop", "ERROR")
            return
            
        self.log("✓ Docker is available", "SUCCESS")
        
        # Check NGC API key
        if not self.check_ngc_key():
            self.log("\n✗ NGC API key not configured", "WARNING")
            self.log("To use NVIDIA NIM models:")
            self.log("1. Get an API key from https://ngc.nvidia.com")
            self.log("2. Add it to the .env file: NGC_API_KEY=your_key_here")
        else:
            self.log("✓ NGC API key is configured", "SUCCESS")
            
        # Show NIM container commands
        self.log("\nTo start NVIDIA NIM containers:")
        self.log("1. For embeddings (2GB VRAM):")
        self.log("   docker-compose up -d nim-embeddings")
        self.log("\n2. For Llama 70B (22GB VRAM):")
        self.log("   docker-compose up nim-generation-70b")
        
        self.log("\n" + "=" * 60)
        self.log("Model installation check complete!")
        self.log("=" * 60)
        
        # Summary
        self.log("\nSummary:")
        self.log("- Ollama models: Check the installation status above")
        self.log("- NVIDIA NIM: Requires Docker and NGC API key")
        self.log("- Total VRAM needed: 24GB for all models")
        self.log("- The system will manage VRAM automatically")

if __name__ == "__main__":
    installer = ModelInstaller()
    installer.run()
    
    input("\nPress Enter to exit...")