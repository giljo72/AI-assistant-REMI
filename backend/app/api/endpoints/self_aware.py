from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import re
from pathlib import Path
import json
import hashlib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/self-aware",
    tags=["self-aware"]
)

# Security configuration
ALLOWED_BASE_PATH = Path("F:/assistant").resolve()
DANGEROUS_PATTERNS = [
    r'exec\s*\(',
    r'eval\s*\(',
    r'__import__\s*\(',
    r'compile\s*\(',
    r'globals\s*\(',
    r'locals\s*\(',
    r'vars\s*\(',
    r'open\s*\([^)]*[\'"]w[\'"]',  # Writing to files
    r'os\.system\s*\(',
    r'subprocess\.',
    r'pickle\.load',
    r'pickle\.loads',
    r'marshal\.load',
    r'importlib\.',
]

PROTECTED_PATHS = [
    ".git",
    ".env",
    "venv",
    "node_modules",
    "__pycache__",
    ".gitignore",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dll",
    "*.exe",
    "*.bat",
    "*.sh"
]

MAX_FILE_SIZE = 1024 * 1024  # 1MB limit for reading

class FileInfo(BaseModel):
    """Information about a file"""
    path: str
    name: str
    size: int
    modified: str
    is_directory: bool
    extension: Optional[str] = None

class FileContent(BaseModel):
    """File content with metadata"""
    path: str
    content: str
    size: int
    modified: str
    hash: str

class FileUpdate(BaseModel):
    """Request to update a file"""
    path: str = Field(..., description="Relative path from F:/assistant")
    content: str = Field(..., description="New file content")
    reason: str = Field(..., description="Reason for the change")
    
class FileUpdateResponse(BaseModel):
    """Response after file update"""
    success: bool
    path: str
    backup_path: Optional[str] = None
    message: str
    warnings: List[str] = Field(default_factory=list)
    
class CodeValidation(BaseModel):
    """Code validation result"""
    is_safe: bool
    warnings: List[str] = Field(default_factory=list)
    dangerous_patterns: List[str] = Field(default_factory=list)

def validate_path(path: str) -> Path:
    """Validate and resolve path within allowed directory"""
    try:
        # Convert to Path and resolve
        requested_path = Path(path)
        if requested_path.is_absolute():
            full_path = requested_path.resolve()
        else:
            full_path = (ALLOWED_BASE_PATH / requested_path).resolve()
        
        # Ensure path is within allowed directory
        if not str(full_path).startswith(str(ALLOWED_BASE_PATH)):
            raise ValueError("Path traversal attempt detected")
            
        # Check against protected paths
        for protected in PROTECTED_PATHS:
            if protected.startswith("*"):
                if full_path.suffix == protected[1:]:
                    raise ValueError(f"Protected file type: {protected}")
            elif protected in str(full_path):
                raise ValueError(f"Protected path: {protected}")
                
        return full_path
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Invalid path: {str(e)}")

def validate_code_safety(content: str) -> CodeValidation:
    """Check code for potentially dangerous patterns"""
    warnings = []
    dangerous = []
    
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            dangerous.append(pattern)
            
    # Additional checks
    if "import os" in content or "from os import" in content:
        warnings.append("Uses OS module - review system calls carefully")
    if "import socket" in content or "from socket import" in content:
        warnings.append("Uses socket module - review network operations")
    if "import requests" in content or "import urllib" in content:
        warnings.append("Makes network requests - review URLs and data")
        
    return CodeValidation(
        is_safe=len(dangerous) == 0,
        warnings=warnings,
        dangerous_patterns=dangerous
    )

