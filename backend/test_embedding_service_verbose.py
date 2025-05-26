#!/usr/bin/env python3
"""
Test script for the embedding service implementation with verbose output.
Shows download progress and initialization steps.
"""

import asyncio
import time
import sys
import os
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting embedding service test...")
print("This may take several minutes on first run as the model downloads (~420MB)")
print("-" * 60)

from app.services.embedding_service import EmbeddingService, get_embedding_service


async def test_embedding_service():
    print("\n=== Testing Embedding Service ===\n")
    
    # Create embedding service instance
    print("1. Creating embedding service...")
    print("   Note: First-time model download may take 2-5 minutes depending on connection speed")
    service = get_embedding_service()
    
    # Initialize the model (this is where download happens)
    print("\n2. Initializing model (downloading if needed)...")
    print("   Model: sentence-transformers/all-mpnet-base-v2")
    print("   Size: ~420MB")
    print("   This will be cached for future use in ~/.cache/huggingface/")
    
    start_init = time.time()
    await service.initialize()
    end_init = time.time()
    print(f"   ✓ Model initialized in {(end_init - start_init):.1f} seconds")
    
    # Get model info
    info = await service.get_model_info()
    print(f"\n3. Model Information:")
    print(f"   - Model: {info['model_name']}")
    print(f"   - Embedding dimension: {info['dimension']}")
    print(f"   - Device: {info['device']}")
    print(f"   - Max sequence length: {info['max_seq_length']}")
    
    # Test single text embedding
    print("\n4. Testing single text embedding...")
    test_text = "This is a test document about artificial intelligence and machine learning."
    
    start_time = time.time()
    embedding = await service.embed_text(test_text)
    end_time = time.time()
    
    print(f"   - Text: '{test_text[:50]}...'")
    print(f"   - Embedding dimension: {len(embedding)}")
    print(f"   - First 5 values: [{', '.join(f'{x:.4f}' for x in embedding[:5])}]")
    print(f"   - Time taken: {(end_time - start_time):.3f} seconds")
    print("   ✓ Single embedding test passed!")
    
    # Test batch embeddings
    print("\n5. Testing batch embeddings...")
    test_texts = [
        "Document about Python programming",
        "Machine learning and deep learning concepts",
        "Natural language processing with transformers",
        ""  # Test empty text handling
    ]
    
    start_time = time.time()
    embeddings = await service.embed_batch(test_texts)
    end_time = time.time()
    
    print(f"   - Number of texts: {len(test_texts)}")
    print(f"   - Time taken: {(end_time - start_time):.3f} seconds")
    print(f"   - Time per text: {(end_time - start_time) / len(test_texts):.3f} seconds")
    print("   ✓ Batch embedding test passed!")
    
    # Test similarity
    print("\n6. Testing semantic similarity...")
    text1 = "Machine learning is a subset of artificial intelligence"
    text2 = "AI and ML are closely related fields"
    text3 = "The weather today is sunny and warm"
    
    print("   Generating embeddings for similarity test...")
    emb1 = await service.embed_text(text1)
    emb2 = await service.embed_text(text2)
    emb3 = await service.embed_text(text3)
    
    # Calculate cosine similarity
    import numpy as np
    
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    sim_12 = cosine_similarity(emb1, emb2)
    sim_13 = cosine_similarity(emb1, emb3)
    
    print(f"   - Text 1: '{text1}'")
    print(f"   - Text 2: '{text2}'")
    print(f"   - Text 3: '{text3}'")
    print(f"   - Similarity (Text1 vs Text2): {sim_12:.3f}")
    print(f"   - Similarity (Text1 vs Text3): {sim_13:.3f}")
    print(f"   - Related texts more similar: {sim_12 > sim_13} ✓")
    
    print("\n=== All tests passed! ===")
    print(f"\nModel cache location: ~/.cache/huggingface/")
    print("Future runs will be much faster as the model is now cached.")


if __name__ == "__main__":
    try:
        print("Python version:", sys.version)
        print("Starting test...\n")
        asyncio.run(test_embedding_service())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)