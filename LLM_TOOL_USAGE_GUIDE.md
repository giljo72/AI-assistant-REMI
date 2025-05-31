# LLM Tool Usage Guide for Code Modifications

## Tool Patterns for Your LLM

### Reading Files
When user asks to see a file:
```
Tool: file_operations
Action: read
Parameters: {
  "path": "F:/assistant/stopai.bat"
}
```

### Editing Files
When user asks to change something:
```
Tool: file_operations
Action: edit
Parameters: {
  "path": "F:/assistant/stopai.bat",
  "pattern": "color 0C",
  "replacement": "color 09"
}
```

### Writing New Files
When creating new files:
```
Tool: file_operations
Action: write
Parameters: {
  "path": "F:/assistant/new_file.py",
  "content": "# File content here"
}
```

## Training Your LLM

1. **Be Explicit**: Instead of "change the color to blue", say "edit the file stopai.bat and change 'color 0C' to 'color 09'"

2. **Provide Context**: Tell the LLM what type of file it is and where it's located

3. **Use Templates**: Create templates for common operations

## Example Interactions:

### Good:
"Edit the file F:\assistant\stopai.bat. Find the line that says 'color 0C' and change it to 'color 09' to make the text blue instead of red."

### Better:
"Use the file_operations tool to edit F:\assistant\stopai.bat. Replace the string 'color 0C' with 'color 09'. This will change the console text from red to blue."

### Best:
"Task: Change console text color in stopai.bat from red to blue
1. Use file_operations tool with action='read' to read F:\assistant\stopai.bat
2. Find the line containing 'color 0C' 
3. Use file_operations tool with action='edit' to replace 'color 0C' with 'color 09'
4. Verify the change was made"