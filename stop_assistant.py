#!/usr/bin/env python3
"""
AI Assistant Shutdown Script
Stops all running services gracefully
"""

import os
import sys
import subprocess
import psutil
import time
from datetime import datetime

class AIAssistantStopper:
    def __init__(self):
        self.services_to_stop = {
            "Frontend (npm/vite)": {
                "ports": [3000],
                "process_names": ["node", "npm", "vite"]
            },
            "Backend (uvicorn)": {
                "ports": [8000],
                "process_names": ["uvicorn", "python"]
            },
            "Ollama": {
                "ports": [11434],
                "process_names": ["ollama"]
            }
        }
        
    def log(self, message, level="INFO"):
        """Log messages to console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def find_processes_by_port(self, port):
        """Find processes using a specific port"""
        processes = []
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                try:
                    process = psutil.Process(conn.pid)
                    processes.append(process)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return processes
        
    def find_processes_by_name(self, names):
        """Find processes by name"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info.get('cmdline', [])).lower()
                
                for name in names:
                    if name.lower() in proc_name or name.lower() in cmdline:
                        processes.append(proc)
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
        
    def stop_process(self, process):
        """Stop a process gracefully"""
        try:
            self.log(f"Stopping {process.name()} (PID: {process.pid})")
            process.terminate()
            
            # Give it time to terminate gracefully
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if it doesn't terminate
                self.log(f"Force killing {process.name()} (PID: {process.pid})", "WARNING")
                process.kill()
                
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.log(f"Could not stop process: {e}", "ERROR")
            return False
            
    def stop_docker_containers(self):
        """Stop NVIDIA NIM Docker containers"""
        self.log("\nStopping Docker containers...")
        
        try:
            # List NIM containers
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", "name=nim-", "--format", "{{.Names}}"],
                capture_output=True,
                text=True
            )
            
            containers = result.stdout.strip().split('\n')
            containers = [c for c in containers if c]  # Remove empty strings
            
            if containers:
                for container in containers:
                    self.log(f"Stopping container: {container}")
                    subprocess.run(["docker", "stop", container], capture_output=True)
                self.log("Docker containers stopped")
            else:
                self.log("No NIM containers found")
                
        except FileNotFoundError:
            self.log("Docker not found - skipping container shutdown", "WARNING")
        except Exception as e:
            self.log(f"Error stopping containers: {e}", "ERROR")
            
    def run(self):
        """Main shutdown sequence"""
        self.log("=" * 60)
        self.log("AI Assistant Shutdown Sequence")
        self.log("=" * 60)
        
        total_stopped = 0
        
        # Stop each service
        for service_name, config in self.services_to_stop.items():
            self.log(f"\nStopping {service_name}...")
            
            # Find processes by port
            for port in config.get("ports", []):
                processes = self.find_processes_by_port(port)
                for proc in processes:
                    if self.stop_process(proc):
                        total_stopped += 1
                        
            # Find processes by name
            processes = self.find_processes_by_name(config.get("process_names", []))
            
            # Filter to avoid duplicates and system processes
            unique_processes = []
            seen_pids = set()
            
            for proc in processes:
                if proc.pid not in seen_pids:
                    seen_pids.add(proc.pid)
                    # Additional filtering for specific services
                    cmdline = ' '.join(proc.cmdline()).lower()
                    
                    # Skip if it's not related to our services
                    if service_name == "Frontend" and ("vite" not in cmdline and "dev" not in cmdline):
                        continue
                    if service_name == "Backend" and ("uvicorn" not in cmdline and "app.main" not in cmdline):
                        continue
                    if service_name == "Ollama" and "serve" not in cmdline:
                        continue
                        
                    unique_processes.append(proc)
                    
            for proc in unique_processes:
                if self.stop_process(proc):
                    total_stopped += 1
                    
        # Stop Docker containers
        self.stop_docker_containers()
        
        self.log("\n" + "=" * 60)
        self.log(f"Shutdown complete. Stopped {total_stopped} processes.")
        self.log("=" * 60)
        
        # On Windows, pause before closing
        if sys.platform == "win32":
            input("\nPress Enter to close...")

if __name__ == "__main__":
    stopper = AIAssistantStopper()
    stopper.run()