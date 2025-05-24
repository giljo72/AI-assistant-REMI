#!/usr/bin/env python3
"""
AI Assistant Debug Monitor
Provides real-time color-coded monitoring of all services
"""

import os
import sys
import time
import requests
import psutil
import subprocess
from datetime import datetime
from pathlib import Path
import threading
import signal
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for Windows console colors
colorama.init()

class DebugMonitor:
    def __init__(self):
        self.running = True
        self.base_path = Path(__file__).parent
        self.log_file = self.base_path / "logs" / f"monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Service status
        self.services = {
            "PostgreSQL": {"status": "UNKNOWN", "last_check": None, "port": 5432},
            "Ollama": {"status": "UNKNOWN", "last_check": None, "port": 11434, "url": "http://localhost:11434/api/version"},
            "Backend": {"status": "UNKNOWN", "last_check": None, "port": 8000, "url": "http://localhost:8000/api/health/ping"},
            "Frontend": {"status": "UNKNOWN", "last_check": None, "port": 5173, "url": "http://localhost:5173"},
        }
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        self.log("SHUTDOWN", "Received shutdown signal. Stopping monitor...")
        self.running = False
        sys.exit(0)
        
    def log(self, level, message):
        """Log with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color mapping
        colors = {
            "SUCCESS": Fore.GREEN,
            "ERROR": Fore.RED,
            "WARNING": Fore.YELLOW,
            "INFO": Fore.CYAN,
            "SHUTDOWN": Fore.MAGENTA,
        }
        
        color = colors.get(level, Fore.WHITE)
        
        # Print to console with color
        print(f"{color}[{timestamp}] [{level}] {message}{Style.RESET_ALL}")
        
        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
            
    def check_port(self, port):
        """Check if a port is in use"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False
        
    def check_postgres(self):
        """Check PostgreSQL status"""
        try:
            # Windows service check
            result = subprocess.run(
                ["sc", "query", "postgresql-x64-17"],
                capture_output=True,
                text=True
            )
            if "RUNNING" in result.stdout:
                return "RUNNING"
            
            # Try alternative service name
            result = subprocess.run(
                ["sc", "query", "postgresql"],
                capture_output=True,
                text=True
            )
            if "RUNNING" in result.stdout:
                return "RUNNING"
                
            return "STOPPED"
        except:
            return "ERROR"
            
    def check_http_service(self, url, timeout=2):
        """Check if an HTTP service is responsive"""
        try:
            response = requests.get(url, timeout=timeout)
            return "RUNNING" if response.status_code in [200, 404] else "ERROR"
        except requests.exceptions.ConnectionError:
            return "STOPPED"
        except requests.exceptions.Timeout:
            return "TIMEOUT"
        except:
            return "ERROR"
            
    def check_ollama(self):
        """Check Ollama service"""
        # First check if process is running
        for proc in psutil.process_iter(['name']):
            try:
                if 'ollama' in proc.info['name'].lower():
                    # Process found, check API
                    return self.check_http_service(self.services["Ollama"]["url"])
            except:
                pass
        return "STOPPED"
        
    def update_status(self):
        """Update status of all services"""
        # PostgreSQL
        old_status = self.services["PostgreSQL"]["status"]
        new_status = self.check_postgres()
        self.services["PostgreSQL"]["status"] = new_status
        if old_status != new_status:
            level = "SUCCESS" if new_status == "RUNNING" else "ERROR"
            self.log(level, f"PostgreSQL: {old_status} -> {new_status}")
            
        # Ollama
        old_status = self.services["Ollama"]["status"]
        new_status = self.check_ollama()
        self.services["Ollama"]["status"] = new_status
        if old_status != new_status:
            level = "SUCCESS" if new_status == "RUNNING" else "ERROR"
            self.log(level, f"Ollama: {old_status} -> {new_status}")
            
        # Backend
        old_status = self.services["Backend"]["status"]
        new_status = self.check_http_service(self.services["Backend"]["url"])
        self.services["Backend"]["status"] = new_status
        if old_status != new_status:
            level = "SUCCESS" if new_status == "RUNNING" else "ERROR"
            self.log(level, f"Backend API: {old_status} -> {new_status}")
            
        # Frontend
        old_status = self.services["Frontend"]["status"]
        if self.check_port(5173):
            new_status = "RUNNING"
        else:
            new_status = "STOPPED"
        self.services["Frontend"]["status"] = new_status
        if old_status != new_status:
            level = "SUCCESS" if new_status == "RUNNING" else "ERROR"
            self.log(level, f"Frontend: {old_status} -> {new_status}")
            
    def display_dashboard(self):
        """Display current status dashboard"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}AI Assistant Debug Monitor - Press Ctrl+C to exit")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print()
        
        # Service status table
        print(f"{Fore.WHITE}Service Status:")
        print(f"{'-'*50}")
        
        for service, info in self.services.items():
            status = info["status"]
            
            # Color based on status
            if status == "RUNNING":
                status_color = Fore.GREEN
                symbol = "✓"
            elif status == "STOPPED":
                status_color = Fore.RED
                symbol = "✗"
            elif status == "TIMEOUT":
                status_color = Fore.YELLOW
                symbol = "⚠"
            else:
                status_color = Fore.RED
                symbol = "!"
                
            print(f"{service:<15} {status_color}[{symbol}] {status:<10}{Style.RESET_ALL}", end="")
            
            # Add URL/port info
            if "url" in info:
                url = info["url"].replace("http://localhost", "")
                print(f" {Fore.DARK_GRAY}{url}{Style.RESET_ALL}")
            else:
                print(f" {Fore.DARK_GRAY}Port {info['port']}{Style.RESET_ALL}")
                
        print(f"{'-'*50}")
        print()
        
        # Recent logs
        print(f"{Fore.WHITE}Recent Activity:")
        print(f"{'-'*50}")
        
        # Show last 10 lines from log file
        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    if "[SUCCESS]" in line:
                        print(f"{Fore.GREEN}{line.strip()}{Style.RESET_ALL}")
                    elif "[ERROR]" in line:
                        print(f"{Fore.RED}{line.strip()}{Style.RESET_ALL}")
                    elif "[WARNING]" in line:
                        print(f"{Fore.YELLOW}{line.strip()}{Style.RESET_ALL}")
                    elif "[INFO]" in line:
                        print(f"{Fore.CYAN}{line.strip()}{Style.RESET_ALL}")
                    else:
                        print(line.strip())
                        
        print()
        print(f"{Fore.DARK_GRAY}Log file: {self.log_file}{Style.RESET_ALL}")
        
    def run(self):
        """Main monitoring loop"""
        self.log("INFO", "Debug Monitor started")
        
        try:
            while self.running:
                self.update_status()
                self.display_dashboard()
                
                # Check every 2 seconds
                for i in range(20):
                    if not self.running:
                        break
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            self.log("SHUTDOWN", "Monitor stopped by user")
        except Exception as e:
            self.log("ERROR", f"Monitor error: {e}")
        finally:
            print(f"\n{Fore.YELLOW}Monitor stopped. Log saved to: {self.log_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    monitor = DebugMonitor()
    monitor.run()