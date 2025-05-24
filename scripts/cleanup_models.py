#!/usr/bin/env python3
"""
Model Cleanup Script
Removes redundant models to keep only the essential set:
- Qwen 32B (default)
- Llama 70B NIM (complex tasks) 
- Mistral Nemo (speed)
- DeepSeek Coder (coding)
"""

import subprocess
import sys
import requests
import json

def get_ollama_models():
    """Get list of installed Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return response.json().get("models", [])
    except:
        # Fallback to command line
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                models = []
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            models.append({"name": parts[0]})
                return models
        except:
            pass
    return []

def remove_model(model_name):
    """Remove an Ollama model"""
    print(f"Removing {model_name}...")
    try:
        result = subprocess.run(['ollama', 'rm', model_name], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Successfully removed {model_name}")
            return True
        else:
            print(f"✗ Failed to remove {model_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error removing {model_name}: {e}")
        return False

def main():
    # Models to keep
    KEEP_MODELS = {
        "qwen2.5:32b-instruct-q4_K_M",
        "llama3.1:70b-instruct-q4_K_M",  # This is actually NIM, but might show in ollama list
        "mistral-nemo:latest",
        "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
    }
    
    # Known redundant models to remove
    REMOVE_MODELS = [
        "mistral-nemo:12b-instruct-2407-q4_0",  # Duplicate of mistral-nemo:latest
        "llama3.1:8b-instruct",  # Redundant with 70B and Mistral for light tasks
        "phi3.5:latest",  # If exists, not in your final list
        "codellama:latest",  # Replaced by deepseek-coder
    ]
    
    print("AI Assistant Model Cleanup")
    print("=" * 50)
    print("\nModels to KEEP:")
    for model in KEEP_MODELS:
        print(f"  ✓ {model}")
    
    print("\nModels to REMOVE:")
    for model in REMOVE_MODELS:
        print(f"  ✗ {model}")
    
    print("\nFetching installed models...")
    installed_models = get_ollama_models()
    
    if not installed_models:
        print("Could not fetch model list. Is Ollama running?")
        print("Start Ollama with: ollama serve")
        return
    
    print(f"\nFound {len(installed_models)} installed models:")
    for model in installed_models:
        model_name = model.get("name", "Unknown")
        model_size = model.get("size", 0)
        if isinstance(model_size, int) and model_size > 0:
            size_str = f" ({model_size / (1024**3):.1f}GB)"
        else:
            size_str = f" ({model_size})" if model_size else ""
        print(f"  - {model_name}{size_str}")
    
    # Find models to remove
    models_to_remove = []
    for model in installed_models:
        model_name = model.get("name", "")
        if model_name in REMOVE_MODELS:
            models_to_remove.append(model_name)
        elif model_name and model_name not in KEEP_MODELS:
            # Check if it's a model we didn't explicitly list
            print(f"\nFound additional model: {model_name}")
            response = input("Remove this model? (y/n): ")
            if response.lower() == 'y':
                models_to_remove.append(model_name)
    
    if not models_to_remove:
        print("\nNo models to remove. Your collection is already optimized!")
        return
    
    print(f"\nAbout to remove {len(models_to_remove)} models:")
    for model in models_to_remove:
        print(f"  - {model}")
    
    response = input("\nProceed with cleanup? (y/n): ")
    if response.lower() != 'y':
        print("Cleanup cancelled.")
        return
    
    print("\nStarting cleanup...")
    success_count = 0
    for model in models_to_remove:
        if remove_model(model):
            success_count += 1
    
    print(f"\nCleanup complete! Removed {success_count}/{len(models_to_remove)} models.")
    
    # Show final state
    print("\nFinal model collection:")
    remaining_models = get_ollama_models()
    for model in remaining_models:
        model_name = model.get("name", "")
        if model_name in KEEP_MODELS:
            print(f"  ✓ {model_name} (KEPT)")
        else:
            print(f"  ? {model_name} (Unknown - consider removing)")

if __name__ == "__main__":
    main()