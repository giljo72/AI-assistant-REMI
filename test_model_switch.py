#!/usr/bin/env python3
"""
Quick test to verify model switching functionality
"""

import requests
import time
import json

def test_model_switch():
    base_url = "http://localhost:8000"
    
    print("Testing Model Switching Functionality")
    print("=" * 50)
    
    # Check current status
    print("\n1. Checking current model status...")
    response = requests.get(f"{base_url}/api/system/models/status")
    if response.status_code == 200:
        status = response.json()
        system = status['system']
        print(f"   Current mode: {system['mode']}")
        print(f"   VRAM usage: {system['used_vram_gb']:.1f}GB / {system['total_vram_gb']}GB")
        print(f"   Available VRAM: {system['available_vram_gb']:.1f}GB")
        
        print("\n   Loaded models:")
        for model_name, model_info in status['models'].items():
            if model_info['status'] == 'loaded':
                print(f"   - {model_info['display_name']} ({model_info['backend']})")
    else:
        print(f"   ERROR: Failed to get status: {response.status_code}")
        return
    
    # Test switching to different models
    print("\n2. Testing model switching...")
    
    models_to_test = [
        ("mistral-nemo:latest", "Mistral Nemo - Quick responses"),
        ("qwen2.5:32b-instruct-q4_K_M", "Qwen 2.5 32B - Default model"),
        ("deepseek-coder-v2:16b-lite-instruct-q4_K_M", "DeepSeek Coder - Coding mode"),
        ("llama3.1:70b-instruct-q4_K_M", "Llama 70B - Solo deep reasoning")
    ]
    
    for model_name, description in models_to_test:
        print(f"\n   Switching to: {description}")
        
        response = requests.post(
            f"{base_url}/api/system/models/switch",
            json={"model_name": model_name}
        )
        
        if response.status_code == 200:
            print(f"   ✓ Successfully initiated switch to {model_name}")
            
            # Wait a bit for the switch to complete
            time.sleep(3)
            
            # Check the status
            status_response = requests.get(f"{base_url}/api/system/models/status")
            if status_response.status_code == 200:
                status = status_response.json()
                system = status['system']
                
                # Check if the model is loaded
                model_status = status['models'].get(model_name, {})
                if model_status.get('status') == 'loaded':
                    print(f"   ✓ Model loaded successfully")
                    print(f"   VRAM usage: {system['used_vram_gb']:.1f}GB")
                    
                    # For Llama 70B, check if other models were unloaded
                    if model_name == "llama3.1:70b-instruct-q4_K_M":
                        loaded_count = sum(1 for m in status['models'].values() if m['status'] == 'loaded')
                        if loaded_count == 1:
                            print(f"   ✓ Solo mode confirmed - only Llama 70B is loaded")
                        else:
                            print(f"   ⚠ Warning: {loaded_count} models loaded in solo mode")
                else:
                    print(f"   ⚠ Model status: {model_status.get('status', 'unknown')}")
                    if model_status.get('error_message'):
                        print(f"   Error: {model_status['error_message']}")
        else:
            print(f"   ✗ Failed to switch: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error.get('detail', 'Unknown error')}")
            except:
                pass
    
    # Test mode switching
    print("\n3. Testing operational modes...")
    
    modes = [
        ("quick", "Quick Response Mode"),
        ("business_fast", "Business Fast Mode"),
        ("development", "Development Mode"),
        ("balanced", "Balanced Mode")
    ]
    
    for mode_id, mode_name in modes:
        print(f"\n   Switching to: {mode_name}")
        
        response = requests.post(
            f"{base_url}/api/system/models/mode",
            json={"mode": mode_id}
        )
        
        if response.status_code == 200:
            print(f"   ✓ Successfully switched to {mode_id} mode")
            time.sleep(2)
            
            # Verify the mode
            status_response = requests.get(f"{base_url}/api/system/models/status")
            if status_response.status_code == 200:
                current_mode = status_response.json()['system']['mode']
                if current_mode == mode_id:
                    print(f"   ✓ Mode verified: {current_mode}")
                else:
                    print(f"   ⚠ Mode mismatch: expected {mode_id}, got {current_mode}")
        else:
            print(f"   ✗ Failed to switch mode: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("Model switching test complete!")

if __name__ == "__main__":
    test_model_switch()