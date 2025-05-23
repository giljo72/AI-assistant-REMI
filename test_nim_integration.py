#!/usr/bin/env python3
"""
Test script for NVIDIA NIM integration
Tests Docker setup, containers, and API endpoints
"""

import subprocess
import requests
import json
import time
import sys
import os
from pathlib import Path

class NIMIntegrationTester:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def log(self, message, level="INFO"):
        prefix = {
            "INFO": "[INFO]",
            "SUCCESS": "[✓]",
            "WARNING": "[!]",
            "ERROR": "[✗]"
        }
        print(f"{prefix.get(level, '[INFO]')} {message}")
        
    def run_command(self, command, check=True):
        """Run a command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
            
    def test_docker_setup(self):
        """Test Docker installation and configuration"""
        self.log("Testing Docker setup...", "INFO")
        
        # Check Docker is installed
        success, stdout, stderr = self.run_command("docker --version", check=False)
        if not success:
            self.errors.append("Docker is not installed or not in PATH")
            return False
            
        self.log(f"Docker version: {stdout.strip()}", "SUCCESS")
        
        # Check Docker daemon is running
        success, stdout, stderr = self.run_command("docker ps", check=False)
        if not success:
            self.errors.append("Docker daemon is not running")
            return False
            
        self.log("Docker daemon is running", "SUCCESS")
        
        # Check docker-compose
        success, stdout, stderr = self.run_command("docker-compose --version", check=False)
        if not success:
            self.errors.append("docker-compose is not installed")
            return False
            
        self.log(f"docker-compose version: {stdout.strip()}", "SUCCESS")
        
        # Check NVIDIA runtime
        success, stdout, stderr = self.run_command("docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi", check=False)
        if not success:
            self.warnings.append("NVIDIA Docker runtime not available - GPU acceleration disabled")
        else:
            self.log("NVIDIA Docker runtime is available", "SUCCESS")
            
        return True
        
    def test_nim_containers(self):
        """Test NIM containers status"""
        self.log("Testing NIM containers...", "INFO")
        
        # Get all running containers
        success, stdout, stderr = self.run_command("docker ps --format json")
        if not success:
            self.errors.append("Failed to list Docker containers")
            return False
            
        containers = {}
        for line in stdout.strip().split('\n'):
            if line:
                try:
                    container = json.loads(line)
                    name = container.get('Names', '')
                    if 'nim-embeddings' in name or 'nim-llm' in name:
                        containers[name] = container
                except:
                    pass
                    
        # Check nim-embeddings container
        if any('nim-embeddings' in name for name in containers):
            self.log("nim-embeddings container is running", "SUCCESS")
            
            # Test embeddings API
            try:
                response = requests.get("http://localhost:8001/v1/models", timeout=5)
                if response.status_code == 200:
                    self.log("nim-embeddings API is responding", "SUCCESS")
                    models = response.json()
                    self.log(f"Available embedding models: {models}", "INFO")
                else:
                    self.warnings.append(f"nim-embeddings API returned status {response.status_code}")
            except Exception as e:
                self.warnings.append(f"Failed to connect to nim-embeddings API: {e}")
        else:
            self.warnings.append("nim-embeddings container is not running")
            
        # Check nim-llm container (optional)
        if any('nim-llm' in name for name in containers):
            self.log("nim-llm container is running", "SUCCESS")
            
            # Test LLM API
            try:
                response = requests.get("http://localhost:8002/v1/models", timeout=5)
                if response.status_code == 200:
                    self.log("nim-llm API is responding", "SUCCESS")
                else:
                    self.warnings.append(f"nim-llm API returned status {response.status_code}")
            except Exception as e:
                self.warnings.append(f"Failed to connect to nim-llm API: {e}")
        else:
            self.log("nim-llm container is not running (optional)", "INFO")
            
        return True
        
    def test_ngc_api_key(self):
        """Test NGC API key configuration"""
        self.log("Testing NGC API key configuration...", "INFO")
        
        # Check .env file
        env_path = Path("/mnt/f/assistant/.env")
        if env_path.exists():
            with open(env_path) as f:
                content = f.read()
                if "NGC_API_KEY=" in content and not "NGC_API_KEY=$" in content:
                    self.log("NGC API key is configured in .env", "SUCCESS")
                else:
                    self.warnings.append("NGC API key not found in .env file")
        else:
            self.warnings.append(".env file not found")
            
        # Check environment variable
        if os.getenv("NGC_API_KEY"):
            self.log("NGC API key is set in environment", "SUCCESS")
        else:
            self.log("NGC API key not set in environment (will use .env)", "INFO")
            
        return True
        
    def test_docker_compose_file(self):
        """Test docker-compose.yml configuration"""
        self.log("Testing docker-compose.yml...", "INFO")
        
        compose_path = Path("/mnt/f/assistant/docker-compose.yml")
        if not compose_path.exists():
            self.errors.append("docker-compose.yml not found")
            return False
            
        self.log("docker-compose.yml exists", "SUCCESS")
        
        # Validate compose file
        success, stdout, stderr = self.run_command("docker-compose config", check=False)
        if not success:
            self.errors.append(f"docker-compose.yml validation failed: {stderr}")
            return False
            
        self.log("docker-compose.yml is valid", "SUCCESS")
        
        # Check for NIM services
        with open(compose_path) as f:
            content = f.read()
            if "nim-embeddings" in content:
                self.log("nim-embeddings service defined", "SUCCESS")
            else:
                self.warnings.append("nim-embeddings service not found in docker-compose.yml")
                
            if "nvcr.io/nim/nvidia/nv-embedqa-e5-v5" in content:
                self.log("Correct NIM embedding image configured", "SUCCESS")
            else:
                self.warnings.append("NIM embedding image not correctly configured")
                
        return True
        
    def test_backend_integration(self):
        """Test backend integration with NIM"""
        self.log("Testing backend NIM integration...", "INFO")
        
        # Check if backend is running
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=5)
            if response.status_code == 200:
                self.log("Backend API is running", "SUCCESS")
            else:
                self.warnings.append("Backend API not responding correctly")
                return True
        except:
            self.log("Backend API not running - skipping integration tests", "INFO")
            return True
            
        # Test embedding endpoint
        try:
            response = requests.post(
                "http://localhost:8000/api/semantic-search/embed",
                json={"text": "test embedding"},
                timeout=10
            )
            if response.status_code == 200:
                self.log("Backend embedding endpoint working", "SUCCESS")
            else:
                self.warnings.append(f"Backend embedding endpoint returned {response.status_code}")
        except Exception as e:
            self.warnings.append(f"Failed to test embedding endpoint: {e}")
            
        return True
        
    def run_tests(self):
        """Run all integration tests"""
        self.log("Starting NIM Integration Tests", "INFO")
        self.log("=" * 50, "INFO")
        
        tests = [
            ("Docker Setup", self.test_docker_setup),
            ("NGC API Key", self.test_ngc_api_key),
            ("Docker Compose", self.test_docker_compose_file),
            ("NIM Containers", self.test_nim_containers),
            ("Backend Integration", self.test_backend_integration)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            self.log(f"\nTesting {test_name}...", "INFO")
            try:
                if not test_func():
                    all_passed = False
            except Exception as e:
                self.errors.append(f"{test_name} failed with exception: {e}")
                all_passed = False
                
        # Summary
        self.log("\n" + "=" * 50, "INFO")
        self.log("Test Summary:", "INFO")
        
        if self.errors:
            self.log(f"Errors: {len(self.errors)}", "ERROR")
            for error in self.errors:
                self.log(f"  - {error}", "ERROR")
                
        if self.warnings:
            self.log(f"Warnings: {len(self.warnings)}", "WARNING")
            for warning in self.warnings:
                self.log(f"  - {warning}", "WARNING")
                
        if all_passed and not self.errors:
            self.log("\nAll critical tests passed! NIM integration is ready.", "SUCCESS")
            
            self.log("\nNext steps:", "INFO")
            self.log("1. Run: python start_assistant.py", "INFO")
            self.log("2. The script will automatically start NIM containers", "INFO")
            self.log("3. Access the UI at http://localhost:3000", "INFO")
        else:
            self.log("\nSome tests failed. Please fix the errors above.", "ERROR")
            
            if not any('Docker' in e for e in self.errors):
                self.log("\nTo start NIM containers manually:", "INFO")
                self.log("docker-compose up -d nim-embeddings", "INFO")
                
        return all_passed and not self.errors


if __name__ == "__main__":
    tester = NIMIntegrationTester()
    success = tester.run_tests()
    sys.exit(0 if success else 1)