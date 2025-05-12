# scripts/create_css_file.py
import os
from pathlib import Path

# Define the custom CSS content
custom_css_content = """# src/gradio/utils/custom_css.py

def get_custom_css():
    \"\"\"Return custom CSS for the application\"\"\"
    return \"\"\"
    /* Project sidebar styling */
    .sidebar-container {
        background-color: #080d13 !important;
        border-right: 1px solid #2d3748 !important;
    }
    
    /* Project headers */
    .project-header {
        color: #ffc300 !important;
        font-weight: bold !important;
        margin-top: 8px !important;
    }
    
    /* Chat items */
    .chat-item {
        color: #ffffff !important;
        margin-left: 15px !important;
        cursor: pointer !important;
    }
    
    /* User messages */
    .user-message {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        padding: 10px !important;
        margin-left: 30% !important;
    }
    
    /* Assistant messages */
    .assistant-message {
        background-color: #121922 !important;
        color: #ffc300 !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    /* Project title */
    .project-title {
        color: #ffc300 !important;
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 10px !important;
        background-color: #080d13 !important;
    }
    
    /* Button icons */
    .icon-button {
        background-color: transparent !important;
        border: none !important;
        color: #ffc300 !important;
        cursor: pointer !important;
    }
    
    /* Memory scope section */
    .memory-scope {
        background-color: #121922 !important;
        border: 1px solid #2d3748 !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    /* Context buttons */
    .context-button {
        background-color: #ffc300 !important;
        color: #080d13 !important;
        border-radius: 20px !important;
        padding: 8px 16px !important;
        font-weight: bold !important;
    }
    \"\"\"
"""

# Create the file path
project_root = Path(__file__).parent.parent
utils_dir = project_root / "src" / "gradio" / "utils"

# Create the directory if it doesn't exist
utils_dir.mkdir(parents=True, exist_ok=True)

# Create the custom CSS file
css_file_path = utils_dir / "custom_css.py"
with open(css_file_path, "w") as f:
    f.write(custom_css_content)

print(f"Created custom CSS file at: {css_file_path}")