#!/usr/bin/env python3
"""
Check status of all AI models for the multi-model architecture
"""

import requests
import json
import subprocess
import os

def check_ollama_models():
    """Check installed Ollama models"""
    print("=== Ollama Models ===")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            
            # Required models
            required = {
                "mistral-nemo": False,
                "deepseek-coder-v2": False,
                "qwen2.5:32b": False
            }
            
            # Check installed models
            for model in models:
                name = model.get("name", "")
                for req in required:
                    if req in name:
                        required[req] = True
                        print(f"✓ {name} - {model.get('size', 0) / 1e9:.1f}GB")
            
            # Report missing
            print("\nMissing Ollama models:")
            if not required["deepseek-coder-v2"]:
                print("✗ DeepSeek-Coder-V2 - Run: ollama pull deepseek-coder-v2:16b-lite-instruct-q4_K_M")
            if not required["qwen2.5:32b"]:
                print("✗ Qwen 2.5 32B - Run: ollama pull qwen2.5:32b-instruct-q4_K_M")
            if all(required.values()):
                print("All required Ollama models are installed!")
                
        else:
            print("✗ Ollama is not running on port 11434")
    except Exception as e:
        print(f"✗ Error checking Ollama: {e}")

def check_nim_containers():
    """Check NVIDIA NIM Docker containers"""
    print("\n=== NVIDIA NIM Containers ===")
    try:
        # Check docker containers
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "json"],
            capture_output=True,
            text=True
        )
        
        containers = {}
        for line in result.stdout.strip().split('\n'):
            if line:
                container = json.loads(line)
                name = container.get("Names", "")
                if "nim-" in name:
                    containers[name] = container.get("State", "")
        
        # Check required containers
        required = {
            "nim-embeddings": "8001",
            "nim-generation-70b": "8000"
        }
        
        for name, port in required.items():
            if name in containers:
                state = containers[name]
                if state == "running":
                    # Check if responding
                    try:
                        resp = requests.get(f"http://localhost:{port}/v1/health/ready", timeout=2)
                        if resp.status_code == 200:
                            print(f"✓ {name} - Running and healthy on port {port}")
                        else:
                            print(f"⚠ {name} - Running but not ready on port {port}")
                    except:
                        print(f"⚠ {name} - Container running but API not responding on port {port}")
                else:
                    print(f"✗ {name} - Container exists but {state}")
            else:
                print(f"✗ {name} - Container not found")
                
        print("\nTo start NIM containers:")
        print("1. Set NGC_API_KEY environment variable")
        print("2. Run: docker-compose up -d nim-embeddings")
        print("3. For 70B model: docker-compose up nim-generation-70b")
        
    except FileNotFoundError:
        print("✗ Docker not found. NVIDIA NIM requires Docker.")
    except Exception as e:
        print(f"✗ Error checking Docker: {e}")

def check_backend_integration():
    """Check if backend model endpoints are working"""
    print("\n=== Backend Integration ===")
    try:
        response = requests.get("http://localhost:8000/api/models/status")
        if response.status_code == 200:
            print("✓ Model orchestrator API is accessible")
            models = response.json()
            print(f"  Found {len(models)} configured models")
            
            # Check memory status
            mem_response = requests.get("http://localhost:8000/api/models/memory")
            if mem_response.status_code == 200:
                memory = mem_response.json()
                print(f"✓ VRAM Status: {memory['used_vram_gb']:.1f}GB / {memory['total_vram_gb']}GB")
                print(f"  Loaded models: {', '.join(memory['loaded_models']) or 'None'}")
        else:
            print("✗ Backend API not responding on port 8000")
    except Exception as e:
        print(f"✗ Error checking backend: {e}")

def main():
    print("AI Assistant Model Status Check")
    print("=" * 40)
    
    check_ollama_models()
    check_nim_containers()
    check_backend_integration()
    
    print("\n" + "=" * 40)
    print("Summary:")
    print("- Ollama models can be installed with the install_all_models.bat script")
    print("- NVIDIA NIM containers require NGC API key and docker-compose")
    print("- Backend integration requires the FastAPI server to be running")

if __name__ == "__main__":
    main()