#!/usr/bin/env python3
"""
Test script for the embedding service implementation.
Tests the real embedding generation using sentence-transformers.
"""

import asyncio
import time
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.embedding_service import EmbeddingService, get_embedding_service


async def test_embedding_service():
    print("=== Testing Embedding Service ===\n")
    
    # Create embedding service instance
    print("1. Creating embedding service...")
    service = get_embedding_service()
    
    # Test single text embedding
    print("\n2. Testing single text embedding...")
    test_text = "This is a test document about artificial intelligence and machine learning."
    
    start_time = time.time()
    embedding = await service.embed_text(test_text)
    end_time = time.time()
    
    print(f"   - Text: '{test_text[:50]}...'")
    print(f"   - Embedding dimension: {len(embedding)}")
    print(f"   - First 5 values: {embedding[:5]}")
    print(f"   - Time taken: {(end_time - start_time):.3f} seconds")
    
    # Verify embedding properties
    assert len(embedding) == 768, f"Expected 768 dimensions, got {len(embedding)}"
    assert all(isinstance(x, float) for x in embedding), "All values should be floats"
    print("   ✓ Single embedding test passed!")
    
    # Test batch embeddings
    print("\n3. Testing batch embeddings...")
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
    print(f"   - Number of embeddings: {len(embeddings)}")
    print(f"   - Time taken: {(end_time - start_time):.3f} seconds")
    
    # Verify batch embeddings
    assert len(embeddings) == len(test_texts), "Should have one embedding per text"
    for i, emb in enumerate(embeddings):
        assert len(emb) == 768, f"Embedding {i} has wrong dimension"
        if test_texts[i] == "":
            assert all(x == 0.0 for x in emb), "Empty text should have zero embedding"
    print("   ✓ Batch embedding test passed!")
    
    # Test similarity between embeddings
    print("\n4. Testing embedding similarity...")
    text1 = "Machine learning is a subset of artificial intelligence"
    text2 = "AI and ML are closely related fields"
    text3 = "The weather today is sunny and warm"
    
    emb1 = await service.embed_text(text1)
    emb2 = await service.embed_text(text2)
    emb3 = await service.embed_text(text3)
    
    # Calculate cosine similarity
    import numpy as np
    
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    sim_12 = cosine_similarity(emb1, emb2)
    sim_13 = cosine_similarity(emb1, emb3)
    
    print(f"   - Similarity (ML vs AI): {sim_12:.3f}")
    print(f"   - Similarity (ML vs Weather): {sim_13:.3f}")
    
    assert sim_12 > sim_13, "Related texts should have higher similarity"
    print("   ✓ Similarity test passed!")
    
    # Test model info
    print("\n5. Testing model info...")
    info = await service.get_model_info()
    print(f"   - Model: {info['model_name']}")
    print(f"   - Dimension: {info['dimension']}")
    print(f"   - Device: {info['device']}")
    print(f"   - Max sequence length: {info['max_seq_length']}")
    
    print("\n=== All tests passed! ===")


if __name__ == "__main__":
    try:
        asyncio.run(test_embedding_service())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)