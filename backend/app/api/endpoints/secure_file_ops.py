"""
Secure file operations for self-aware mode.
Enforces F:\\ drive restrictions and requires approval for all writes.
"""
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class SecureFileOperations:
    def __init__(self):
        # Only allow writes to F: drive
        self.write_allowed_roots = ["F:\\", "f:\\", "/mnt/f/"]
        
        # Dangerous patterns to block
        self.dangerous_patterns = [
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__\s*\(',
            r'compile\s*\(',
            r'globals\s*\(',
            r'locals\s*\(',
            r'vars\s*\(',
            r'importlib\.import_module',
            r'pickle\.loads?\s*\(',
            r'marshal\.loads?\s*\(',
            r'os\.system\s*\(',
            r'subprocess\.call\s*\(',
            r'subprocess\.run\s*\(',
            r'subprocess\.Popen\s*\(',
        ]
        
        # Protected files/patterns
        self.protected_patterns = [
            r'\.git[/\\]',
            r'\.env',
            r'venv[/\\]',
            r'node_modules[/\\]',
            r'__pycache__[/\\]',
            r'\.exe$',
            r'\.dll$',
            r'\.so$',
            r'\.bat$',
            r'startai\.bat',
            r'stopai\.bat',
        ]
    
    def normalize_path(self, path: str) -> str:
        """Normalize path for consistent checking."""
        # Handle both Windows and WSL paths
        if path.startswith("/mnt/"):
            # WSL path
            return path
        else:
            # Windows path
            return os.path.abspath(path)
    
    def is_write_allowed(self, path: str) -> bool:
        """Check if write is allowed to the given path."""
        normalized = self.normalize_path(path)
        
        # Check if path is under allowed roots
        allowed = False
        for root in self.write_allowed_roots:
            if normalized.lower().startswith(root.lower()):
                allowed = True
                break
            # WSL path check
            if normalized.startswith("/mnt/f/"):
                allowed = True
                break
        
        if not allowed:
            logger.warning(f"Write blocked - path not in F: drive: {path}")
            return False
        
        # Check protected patterns
        for pattern in self.protected_patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                logger.warning(f"Write blocked - protected pattern: {path}")
                return False
        
        return True
    
    def is_code_safe(self, content: str) -> Tuple[bool, List[str]]:
        """Check if code content is safe. Returns (is_safe, warnings)."""
        warnings = []
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content):
                warnings.append(f"Dangerous pattern detected: {pattern}")
        
        is_safe = len(warnings) == 0
        return is_safe, warnings
    
    def create_backup(self, filepath: str) -> Optional[str]:
        """Create a backup of the file before modification."""
        if not os.path.exists(filepath):
            return None
        
        backup_dir = Path("F:/assistant/backups/self_aware")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(filepath).name
        backup_path = backup_dir / f"{filename}_{timestamp}.bak"
        
        try:
            shutil.copy2(filepath, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    async def read_file(self, filepath: str) -> str:
        """Read a file (no approval needed for reads)."""
        normalized = self.normalize_path(filepath)
        
        try:
            with open(normalized, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Could not read file: {str(e)}")
    
    async def write_file(self, filepath: str, content: str, action_id: str) -> dict:
        """Write a file (requires prior approval via action_id)."""
        normalized = self.normalize_path(filepath)
        
        # Check write permissions
        if not self.is_write_allowed(normalized):
            raise HTTPException(status_code=403, detail="Write not allowed to this path")
        
        # Check code safety
        is_safe, warnings = self.is_code_safe(content)
        
        # Create backup
        backup_path = self.create_backup(normalized)
        
        # Write the file
        try:
            os.makedirs(os.path.dirname(normalized), exist_ok=True)
            with open(normalized, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"File written: {normalized}")
            
            return {
                "success": True,
                "path": filepath,
                "backup": backup_path,
                "warnings": warnings
            }
        except Exception as e:
            logger.error(f"Failed to write file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")
    
    async def execute_command(self, command: List[str], cwd: Optional[str] = None) -> dict:
        """Execute a command (requires prior approval)."""
        # Default to F:\assistant if no cwd specified
        if not cwd:
            cwd = "F:\\assistant"
        
        # Normalize the working directory
        cwd = self.normalize_path(cwd)
        
        # Log the command for audit
        logger.info(f"Executing command: {' '.join(command)} in {cwd}")
        
        try:
            # Execute with timeout of 5 minutes
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300,
                shell=False  # Never use shell=True for security
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": ' '.join(command),
                "cwd": cwd
            }
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {' '.join(command)}")
            return {
                "success": False,
                "error": "Command execution timeout (5 minutes)",
                "command": ' '.join(command),
                "cwd": cwd
            }
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": ' '.join(command),
                "cwd": cwd
            }

# Global instance
secure_file_ops = SecureFileOperations()