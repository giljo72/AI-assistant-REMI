#!/usr/bin/env python3
"""
Test script for the mock NeMo module implementation.
This script verifies that the mock NeMo module functions correctly.
"""

import os
import sys

print("Testing NeMo mock implementation...")

# Add the project root to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try to import the mock
    from backend.app.core.mock_nemo import load_model, get_embeddings
    
    # Try to initialize the model
    model = load_model("test-model")
    
    # Test generation
    print("\nTesting text generation...")
    test_prompts = [
        "What is artificial intelligence?",
        "Tell me about machine learning models"
    ]
    
    for prompt in test_prompts:
        response = model.generate(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"Response: {response}")
    
    # Test embeddings (if numpy is available)
    try:
        import numpy as np
        print("\nTesting embeddings generation...")
        
        text = "This is a test document"
        embedding = model.embeddings(text)
        print(f"Text: {text}")
        print(f"Embedding shape: {embedding.shape}")
        print(f"Embedding norm: {np.linalg.norm(embedding):.6f}")
        
        # Test batch embeddings
        texts = ["Text 1", "Text 2", "Text 3"]
        batch_embeddings = get_embeddings(texts)
        print(f"Batch embeddings count: {len(batch_embeddings)}")
        
    except ImportError:
        print("\nSkipping embedding tests - numpy not available")
        print("To test embeddings, install numpy: pip install numpy")
    
    print("\nMock NeMo implementation test successful!")
    
except Exception as e:
    print(f"Error testing mock NeMo: {e}")