"""
Simplified self-aware file reading for chat context

DEPRECATION NOTICE (2025-01-29):
This file is currently DISABLED in chats.py (inside "if False" block)
Functionality replaced by simple_file_access.py
Only imported by chats.py line 450 in disabled code path
Status: DEPRECATED - Safe to delete after removing disabled code block
"""
import re
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_file_requests(message: str) -> Dict[str, Any]:
    """Extract file paths and commands from user message"""
    message_lower = message.lower()
    
    # Commands that indicate file operations
    file_commands = ['read', 'show', 'display', 'view', 'cat', 'open', 'list', 'ls']
    has_file_command = any(cmd in message_lower for cmd in file_commands)
    
    # Improved patterns to catch file paths
    file_patterns = [
        # Quoted filenames (single, double, or backticks)
        r'[\'"`]([^\'"`]+\.[a-zA-Z]+)[\'"`]',
        # Filenames with paths
        r'\b([a-zA-Z0-9_\-/\\]+\.[a-zA-Z]+)\b',
        # Simple filenames with underscore
        r'\b([a-zA-Z0-9_\-]+\.[a-zA-Z]+)\b',
    ]
    
    found_files = []
    for pattern in file_patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        found_files.extend(matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in found_files:
        # Normalize path separators
        f = f.replace('\\', '/')
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    
    return {
        'has_command': has_file_command,
        'files': unique_files,
        'wants_list': 'list' in message_lower or 'ls' in message_lower
    }

def build_self_aware_context(message: str) -> str:
    """Build file context for self-aware mode"""
    from ...services.file_reader_service import get_file_reader
    
    request_info = extract_file_requests(message)
    
    if not request_info['has_command'] and not request_info['files']:
        return ""
    
    file_reader = get_file_reader()
    context_parts = []
    
    # Add header
    context_parts.append("SELF-AWARE MODE - FILE ACCESS")
    context_parts.append("=" * 60)
    
    # Process each file
    files_found = False
    for file_path in request_info['files']:
        logger.info(f"Attempting to read file: {file_path}")
        
        result = file_reader.read_file(file_path)
        
        if result["success"]:
            files_found = True
            content = result["content"]
            
            # Determine file type for syntax highlighting
            path_obj = Path(file_path)
            ext = path_obj.suffix.lower()
            
            # Language mapping
            lang_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.tsx': 'tsx',
                '.jsx': 'jsx',
                '.json': 'json',
                '.md': 'markdown',
                '.txt': 'text',
                '.yml': 'yaml',
                '.yaml': 'yaml',
                '.css': 'css',
                '.html': 'html',
                '.sh': 'bash',
                '.bat': 'batch',
            }
            
            language = lang_map.get(ext, 'text')
            
            # Add file header
            context_parts.append(f"\n=== FILE: {file_path} ===")
            context_parts.append(f"Type: {language} | Size: {result.get('size', len(content))} bytes")
            context_parts.append("")
            
            # Add content with syntax highlighting hint
            if language != 'text':
                context_parts.append(f"```{language}")
            
            # For code files, add line numbers
            if ext in ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.c', '.cpp']:
                lines = content.split('\n')
                numbered_lines = []
                for i, line in enumerate(lines, 1):
                    numbered_lines.append(f"{i:4d} | {line}")
                context_parts.append('\n'.join(numbered_lines))
            else:
                context_parts.append(content)
            
            if language != 'text':
                context_parts.append("```")
            
            context_parts.append("=" * 60)
        else:
            logger.warning(f"Failed to read file {file_path}: {result.get('error', 'Unknown error')}")
    
    # If no files found but user asked for files
    if not files_found and request_info['files']:
        context_parts.append("\nNo files could be read. Possible reasons:")
        context_parts.append("- File doesn't exist")
        context_parts.append("- Path is incorrect (use forward slashes: backend/app/main.py)")
        context_parts.append("- File type not allowed")
        context_parts.append("\nTry:")
        context_parts.append('- "show stop_assistant.py"')
        context_parts.append('- "read backend/app/main.py"')
        context_parts.append('- "display Readme.MD"')
    
    return '\n'.join(context_parts) if context_parts else ""