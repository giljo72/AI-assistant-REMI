"""
Enhanced prompts for better code display formatting
"""

def get_code_display_prompt():
    """Get formatting instructions for code display"""
    return """
When displaying code files, use the following formatting guidelines:

For Python files:
- Use ```python for syntax highlighting
- Add comments to highlight important sections with # 🔵 for functions, # 🟢 for classes, # 🟡 for important notes
- Keep line numbers if provided

For JavaScript/TypeScript:
- Use ```javascript or ```typescript 
- Add // 🔵 for functions, // 🟢 for classes, // 🟡 for important notes

For Markdown files:
- Use ```markdown for syntax highlighting
- Headers will be automatically highlighted by the markdown renderer

For JSON files:
- Use ```json for proper formatting

Example Python display:
```python
# 🟢 Main class definition
class AIAssistantStopper:
    def __init__(self):
        # 🟡 Configuration for services
        self.services_to_stop = {
            "Frontend": {"ports": [5173]},
        }
    
    # 🔵 Core method
    def stop_process(self, process):
        '''Stop a process gracefully'''
        process.terminate()
```

IMPORTANT: When showing file contents, display them in a code block with proper syntax highlighting. The dark theme will handle the colors.
"""

def enhance_file_display_for_ai(content: str, file_type: str) -> str:
    """
    Add visual markers to help AI format code better
    """
    if file_type == 'python':
        lines = content.split('\n')
        enhanced_lines = []
        
        for line in lines:
            # Add visual markers for important elements
            if line.strip().startswith('class '):
                enhanced_lines.append(f"# 🟢 CLASS DEFINITION")
                enhanced_lines.append(line)
            elif line.strip().startswith('def '):
                if '__init__' in line:
                    enhanced_lines.append(f"    # 🟡 Constructor")
                else:
                    enhanced_lines.append(f"    # 🔵 Method")
                enhanced_lines.append(line)
            elif line.strip().startswith('# ') and len(line.strip()) > 2:
                # Enhance existing comments
                enhanced_lines.append(line.replace('# ', '# 📝 ', 1))
            else:
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    elif file_type == 'markdown':
        lines = content.split('\n')
        enhanced_lines = []
        
        for line in lines:
            if line.startswith('# '):
                enhanced_lines.append(f"🔷 {line}")  # Main header
            elif line.startswith('## '):
                enhanced_lines.append(f"🔹 {line}")  # Section header
            elif line.startswith('### '):
                enhanced_lines.append(f"▪️ {line}")  # Subsection
            else:
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    return content  # Return as-is for other file types