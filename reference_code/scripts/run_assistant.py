# scripts/run_assistant.py
import os
import sys
from pathlib import Path
import subprocess

# Add parent directory to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

def main():
    """Run the AI Assistant application"""
    print("Starting AI Assistant...")
    
    # Path to the Gradio app
    app_path = project_root / "src" / "gradio" / "app.py"
    
    if not app_path.exists():
        print(f"Error: App file not found at {app_path}")
        return False
    
    # Run the Gradio app
    try:
        subprocess.run([sys.executable, str(app_path)])
        return True
    except KeyboardInterrupt:
        print("\nShutting down AI Assistant...")
        return True
    except Exception as e:
        print(f"Error running AI Assistant: {e}")
        return False

if __name__ == "__main__":
    main()