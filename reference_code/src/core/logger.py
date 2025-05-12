# src/core/logger.py
import logging
import os
from datetime import datetime
from pathlib import Path
import json

class Logger:
    """Custom logger with file processing logging capabilities"""
    
    def __init__(self, log_dir="data/logs", process_log_file="_process_log.txt"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.process_log_path = self.log_dir / process_log_file
        
        # Setup standard Python logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / "app.log"),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("ai_assistant")
    
    def info(self, message):
        """Log informational message"""
        self.logger.info(message)
    
    def error(self, message, exc_info=False):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def log_file_process(self, filename, tag, description, success, error_details=None):
        """Log file processing to the dedicated process log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        
        # Format the log entry
        log_entry = f"{timestamp} | {filename} | {tag} | {status}"
        
        # Add error details if applicable
        if error_details and not success:
            log_entry += f" | ERROR: {error_details}"
        
        # Add description
        if description:
            # Truncate if necessary
            max_desc_length = 50
            if len(description) > max_desc_length:
                description = description[:max_desc_length] + "..."
            log_entry += f" | {description}"
        
        # Write to the process log file
        with open(self.process_log_path, "a") as f:
            f.write(log_entry + "\n")
        
        # Also log to standard logger
        if success:
            self.logger.info(f"File processed: {filename}")
        else:
            self.logger.error(f"File processing failed: {filename} - {error_details}")
        
        return log_entry
    
    def get_recent_file_logs(self, count=50):
        """Get the most recent file processing logs"""
        if not self.process_log_path.exists():
            return []
        
        with open(self.process_log_path, "r") as f:
            lines = f.readlines()
        
        # Return the most recent logs, limited by count
        return [line.strip() for line in lines[-count:]]
    
    def get_error_logs(self, count=50):
        """Get the most recent error logs"""
        error_logs = []
        
        if not self.process_log_path.exists():
            return []
        
        with open(self.process_log_path, "r") as f:
            for line in f:
                if "FAILED" in line:
                    error_logs.append(line.strip())
        
        # Return the most recent error logs, limited by count
        return error_logs[-count:]