#!/usr/bin/env python3
"""Quick check of currently installed Ollama models"""

import subprocess
import requests

def check_ollama_models():
    print("Checking installed Ollama models...\n")
    
    # Try API first
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print("Installed models:")
                for model in models:
                    name = model.get("name", "Unknown")
                    size = model.get("size", 0)
                    size_gb = f"{size / (1024**3):.1f}GB" if size > 0 else "Unknown"
                    print(f"  ✓ {name} ({size_gb})")
            else:
                print("No models installed yet!")
            return models
    except:
        pass
    
    # Fallback to command
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Installed models (via CLI):")
            print(result.stdout)
        else:
            print("Could not fetch model list. Is Ollama running?")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Ollama is running with: ollama serve")

if __name__ == "__main__":
    check_ollama_models()