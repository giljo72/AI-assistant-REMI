"""
Enhanced chat endpoint with improved self-aware mode file handling

DEPRECATION NOTICE (2025-01-29):
This file is currently UNUSED and replaced by simple_file_access.py
Only referenced by restart_with_self_aware.py (test script)
Considered for deletion but kept as reference implementation
Status: DEPRECATED - Safe to delete when confirmed no longer needed
"""
from typing import Any, Dict, List
from fastapi import HTTPException
import logging
import re

logger = logging.getLogger(__name__)

class SelfAwareContextBuilder:
    """Builds context for self-aware mode with enhanced file operations"""
    
    def __init__(self):
        self.file_commands = {
            # File reading commands
            'read': ['read', 'show', 'display', 'view', 'cat', 'open'],
            'list': ['list', 'ls', 'dir', 'directory', 'files', 'folders'],
            'search': ['search', 'find', 'grep', 'locate'],
            'tree': ['tree', 'structure', 'hierarchy', 'overview'],
        }
        
    def extract_commands(self, message: str) -> Dict[str, Any]:
        """Extract file commands and paths from user message"""
        message_lower = message.lower()
        commands = []
        
        # Check for explicit commands
        for cmd_type, keywords in self.file_commands.items():
            for keyword in keywords:
                if keyword in message_lower:
                    commands.append(cmd_type)
                    break
        
        # Extract file paths - improved patterns
        file_patterns = [
            # Absolute Windows paths
            r'[Ff]:\\[Aa]ssistant\\([^\s\"\']+)',
            r'[Ff]:/[Aa]ssistant/([^\s\"\']+)',
            # Quoted paths
            r'[\'"`]([^\'"`]+\.[a-zA-Z]+)[\'"`]',
            # Relative paths with folders
            r'\b([a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-]+)*\.[a-zA-Z]+)\b',
            # Simple filenames
            r'\b([a-zA-Z0-9_\-]+\.[a-zA-Z]+)\b',
            # Directory paths
            r'\b([a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-]+)+)/?\\b',
        ]
        
        paths = []
        for pattern in file_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            paths.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_paths = []
        for path in paths:
            if path not in seen:
                seen.add(path)
                unique_paths.append(path)
        
        return {
            'commands': list(set(commands)),
            'paths': unique_paths,
            'has_file_request': bool(commands or paths)
        }
    
    def build_file_context(self, message: str) -> str:
        """Build comprehensive file context for self-aware mode"""
        from ...services.enhanced_file_reader import get_enhanced_file_reader
        reader = get_enhanced_file_reader()
        
        extracted = self.extract_commands(message)
        context_parts = []
        
        # Add introductory context
        context_parts.append("""
SELF-AWARE MODE - FILE SYSTEM ACCESS
You have direct access to the AI Assistant source code at F:\\assistant.
When displaying code, preserve formatting and use appropriate language indicators.
""")
        
        # Handle specific commands
        if 'tree' in extracted['commands']:
            result = reader.get_project_structure()
            if result['success']:
                context_parts.append("\n=== PROJECT STRUCTURE ===")
                context_parts.append(self._format_tree(result['tree']))
        
        elif 'list' in extracted['commands']:
            # Determine directory to list
            directory = ""
            if extracted['paths']:
                # Use first path that looks like a directory
                for path in extracted['paths']:
                    if not '.' in path.split('/')[-1]:  # No extension = likely directory
                        directory = path
                        break
            
            result = reader.list_directory(directory)
            if result['success']:
                context_parts.append(f"\n=== DIRECTORY LISTING: {result['current_directory']} ===")
                
                # List directories first
                if result['directories']:
                    context_parts.append("\nDirectories:")
                    for d in result['directories']:
                        context_parts.append(f"  📁 {d['name']}/")
                
                # Then files
                if result['files']:
                    context_parts.append("\nFiles:")
                    for f in result['files']:
                        size_str = self._format_size(f['size'])
                        context_parts.append(f"  📄 {f['name']} ({size_str})")
                
                context_parts.append(f"\nTotal: {result['total_items']} items")
        
        elif 'search' in extracted['commands']:
            # Extract search term
            search_match = re.search(r'(?:search|find)\s+(?:for\s+)?[\'"`]?([^\'"`\s]+)[\'"`]?', message, re.IGNORECASE)
            if search_match:
                pattern = search_match.group(1)
                result = reader.search_files(pattern)
                if result['success']:
                    context_parts.append(f"\n=== SEARCH RESULTS FOR '{pattern}' ===")
                    if result['matches']:
                        for match in result['matches'][:20]:  # Limit to 20 results
                            context_parts.append(f"  📄 {match['path']}")
                        if result['count'] > 20:
                            context_parts.append(f"  ... and {result['count'] - 20} more files")
                    else:
                        context_parts.append("  No files found matching the pattern.")
        
        # Handle file reading
        if extracted['paths'] and ('read' in extracted['commands'] or not extracted['commands']):
            for path in extracted['paths']:
                result = reader.read_file_with_context(path)
                if result['success']:
                    context_parts.append(f"\n=== FILE: {result['path']} ===")
                    context_parts.append(f"Language: {result['language']} | Size: {self._format_size(result['size'])} | Lines: {result['lines']}")
                    context_parts.append("```" + result['language'])
                    
                    # Use numbered content for code files, regular for others
                    if result['language'] in ['python', 'javascript', 'typescript', 'java', 'c', 'cpp', 'go', 'rust']:
                        context_parts.append(result['numbered_content'])
                    else:
                        context_parts.append(result['content'])
                    
                    context_parts.append("```")
                else:
                    context_parts.append(f"\n=== ERROR READING FILE: {path} ===")
                    context_parts.append(f"Error: {result['error']}")
        
        # If no specific command but in self-aware mode, provide help
        if not extracted['has_file_request']:
            context_parts.append("""
Available file operations:
- To read a file: "read backend/app/main.py" or "show main.py"
- To list directory: "list backend/app" or "ls frontend/src"
- To search files: "search for 'pattern'" or "find config files"
- To see project structure: "show project tree" or "display structure"

Example paths:
- backend/app/main.py
- frontend/src/App.tsx
- docker-compose.yml
- requirements.txt
""")
        
        return "\n".join(context_parts)
    
    def _format_tree(self, node: Dict[str, Any], prefix: str = "", is_last: bool = True) -> str:
        """Format directory tree structure"""
        lines = []
        
        # Current node
        connector = "└── " if is_last else "├── "
        icon = "📁 " if node['type'] == 'directory' else "📄 "
        lines.append(prefix + connector + icon + node['name'])
        
        # Children
        if 'children' in node:
            extension = "    " if is_last else "│   "
            children = node['children']
            for i, child in enumerate(children):
                is_last_child = i == len(children) - 1
                child_lines = self._format_tree(child, prefix + extension, is_last_child)
                lines.append(child_lines)
        
        return "\n".join(lines)
    
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


def enhance_self_aware_context(is_self_aware: bool, request_message: str, context_mode: str) -> str:
    """
    Enhanced self-aware context builder that properly handles file operations.
    This ensures ONLY self-aware mode can access files.
    """
    # Security check - ONLY allow file access in self-aware mode
    if not is_self_aware or context_mode != "self-aware":
        return ""
    
    builder = SelfAwareContextBuilder()
    return builder.build_file_context(request_message)