@router.get("/files", response_model=List[FileInfo])
async def list_files(
    path: Optional[str] = Query("", description="Relative path from F:/assistant"),
    include_hidden: bool = Query(False, description="Include hidden files")
):
    """List files in the assistant directory"""
    try:
        base_path = validate_path(path or "")
        
        if not base_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
            
        if not base_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
            
        files = []
        for item in base_path.iterdir():
            # Skip hidden files unless requested
            if not include_hidden and item.name.startswith('.'):
                continue
                
            # Skip protected paths
            skip = False
            for protected in PROTECTED_PATHS:
                if protected.startswith("*") and item.suffix == protected[1:]:
                    skip = True
                    break
                elif protected in str(item):
                    skip = True
                    break
            if skip:
                continue
                
            stat = item.stat()
            relative_path = str(item.relative_to(ALLOWED_BASE_PATH)).replace("\\", "/")
            
            files.append(FileInfo(
                path=relative_path,
                name=item.name,
                size=stat.st_size,
                modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                is_directory=item.is_dir(),
                extension=item.suffix if item.is_file() else None
            ))
            
        return sorted(files, key=lambda x: (not x.is_directory, x.name))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/read", response_model=FileContent)
async def read_file(path: str = Query(..., description="Relative path from F:/assistant")):
    """Read a file from the assistant directory"""
    try:
        full_path = validate_path(path)
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
            
        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
            
        # Check file size
        stat = full_path.stat()
        if stat.st_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File too large (max {MAX_FILE_SIZE} bytes)")
            
        # Read file content
        try:
            content = full_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252']:
                try:
                    content = full_path.read_text(encoding=encoding)
                    break
                except:
                    continue
            else:
                raise HTTPException(status_code=415, detail="Cannot decode file content")
                
        # Calculate hash
        file_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        return FileContent(
            path=str(full_path.relative_to(ALLOWED_BASE_PATH)).replace("\\", "/"),
            content=content,
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            hash=file_hash
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate", response_model=CodeValidation)
async def validate_code(code: str):
    """Validate code for safety before writing"""
    return validate_code_safety(code)

@router.post("/update", response_model=FileUpdateResponse)
async def update_file(update: FileUpdate):
    """Update a file with safety checks and backup"""
    try:
        full_path = validate_path(update.path)
        
        # Validate the new content
        validation = validate_code_safety(update.content)
        if not validation.is_safe:
            return FileUpdateResponse(
                success=False,
                path=update.path,
                message="Code contains potentially dangerous patterns",
                warnings=validation.dangerous_patterns
            )
            
        # Create backup if file exists
        backup_path = None
        if full_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = ALLOWED_BASE_PATH / "backups" / full_path.parent.relative_to(ALLOWED_BASE_PATH)
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"{full_path.stem}_{timestamp}{full_path.suffix}"
            backup_path.write_text(full_path.read_text())
            
        # Write the new content
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(update.content)
        
        # Log the change
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "path": str(full_path.relative_to(ALLOWED_BASE_PATH)),
            "reason": update.reason,
            "backup": str(backup_path.relative_to(ALLOWED_BASE_PATH)) if backup_path else None,
            "warnings": validation.warnings
        }
        
        log_file = ALLOWED_BASE_PATH / "logs" / "file_modifications.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        return FileUpdateResponse(
            success=True,
            path=update.path,
            backup_path=str(backup_path.relative_to(ALLOWED_BASE_PATH)) if backup_path else None,
            message="File updated successfully",
            warnings=validation.warnings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating file: {e}")
        return FileUpdateResponse(
            success=False,
            path=update.path,
            message=f"Failed to update file: {str(e)}",
            warnings=[]
        )

@router.get("/modifications")
async def get_modifications(limit: int = Query(50, description="Number of recent modifications")):
    """Get recent file modifications"""
    try:
        log_file = ALLOWED_BASE_PATH / "logs" / "file_modifications.jsonl"
        if not log_file.exists():
            return []
            
        modifications = []
        with log_file.open() as f:
            for line in f:
                if line.strip():
                    modifications.append(json.loads(line))
                    
        # Return most recent first
        return sorted(modifications, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
    except Exception as e:
        logger.error(f"Error reading modifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))