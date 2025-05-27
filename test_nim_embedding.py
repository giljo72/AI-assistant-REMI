#!/usr/bin/env python3
"""Test NIM embedding service to diagnose 400 errors."""

import asyncio
import httpx
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_nim_embeddings():
    """Test NIM embedding API directly"""
    base_url = "http://localhost:8081"
    
    # Test 1: Health check
    print("\n=== Testing NIM health check ===")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/v1/health/ready")
            print(f"Health check status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Health check failed: {e}")
            return
    
    # Test 2: Test embedding with different payloads
    print("\n=== Testing NIM embeddings ===")
    
    test_payloads = [
        # Test 1: Single text as string (may be incorrect)
        {
            "name": "Single text as string",
            "payload": {
                "input": "This is a test document chunk",
                "model": "nvidia/nv-embedqa-e5-v5",
                "input_type": "passage"
            }
        },
        # Test 2: Single text in array (correct format)
        {
            "name": "Single text in array",
            "payload": {
                "input": ["This is a test document chunk"],
                "model": "nvidia/nv-embedqa-e5-v5",
                "input_type": "passage"
            }
        },
        # Test 3: Multiple texts
        {
            "name": "Multiple texts",
            "payload": {
                "input": ["First chunk", "Second chunk", "Third chunk"],
                "model": "nvidia/nv-embedqa-e5-v5",
                "input_type": "passage"
            }
        },
        # Test 4: Query type
        {
            "name": "Query embedding",
            "payload": {
                "input": ["What is the document about?"],
                "model": "nvidia/nv-embedqa-e5-v5",
                "input_type": "query"
            }
        },
        # Test 5: Without input_type
        {
            "name": "Without input_type",
            "payload": {
                "input": ["Test without input type"],
                "model": "nvidia/nv-embedqa-e5-v5"
            }
        }
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for test in test_payloads:
            print(f"\n--- Test: {test['name']} ---")
            print(f"Payload: {json.dumps(test['payload'], indent=2)}")
            
            try:
                response = await client.post(
                    f"{base_url}/v1/embeddings",
                    json=test['payload'],
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Status: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    result = response.json()
                    if 'data' in result and result['data']:
                        embedding_dim = len(result['data'][0]['embedding'])
                        print(f"Success! Embedding dimension: {embedding_dim}")
                        print(f"Number of embeddings: {len(result['data'])}")
                else:
                    print(f"Error response: {response.text}")
                    
            except Exception as e:
                print(f"Request failed: {e}")

    # Test 3: Check what models are available
    print("\n=== Checking available models ===")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/v1/models")
            if response.status_code == 200:
                print(f"Available models: {response.json()}")
            else:
                print(f"Models endpoint status: {response.status_code}")
        except Exception as e:
            print(f"Models check failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_nim_embeddings())