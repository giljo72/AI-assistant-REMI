#!/usr/bin/env python3
"""
AI Assistant Startup Launcher
Elegant GUI for monitoring and starting all required services
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import time
import sys
import os
import psutil
import requests
from pathlib import Path
from datetime import datetime

class ServiceStatus:
    CHECKING = "checking"
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    ERROR = "error"

class AIAssistantLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant Launcher")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Set dark theme colors
        self.bg_color = "#1a1a1a"
        self.fg_color = "#ffffff"
        self.accent_color = "#FFC000"
        self.success_color = "#4CAF50"
        self.error_color = "#f44336"
        self.warning_color = "#ff9800"
        
        self.root.configure(bg=self.bg_color)
        
        # Service definitions
        self.services = {
            "PostgreSQL": {
                "status": ServiceStatus.CHECKING,
                "check_func": self.check_postgres,
                "start_func": self.start_postgres,
                "description": "Database for document storage",
                "required": True
            },
            "Ollama": {
                "status": ServiceStatus.CHECKING,
                "check_func": self.check_ollama,
                "start_func": self.start_ollama,
                "description": "Local AI model service",
                "required": True
            },
            "Docker": {
                "status": ServiceStatus.CHECKING,
                "check_func": self.check_docker,
                "start_func": self.start_docker,
                "description": "Container platform for NIM models",
                "required": False
            },
            "NIM Embeddings": {
                "status": ServiceStatus.CHECKING,
                "check_func": self.check_nim_embeddings,
                "start_func": self.start_nim_embeddings,
                "description": "NVIDIA embeddings for RAG",
                "required": False
            }
        }
        
        self.service_widgets = {}
        self.is_checking = False
        self.all_services_ready = False
        
        self.setup_ui()
        self.start_checking()
        
    def setup_ui(self):
        """Create the user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            title_frame,
            text="AI Assistant Startup",
            font=("Segoe UI", 24, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Checking required services...",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.fg_color
        )
        subtitle_label.pack()
        self.subtitle_label = subtitle_label
        
        # Services frame
        services_frame = tk.Frame(self.root, bg=self.bg_color)
        services_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create service status widgets
        for i, (service_name, service_info) in enumerate(self.services.items()):
            service_frame = tk.Frame(services_frame, bg=self.bg_color)
            service_frame.pack(fill="x", pady=5)
            
            # Status indicator (circle)
            status_canvas = tk.Canvas(
                service_frame,
                width=20,
                height=20,
                bg=self.bg_color,
                highlightthickness=0
            )
            status_canvas.pack(side="left", padx=(0, 10))
            
            # Service info
            info_frame = tk.Frame(service_frame, bg=self.bg_color)
            info_frame.pack(side="left", fill="x", expand=True)
            
            name_label = tk.Label(
                info_frame,
                text=service_name,
                font=("Segoe UI", 12, "bold"),
                bg=self.bg_color,
                fg=self.fg_color,
                anchor="w"
            )
            name_label.pack(fill="x")
            
            desc_label = tk.Label(
                info_frame,
                text=service_info["description"],
                font=("Segoe UI", 9),
                bg=self.bg_color,
                fg="#999999",
                anchor="w"
            )
            desc_label.pack(fill="x")
            
            # Status text
            status_label = tk.Label(
                service_frame,
                text="Checking...",
                font=("Segoe UI", 10),
                bg=self.bg_color,
                fg=self.fg_color,
                width=15,
                anchor="e"
            )
            status_label.pack(side="right")
            
            self.service_widgets[service_name] = {
                "canvas": status_canvas,
                "status_label": status_label,
                "circle": None
            }
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Retry button
        self.retry_button = tk.Button(
            button_frame,
            text="Retry Failed Services",
            font=("Segoe UI", 12),
            bg=self.warning_color,
            fg="white",
            activebackground="#e68900",
            activeforeground="white",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.retry_services,
            state="disabled"
        )
        self.retry_button.pack(side="left", padx=(0, 10))
        
        # Start button
        self.start_button = tk.Button(
            button_frame,
            text="Start AI Assistant",
            font=("Segoe UI", 12, "bold"),
            bg=self.success_color,
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            bd=0,
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.start_assistant,
            state="disabled"
        )
        self.start_button.pack(side="right")
        
        # Exit button
        self.exit_button = tk.Button(
            button_frame,
            text="Exit",
            font=("Segoe UI", 12),
            bg="#555555",
            fg="white",
            activebackground="#666666",
            activeforeground="white",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.root.quit
        )
        self.exit_button.pack(side="right", padx=(0, 10))
        
        # Log area
        log_frame = tk.Frame(self.root, bg=self.bg_color)
        log_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.log_text = tk.Text(
            log_frame,
            height=6,
            bg="#0a0a0a",
            fg="#00ff00",
            font=("Consolas", 9),
            wrap="word",
            bd=1,
            relief="solid"
        )
        self.log_text.pack(fill="x")
        
        # Configure text tags for different log levels
        self.log_text.tag_config("info", foreground="#00ff00")
        self.log_text.tag_config("warning", foreground="#ff9800")
        self.log_text.tag_config("error", foreground="#f44336")
        self.log_text.tag_config("success", foreground="#4CAF50")
        
    def log(self, message, level="info"):
        """Add message to log area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n", level)
        self.log_text.see("end")
        
    def update_service_status(self, service_name, status):
        """Update the visual status of a service"""
        if service_name not in self.service_widgets:
            return
            
        widgets = self.service_widgets[service_name]
        canvas = widgets["canvas"]
        status_label = widgets["status_label"]
        
        # Remove old circle
        if widgets["circle"]:
            canvas.delete(widgets["circle"])
        
        # Set colors and text based on status
        if status == ServiceStatus.CHECKING:
            color = "#666666"
            text = "Checking..."
        elif status == ServiceStatus.RUNNING:
            color = self.success_color
            text = "Running"
        elif status == ServiceStatus.STOPPED:
            color = self.error_color
            text = "Stopped"
        elif status == ServiceStatus.STARTING:
            color = self.warning_color
            text = "Starting..."
        elif status == ServiceStatus.ERROR:
            color = self.error_color
            text = "Error"
        else:
            color = "#666666"
            text = "Unknown"
        
        # Draw new circle
        widgets["circle"] = canvas.create_oval(
            2, 2, 18, 18,
            fill=color,
            outline=color
        )
        
        # Update status text
        status_label.config(text=text)
        
        # Update service status
        self.services[service_name]["status"] = status
        
    def check_postgres(self):
        """Check if PostgreSQL is running"""
        try:
            # Check Windows service
            result = subprocess.run(
                ["sc", "query", "postgresql-x64-17"],
                capture_output=True,
                text=True
            )
            return "RUNNING" in result.stdout
        except:
            return False
            
    def start_postgres(self):
        """Start PostgreSQL service"""
        try:
            subprocess.run(["net", "start", "postgresql-x64-17"], check=True)
            return True
        except:
            try:
                subprocess.run(["net", "start", "postgresql"], check=True)
                return True
            except:
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
        try:
            subprocess.Popen(["ollama", "serve"], shell=True)
            time.sleep(3)
            return True
        except:
            return False
            
    def check_docker(self):
        """Check if Docker is running"""
        try:
            result = subprocess.run(["docker", "info"], capture_output=True)
            return result.returncode == 0
        except:
            return False
            
    def start_docker(self):
        """Start Docker Desktop"""
        try:
            docker_paths = [
                r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
                r"C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"
            ]
            
            for path in docker_paths:
                if Path(path).exists():
                    subprocess.Popen([path])
                    return True
            return False
        except:
            return False
            
    def check_nim_embeddings(self):
        """Check if NIM embeddings container is running"""
        if not self.check_docker():
            return False
            
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=nim-embeddings", "--format", "{{.Names}}"],
                capture_output=True,
                text=True
            )
            return "nim-embeddings" in result.stdout
        except:
            return False
            
    def start_nim_embeddings(self):
        """Start NIM embeddings container"""
        try:
            subprocess.run(
                ["docker-compose", "up", "-d", "nim-embeddings"],
                cwd=Path(__file__).parent.parent
            )
            return True
        except:
            return False
            
    def check_all_services(self):
        """Check all services and update UI"""
        self.log("Starting service checks...", "info")
        all_ready = True
        has_errors = False
        
        for service_name, service_info in self.services.items():
            self.update_service_status(service_name, ServiceStatus.CHECKING)
            
            if service_info["check_func"]():
                self.update_service_status(service_name, ServiceStatus.RUNNING)
                self.log(f"{service_name} is running", "success")
            else:
                if service_info["required"]:
                    all_ready = False
                    has_errors = True
                self.update_service_status(service_name, ServiceStatus.STOPPED)
                self.log(f"{service_name} is not running", "warning" if not service_info["required"] else "error")
        
        self.all_services_ready = all_ready
        self.is_checking = False
        
        # Update UI state
        if all_ready:
            self.subtitle_label.config(text="All required services are running!")
            self.start_button.config(state="normal")
            self.retry_button.config(state="disabled")
            self.log("All required services are ready!", "success")
        else:
            self.subtitle_label.config(text="Some required services are not running")
            self.start_button.config(state="disabled")
            self.retry_button.config(state="normal")
            
    def start_checking(self):
        """Start checking services in a separate thread"""
        if not self.is_checking:
            self.is_checking = True
            thread = threading.Thread(target=self.check_all_services)
            thread.daemon = True
            thread.start()
            
    def retry_services(self):
        """Retry starting failed services"""
        self.log("Attempting to start services...", "info")
        self.retry_button.config(state="disabled")
        
        def retry_thread():
            for service_name, service_info in self.services.items():
                if service_info["status"] == ServiceStatus.STOPPED:
                    self.update_service_status(service_name, ServiceStatus.STARTING)
                    self.log(f"Starting {service_name}...", "info")
                    
                    if service_info["start_func"]():
                        time.sleep(3)  # Give service time to start
                        if service_info["check_func"]():
                            self.update_service_status(service_name, ServiceStatus.RUNNING)
                            self.log(f"{service_name} started successfully", "success")
                        else:
                            self.update_service_status(service_name, ServiceStatus.ERROR)
                            self.log(f"{service_name} failed to start", "error")
                    else:
                        self.update_service_status(service_name, ServiceStatus.ERROR)
                        self.log(f"Could not start {service_name}", "error")
            
            # Recheck all services
            self.check_all_services()
        
        thread = threading.Thread(target=retry_thread)
        thread.daemon = True
        thread.start()
        
    def start_assistant(self):
        """Start the AI Assistant"""
        self.log("Starting AI Assistant...", "info")
        self.start_button.config(state="disabled")
        
        # Start backend
        self.log("Starting Backend API...", "info")
        backend_path = Path(__file__).parent.parent / "backend"
        venv_python = Path(__file__).parent.parent / "venv_nemo" / "Scripts" / "python.exe"
        
        subprocess.Popen(
            [str(venv_python), "run_server.py"],
            cwd=str(backend_path),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        time.sleep(3)
        
        # Start frontend
        self.log("Starting Frontend...", "info")
        frontend_path = Path(__file__).parent.parent / "frontend"
        
        subprocess.Popen(
            ["cmd", "/c", "npm", "run", "dev"],
            cwd=str(frontend_path),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        time.sleep(5)
        
        # Open browser
        self.log("Opening browser...", "info")
        import webbrowser
        webbrowser.open("http://localhost:5173")
        
        self.log("AI Assistant started successfully!", "success")
        self.subtitle_label.config(text="AI Assistant is running!")
        
        # Change start button to "Running"
        self.start_button.config(text="Running", bg="#666666", state="disabled")
        
def main():
    root = tk.Tk()
    app = AIAssistantLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()