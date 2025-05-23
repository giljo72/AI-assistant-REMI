"""
File Reader Service for Self-Aware Mode
Provides safe file system access for the AI assistant to read its own codebase
"""
import os
import logging
from typing import List, Dict, Optional, Union
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)

class FileReaderService:
    """Service for reading files in the assistant's codebase"""
    
    def __init__(self, base_path: str = "F:\\assistant"):
        self.base_path = Path(base_path).resolve()
        self.allowed_extensions = {
            '.py', '.tsx', '.ts', '.jsx', '.js', '.json', '.md', '.txt', '.yml', '.yaml',
            '.env', '.sql', '.sh', '.bat', '.css', '.html', '.xml', '.toml', '.ini',
            '.dockerfile', '.dockerignore', '.gitignore'
        }
        self.max_file_size = 5 * 1024 * 1024  # 5MB max per file
        self.exclude_dirs = {
            'node_modules', '__pycache__', '.git', 'venv', 'venv_nemo', 
            '.pytest_cache', 'dist', 'build', '.next', 'coverage'
        }
    
    def is_safe_path(self, path: Path) -> bool:
        """Check if a path is safe to access"""
        try:
            # Resolve to absolute path and check if it's within base_path
            resolved = path.resolve()
            return resolved.parts[:len(self.base_path.parts)] == self.base_path.parts
        except Exception:
            return False
    
    def list_files(self, directory: str = "", pattern: Optional[str] = None) -> List[Dict[str, str]]:
        """List files in a directory with optional pattern matching"""
        try:
            target_dir = self.base_path / directory
            
            if not self.is_safe_path(target_dir):
                logger.warning(f"Attempted to access unsafe path: {target_dir}")
                return []
            
            files = []
            for item in target_dir.iterdir():
                if item.is_file():
                    if item.suffix.lower() in self.allowed_extensions:
                        rel_path = item.relative_to(self.base_path)
                        files.append({
                            "name": item.name,
                            "path": str(rel_path).replace('\\', '/'),
                            "size": item.stat().st_size,
                            "type": "file"
                        })
                elif item.is_dir() and item.name not in self.exclude_dirs:
                    rel_path = item.relative_to(self.base_path)
                    files.append({
                        "name": item.name,
                        "path": str(rel_path).replace('\\', '/'),
                        "type": "directory"
                    })
            
            # Apply pattern filter if provided
            if pattern:
                pattern_lower = pattern.lower()
                files = [f for f in files if pattern_lower in f["name"].lower()]
            
            return sorted(files, key=lambda x: (x["type"], x["name"]))
            
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return []
    
    def read_file(self, file_path: str, max_lines: Optional[int] = None) -> Dict[str, Union[str, bool]]:
        """Read a file's content with safety checks"""
        try:
            full_path = self.base_path / file_path
            
            if not self.is_safe_path(full_path):
                return {
                    "content": "",
                    "error": "Access denied: Path is outside the allowed directory",
                    "success": False
                }
            
            if not full_path.exists():
                return {
                    "content": "",
                    "error": f"File not found: {file_path}",
                    "success": False
                }
            
            if not full_path.is_file():
                return {
                    "content": "",
                    "error": f"Not a file: {file_path}",
                    "success": False
                }
            
            # Check file size
            file_size = full_path.stat().st_size
            if file_size > self.max_file_size:
                return {
                    "content": "",
                    "error": f"File too large: {file_size} bytes (max: {self.max_file_size})",
                    "success": False
                }
            
            # Check file extension
            if full_path.suffix.lower() not in self.allowed_extensions:
                return {
                    "content": "",
                    "error": f"File type not allowed: {full_path.suffix}",
                    "success": False
                }
            
            # Read the file
            try:
                content = full_path.read_text(encoding='utf-8')
                
                # Limit lines if requested
                if max_lines:
                    lines = content.split('\n')
                    if len(lines) > max_lines:
                        content = '\n'.join(lines[:max_lines])
                        content += f"\n\n... (truncated at {max_lines} lines)"
                
                return {
                    "content": content,
                    "path": file_path,
                    "size": file_size,
                    "success": True
                }
                
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    content = full_path.read_text(encoding='latin-1')
                    return {
                        "content": content,
                        "path": file_path,
                        "size": file_size,
                        "encoding": "latin-1",
                        "success": True
                    }
                except Exception as e:
                    return {
                        "content": "",
                        "error": f"Failed to decode file: {str(e)}",
                        "success": False
                    }
                    
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {
                "content": "",
                "error": str(e),
                "success": False
            }
    
    def search_in_files(self, search_term: str, file_pattern: Optional[str] = None, 
                       max_results: int = 20) -> List[Dict[str, Union[str, int]]]:
        """Search for a term in the codebase"""
        results = []
        search_lower = search_term.lower()
        
        try:
            for root, dirs, files in os.walk(self.base_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
                
                root_path = Path(root)
                if not self.is_safe_path(root_path):
                    continue
                
                for file in files:
                    if len(results) >= max_results:
                        break
                    
                    file_path = root_path / file
                    
                    # Check file pattern if provided
                    if file_pattern and file_pattern.lower() not in file.lower():
                        continue
                    
                    # Check extension
                    if file_path.suffix.lower() not in self.allowed_extensions:
                        continue
                    
                    # Search in file
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            if search_lower in line.lower():
                                rel_path = file_path.relative_to(self.base_path)
                                results.append({
                                    "file": str(rel_path).replace('\\', '/'),
                                    "line": line_num,
                                    "content": line.strip()[:200],  # First 200 chars
                                    "match": True
                                })
                                
                                if len(results) >= max_results:
                                    break
                                    
                    except Exception:
                        # Skip files that can't be read
                        continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []
    
    def get_project_structure(self, max_depth: int = 3) -> Dict[str, any]:
        """Get a tree structure of the project"""
        def build_tree(path: Path, current_depth: int = 0):
            if current_depth >= max_depth:
                return None
            
            tree = {
                "name": path.name,
                "type": "directory" if path.is_dir() else "file",
                "children": []
            }
            
            if path.is_dir() and path.name not in self.exclude_dirs:
                try:
                    for item in sorted(path.iterdir()):
                        if item.is_file() and item.suffix.lower() in self.allowed_extensions:
                            tree["children"].append({
                                "name": item.name,
                                "type": "file"
                            })
                        elif item.is_dir() and item.name not in self.exclude_dirs:
                            subtree = build_tree(item, current_depth + 1)
                            if subtree:
                                tree["children"].append(subtree)
                except PermissionError:
                    pass
            
            return tree
        
        try:
            return build_tree(self.base_path)
        except Exception as e:
            logger.error(f"Error building project structure: {e}")
            return {"name": "assistant", "type": "directory", "children": []}


# Global instance
_file_reader: Optional[FileReaderService] = None

def get_file_reader() -> FileReaderService:
    """Get global file reader instance"""
    global _file_reader
    if _file_reader is None:
        _file_reader = FileReaderService()
    return _file_reader