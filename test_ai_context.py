#!/usr/bin/env python3
"""
Test what the AI actually receives
"""
import sys
sys.path.insert(0, 'backend')

from app.api.endpoints.simple_file_access import inject_file_content_if_requested

def test_ai_context(user_message):
    """Build the same context the AI would receive"""
    
    # 1. System message (simplified)
    system_message = {
        "role": "system",
        "content": """You are a helpful AI assistant designed to provide accurate, thoughtful, and practical assistance.

System Information:
- Model: deepseek-coder-v2:16b-lite-instruct-q4_K_M
- Date: Tuesday, January 27, 2025"""
    }
    
    # 2. File content (if any)
    file_content = inject_file_content_if_requested(user_message)
    
    # 3. User message
    user_msg = {
        "role": "user",
        "content": user_message
    }
    
    # Build messages array like the chat endpoint does
    messages = [system_message]
    
    if file_content:
        file_msg = {
            "role": "system",
            "content": file_content
        }
        messages.append(file_msg)
        print(f"✓ File content added: {len(file_content)} chars")
    else:
        print("✗ No file content added")
    
    messages.append(user_msg)
    
    # Print what the AI receives
    print("\n" + "="*60)
    print("MESSAGES SENT TO AI:")
    print("="*60)
    
    for i, msg in enumerate(messages):
        print(f"\n[{i}] Role: {msg['role']}")
        print(f"Content preview (first 500 chars):")
        print("-" * 40)
        print(msg['content'][:500])
        if len(msg['content']) > 500:
            print(f"... (total {len(msg['content'])} chars)")
        print("-" * 40)
    
    return messages

if __name__ == "__main__":
    test_messages = [
        "show stop_assistant.py",
        "hello, how are you?",
        "read test.md"
    ]
    
    for msg in test_messages:
        print(f"\n{'#'*60}")
        print(f"Testing: '{msg}'")
        print(f"{'#'*60}")
        test_ai_context(msg)