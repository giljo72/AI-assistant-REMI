"""
Service for processing self-aware AI assistant responses and extracting file modification requests.
"""
import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
import difflib

logger = logging.getLogger(__name__)

class SelfAwareService:
    """
    Parses AI responses for file modification instructions and prepares them for approval.
    """
    
    # Patterns to detect file modification instructions
    FILE_CHANGE_PATTERNS = [
        # Pattern 1: Explicit update/replace/modify instructions
        r"(?:update|replace|modify|change|edit)\s+(?:the\s+)?(?:file\s+)?['\"`]?([^'\"`\s]+\.[a-zA-Z]+)['\"`]?",
        
        # Pattern 2: Code blocks with file indicators
        r"(?:in|for)\s+['\"`]?([^'\"`\s]+\.[a-zA-Z]+)['\"`]?\s*:?\s*```[a-zA-Z]*\n(.*?)```",
        
        # Pattern 3: File path followed by code block
        r"['\"`]?([^'\"`\s]+\.[a-zA-Z]+)['\"`]?\s*:\s*```[a-zA-Z]*\n(.*?)```",
        
        # Pattern 4: "Save as" or "Write to" patterns
        r"(?:save|write)\s+(?:as|to)\s+['\"`]?([^'\"`\s]+\.[a-zA-Z]+)['\"`]?",
    ]
    
    # Pattern to extract code blocks
    CODE_BLOCK_PATTERN = r"```(?:[a-zA-Z]+)?\n(.*?)```"
    
    def __init__(self):
        self.base_path = Path("F:/assistant")
    
    def extract_file_modifications(self, ai_response: str) -> List[Dict[str, Any]]:
        """
        Extract file modification requests from AI response.
        
        Returns:
            List of modification requests with structure:
            {
                "file_path": str,
                "content": str,
                "operation": str,  # "create", "update", "replace"
                "reason": str,
                "line_range": Optional[Tuple[int, int]]
            }
        """
        modifications = []
        
        # First, look for explicit file modification patterns
        for pattern in self.FILE_CHANGE_PATTERNS[:2]:
            matches = re.finditer(pattern, ai_response, re.DOTALL | re.IGNORECASE)
            for match in matches:
                file_path = match.group(1)
                
                # Extract code content following the file reference
                code_match = re.search(
                    rf"{re.escape(file_path)}.*?```[a-zA-Z]*\n(.*?)```",
                    ai_response[match.start():],
                    re.DOTALL
                )
                
                if code_match:
                    content = code_match.group(1).strip()
                    
                    # Determine operation type
                    operation = self._determine_operation(file_path, ai_response, match.start())
                    
                    # Extract reason from surrounding context
                    reason = self._extract_reason(ai_response, match.start())
                    
                    modifications.append({
                        "file_path": file_path,
                        "content": content,
                        "operation": operation,
                        "reason": reason,
                        "line_range": None  # TODO: Extract if specified
                    })
        
        # Look for structured JSON-like modification instructions
        json_pattern = r"```json\s*\n(.*?)```"
        json_matches = re.finditer(json_pattern, ai_response, re.DOTALL)
        for match in json_matches:
            try:
                data = json.loads(match.group(1))
                if isinstance(data, dict) and "file_modifications" in data:
                    for mod in data["file_modifications"]:
                        modifications.append(mod)
            except json.JSONDecodeError:
                pass
        
        return self._deduplicate_modifications(modifications)
    
    def _determine_operation(self, file_path: str, response: str, position: int) -> str:
        """Determine if this is a create, update, or replace operation."""
        # Check if file exists
        full_path = self.base_path / file_path
        if not full_path.exists():
            return "create"
        
        # Look for keywords near the file reference
        context = response[max(0, position-100):position+100].lower()
        if any(word in context for word in ["replace", "overwrite", "rewrite"]):
            return "replace"
        
        return "update"
    
    def _extract_reason(self, response: str, position: int) -> str:
        """Extract the reason for modification from surrounding context."""
        # Look for reason indicators
        context = response[max(0, position-200):position+200]
        
        reason_patterns = [
            r"(?:to|for|because|in order to)\s+([^.!?]+)[.!?]",
            r"(?:this will|this should|which will)\s+([^.!?]+)[.!?]",
        ]
        
        for pattern in reason_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "AI suggested modification"
    
    def _deduplicate_modifications(self, modifications: List[Dict]) -> List[Dict]:
        """Remove duplicate modification requests."""
        seen = set()
        unique = []
        
        for mod in modifications:
            key = (mod["file_path"], mod["content"][:50])  # Use first 50 chars as key
            if key not in seen:
                seen.add(key)
                unique.append(mod)
        
        return unique
    
    def create_diff_preview(self, file_path: str, new_content: str) -> Optional[str]:
        """Create a diff preview for file changes."""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            return f"New file: {file_path}\n\n{new_content[:500]}..."
        
        try:
            old_content = full_path.read_text()
            diff = difflib.unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                n=3
            )
            return "".join(diff)
        except Exception as e:
            logger.error(f"Error creating diff: {e}")
            return None
    
    def validate_modifications(self, modifications: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate modifications and separate into safe and unsafe.
        
        Returns:
            (safe_modifications, unsafe_modifications)
        """
        safe = []
        unsafe = []
        
        for mod in modifications:
            # Validate file path
            try:
                full_path = (self.base_path / mod["file_path"]).resolve()
                if not str(full_path).startswith(str(self.base_path)):
                    mod["error"] = "Path traversal detected"
                    unsafe.append(mod)
                    continue
            except:
                mod["error"] = "Invalid file path"
                unsafe.append(mod)
                continue
            
            # Validate content
            from ..api.endpoints.self_aware import validate_code_safety
            validation = validate_code_safety(mod["content"])
            
            if not validation.is_safe:
                mod["error"] = f"Dangerous patterns detected: {', '.join(validation.dangerous_patterns)}"
                mod["warnings"] = validation.warnings
                unsafe.append(mod)
            else:
                if validation.warnings:
                    mod["warnings"] = validation.warnings
                safe.append(mod)
        
        return safe, unsafe
    
    def format_modification_summary(self, modifications: List[Dict]) -> str:
        """Format a human-readable summary of modifications."""
        if not modifications:
            return "No file modifications requested."
        
        summary = f"File Modification Summary ({len(modifications)} files):\n\n"
        
        for i, mod in enumerate(modifications, 1):
            summary += f"{i}. {mod['operation'].title()} {mod['file_path']}\n"
            summary += f"   Reason: {mod['reason']}\n"
            if mod.get('warnings'):
                summary += f"   ⚠️ Warnings: {', '.join(mod['warnings'])}\n"
            summary += "\n"
        
        return summary

# Singleton instance
_self_aware_service = None

def get_self_aware_service() -> SelfAwareService:
    """Get or create the self-aware service instance."""
    global _self_aware_service
    if _self_aware_service is None:
        _self_aware_service = SelfAwareService()
    return _self_aware_service