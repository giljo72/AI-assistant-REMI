"""
Simplified file access for the AI assistant - works in ANY context
"""
import re
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def inject_file_content_if_requested(message: str) -> str:
    """
    Check if user is asking for files and inject content directly.
    Works in ANY context mode for simplicity.
    """
    logger.info(f"Checking message for file requests: {message}")
    message_lower = message.lower()
    
    # Quick check if this might be a file request
    file_indicators = ['read', 'show', 'display', 'file', '.py', '.md', '.txt', '.js', '.ts']
    has_indicator = any(indicator in message_lower for indicator in file_indicators)
    logger.info(f"Has file indicator: {has_indicator}")
    
    if not has_indicator:
        return ""
    
    # Import file reader
    try:
        from ...services.file_reader_service import get_file_reader
        file_reader = get_file_reader()
    except Exception as e:
        logger.error(f"Failed to import file reader: {e}")
        return ""
    
    # Find file references in the message
    file_patterns = [
        r'(?:read|show|display|view|cat|open)\s+[\'"`]?([^\s\'"`]+\.[a-zA-Z]+)[\'"`]?',
        r'[\'"`]([^\'"`]+\.[a-zA-Z]+)[\'"`]',
        r'\b([a-zA-Z0-9_\-/\\]+\.[a-zA-Z]+)\b',
    ]
    
    found_files = []
    for pattern in file_patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        found_files.extend(matches)
    
    # Remove duplicates
    found_files = list(dict.fromkeys(found_files))
    
    if not found_files:
        return ""
    
    # Read files and build context
    file_contents = []
    for file_path in found_files:
        file_path = file_path.replace('\\', '/')
        logger.info(f"Attempting to read: {file_path}")
        
        result = file_reader.read_file(file_path)
        if result["success"]:
            # Determine language for syntax highlighting
            ext = Path(file_path).suffix.lower()
            lang_map = {
                '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                # Use 'plaintext' for markdown and text files to ensure they display in code blocks
                '.md': 'plaintext', '.txt': 'plaintext', '.json': 'json',
                '.yml': 'yaml', '.yaml': 'yaml', '.sh': 'bash'
            }
            lang = lang_map.get(ext, 'plaintext')
            
            file_contents.append(f"\n=== FILE: {file_path} ===")
            file_contents.append(f"```{lang}")
            file_contents.append(result["content"])
            file_contents.append("```")
            file_contents.append("=" * 60)
            
            logger.info(f"Successfully read {file_path}: {len(result['content'])} chars")
        else:
            logger.warning(f"Failed to read {file_path}: {result.get('error', 'Unknown')}")
    
    if file_contents:
        return "\n".join([
            "\nFILE CONTENTS REQUESTED:",
            "=" * 60
        ] + file_contents)
    
    return ""