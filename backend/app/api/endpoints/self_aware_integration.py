"""
Integration layer for self-aware mode in chat system.
Parses AI responses for file operations and command requests.
"""
import re
import json
from typing import Optional, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class SelfAwareResponseParser:
    """Parse AI responses for file operations and commands in self-aware mode."""
    
    def __init__(self):
        # Patterns to detect file write requests
        self.file_write_patterns = [
            # Match: "write to file.py: content" or "save to file.py: content"
            r'(?:write|save|create)\s+(?:to\s+)?[\'"`]?([^\s\'"`]+\.[a-zA-Z]+)[\'"`]?\s*:\s*```(?:\w+)?\n(.*?)```',
            # Match: "update file.py with: content"
            r'(?:update|modify|edit)\s+[\'"`]?([^\s\'"`]+\.[a-zA-Z]+)[\'"`]?\s+with\s*:\s*```(?:\w+)?\n(.*?)```',
            # Match code blocks with file paths
            r'```(?:\w+)?\s*\n#\s*(?:file|File):\s*([^\n]+)\n(.*?)```',
        ]
        
        # Patterns to detect command execution requests
        self.command_patterns = [
            # Match: "run command: npm install"
            r'(?:run|execute|exec)\s+(?:command|cmd)?\s*:\s*`([^`]+)`',
            # Match: "$ npm install" or "> npm install"
            r'^\s*[$>]\s+(.+)$',
            # Match command blocks
            r'```(?:bash|sh|shell|cmd)\n(.*?)```',
        ]
    
    def parse_response(self, ai_response: str, session_token: str) -> List[Dict]:
        """Parse AI response for actions that need approval."""
        actions = []
        
        # Check for file write operations
        for pattern in self.file_write_patterns:
            matches = re.finditer(pattern, ai_response, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            for match in matches:
                filepath = match.group(1)
                content = match.group(2).strip()
                
                # Skip if it's just an example
                if self._is_example_code(filepath, content):
                    continue
                
                actions.append({
                    'type': 'file_write',
                    'filepath': filepath,
                    'content': content,
                    'reason': f'AI wants to write/update {filepath}',
                    'session_token': session_token
                })
        
        # Check for command execution requests
        for pattern in self.command_patterns:
            matches = re.finditer(pattern, ai_response, re.MULTILINE)
            for match in matches:
                command_str = match.group(1).strip()
                
                # Skip if it's just an example
                if self._is_example_command(command_str):
                    continue
                
                # Parse command into list
                command_list = self._parse_command_string(command_str)
                
                actions.append({
                    'type': 'command',
                    'command': command_list,
                    'command_str': command_str,
                    'reason': f'AI wants to execute: {command_str}',
                    'session_token': session_token
                })
        
        return actions
    
    def _is_example_code(self, filepath: str, content: str) -> bool:
        """Check if this is just example code, not meant to be written."""
        example_indicators = [
            'example', 'Example', 'EXAMPLE',
            'sample', 'Sample', 'SAMPLE',
            'like this', 'Like this',
            'for instance', 'For instance',
            'you could', 'You could',
            'would look like', 'might look like'
        ]
        
        # Check if filepath contains example indicators
        for indicator in example_indicators:
            if indicator in filepath:
                return True
        
        # Check if content is very short (likely just a snippet)
        if len(content) < 50:
            return True
        
        return False
    
    def _is_example_command(self, command: str) -> bool:
        """Check if this is just an example command."""
        example_indicators = [
            'example:', 'Example:',
            'like:', 'Like:',
            'such as:', 'Such as:',
            '<your', '<path', '<file',
            'your-', 'path/', 'file.'
        ]
        
        for indicator in example_indicators:
            if indicator in command:
                return True
        
        return False
    
    def _parse_command_string(self, command_str: str) -> List[str]:
        """Parse command string into list of arguments."""
        # Simple parsing - can be enhanced with shlex for more complex cases
        import shlex
        try:
            return shlex.split(command_str)
        except:
            # Fallback to simple split
            return command_str.split()
    
    def inject_approval_status(self, response: str, pending_actions: List[Dict]) -> str:
        """Inject approval status into the response for user visibility."""
        if not pending_actions:
            return response
        
        status_message = "\n\n---\n🔴 **SELF-AWARE MODE - APPROVAL REQUIRED**\n\n"
        
        for i, action in enumerate(pending_actions, 1):
            if action['type'] == 'file_write':
                status_message += f"{i}. **File Write Request**: `{action['filepath']}`\n"
            elif action['type'] == 'command':
                status_message += f"{i}. **Command Execution Request**: `{action['command_str']}`\n"
        
        status_message += "\nThese actions require your approval. You will see approval prompts shortly.\n"
        
        return response + status_message

# Global instance
response_parser = SelfAwareResponseParser()