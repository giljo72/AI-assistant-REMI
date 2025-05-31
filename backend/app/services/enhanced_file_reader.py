"""
Enhanced file reader service for self-aware mode with better formatting and security.
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class EnhancedFileReader:
    """Enhanced file reader with syntax highlighting hints and better formatting"""
    
    def __init__(self, base_path: str = "F:/assistant"):
        self.base_path = Path(base_path).resolve()
        
        # File extension to language mapping for syntax highlighting
        self.language_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'text',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.css': 'css',
            '.html': 'html',
            '.xml': 'xml',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bat': 'batch',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
        }
        
    def validate_path(self, path: str) -> Optional[Path]:
        """Validate and resolve path within base directory"""
        try:
            # Handle different path formats
            if path.startswith('F:\\') or path.startswith('F:/'):
                full_path = Path(path).resolve()
            else:
                # Relative path from base
                full_path = (self.base_path / path).resolve()
            
            # Security check
            if not str(full_path).startswith(str(self.base_path)):
                logger.warning(f"Path traversal attempt: {path}")
                return None
                
            return full_path
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return None
    
    def read_file_with_context(self, path: str) -> Dict[str, Any]:
        """Read file with language detection and formatting hints"""
        full_path = self.validate_path(path)
        if not full_path:
            return {
                "success": False,
                "error": "Invalid path"
            }
            
        if not full_path.exists():
            return {
                "success": False,
                "error": f"File not found: {path}"
            }
            
        if not full_path.is_file():
            return {
                "success": False,
                "error": f"Not a file: {path}"
            }
            
        try:
            # Get file info
            stat = full_path.stat()
            extension = full_path.suffix.lower()
            language = self.language_map.get(extension, 'text')
            
            # Read content
            content = full_path.read_text(encoding='utf-8')
            
            # Add line numbers for code files
            if extension in ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.c', '.cpp', '.go', '.rs']:
                lines = content.split('\n')
                numbered_lines = []
                for i, line in enumerate(lines, 1):
                    numbered_lines.append(f"{i:4d} | {line}")
                numbered_content = '\n'.join(numbered_lines)
            else:
                numbered_content = content
            
            return {
                "success": True,
                "path": str(full_path.relative_to(self.base_path)).replace('\\', '/'),
                "content": content,
                "numbered_content": numbered_content,
                "language": language,
                "size": stat.st_size,
                "lines": content.count('\n') + 1,
                "extension": extension
            }
            
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "Cannot decode file - binary or unsupported encoding"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_directory(self, path: str = "", recursive: bool = False, show_hidden: bool = False) -> Dict[str, Any]:
        """List directory contents with better organization"""
        full_path = self.validate_path(path or ".")
        if not full_path:
            return {
                "success": False,
                "error": "Invalid path"
            }
            
        if not full_path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {path}"
            }
            
        if not full_path.is_dir():
            return {
                "success": False,
                "error": f"Not a directory: {path}"
            }
            
        try:
            files = []
            directories = []
            
            # Patterns to ignore
            ignore_patterns = [
                '__pycache__', '.git', 'node_modules', '.pytest_cache',
                '*.pyc', '*.pyo', '.DS_Store', 'Thumbs.db'
            ]
            
            def should_ignore(name: str) -> bool:
                if not show_hidden and name.startswith('.'):
                    return True
                for pattern in ignore_patterns:
                    if pattern.startswith('*'):
                        if name.endswith(pattern[1:]):
                            return True
                    elif name == pattern:
                        return True
                return False
            
            # List contents
            for item in sorted(full_path.iterdir()):
                if should_ignore(item.name):
                    continue
                    
                relative_path = str(item.relative_to(self.base_path)).replace('\\', '/')
                
                if item.is_dir():
                    directories.append({
                        "name": item.name,
                        "path": relative_path,
                        "type": "directory"
                    })
                else:
                    stat = item.stat()
                    extension = item.suffix.lower()
                    files.append({
                        "name": item.name,
                        "path": relative_path,
                        "type": "file",
                        "extension": extension,
                        "size": stat.st_size,
                        "language": self.language_map.get(extension, 'text')
                    })
            
            # Format output
            current_dir = str(full_path.relative_to(self.base_path)).replace('\\', '/') or "."
            
            return {
                "success": True,
                "current_directory": current_dir,
                "directories": directories,
                "files": files,
                "total_items": len(directories) + len(files)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_files(self, pattern: str, path: str = "", file_extensions: List[str] = None) -> Dict[str, Any]:
        """Search for files by name pattern"""
        full_path = self.validate_path(path or ".")
        if not full_path:
            return {
                "success": False,
                "error": "Invalid path"
            }
            
        try:
            matches = []
            
            # Convert extensions to set for faster lookup
            ext_set = set(file_extensions) if file_extensions else None
            
            # Search recursively
            for item in full_path.rglob("*"):
                if item.is_file():
                    # Check extension filter
                    if ext_set and item.suffix.lower() not in ext_set:
                        continue
                        
                    # Check name pattern
                    if pattern.lower() in item.name.lower():
                        relative_path = str(item.relative_to(self.base_path)).replace('\\', '/')
                        matches.append({
                            "name": item.name,
                            "path": relative_path,
                            "extension": item.suffix.lower(),
                            "size": item.stat().st_size
                        })
                        
                        if len(matches) >= 50:  # Limit results
                            break
            
            return {
                "success": True,
                "query": pattern,
                "matches": matches,
                "count": len(matches)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_project_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """Get a tree view of the project structure"""
        try:
            def build_tree(path: Path, depth: int = 0) -> Dict[str, Any]:
                if depth >= max_depth:
                    return None
                    
                result = {
                    "name": path.name or "assistant",
                    "type": "directory" if path.is_dir() else "file",
                    "path": str(path.relative_to(self.base_path)).replace('\\', '/')
                }
                
                if path.is_dir():
                    children = []
                    # Skip certain directories
                    skip_dirs = {'__pycache__', '.git', 'node_modules', 'venv', '.pytest_cache'}
                    
                    for item in sorted(path.iterdir()):
                        if item.name.startswith('.') or item.name in skip_dirs:
                            continue
                        child = build_tree(item, depth + 1)
                        if child:
                            children.append(child)
                    
                    if children:
                        result["children"] = children
                        
                return result
            
            tree = build_tree(self.base_path)
            
            return {
                "success": True,
                "tree": tree
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Singleton instance
_enhanced_reader = None

def get_enhanced_file_reader() -> EnhancedFileReader:
    """Get or create the enhanced file reader instance"""
    global _enhanced_reader
    if _enhanced_reader is None:
        _enhanced_reader = EnhancedFileReader()
    return _enhanced_reader