"""
Advanced chunking configuration for business context preservation.
"""

# Chunking strategies for different use cases
CHUNKING_STRATEGIES = {
    "standard": {
        "chunk_size": 3000,
        "chunk_overlap": 500,
        "description": "Balanced approach for general documents"
    },
    "business_context": {
        "chunk_size": 8000,  # ~1200-1600 words, 2-3 pages
        "chunk_overlap": 1500,  # Significant overlap to maintain context
        "description": "Large chunks for business cases, strategies, reports"
    },
    "full_section": {
        "chunk_size": 15000,  # ~2250-3000 words, 5-6 pages
        "chunk_overlap": 3000,
        "description": "Entire sections/chapters for comprehensive analysis"
    },
    "technical_docs": {
        "chunk_size": 5000,
        "chunk_overlap": 1000,
        "description": "Technical documentation with code examples"
    }
}

# Document type detection and strategy mapping
DOCUMENT_TYPE_STRATEGIES = {
    # Business documents
    "business_plan": "business_context",
    "strategy": "business_context", 
    "annual_report": "business_context",
    "case_study": "business_context",
    "proposal": "business_context",
    
    # Technical documents
    "technical_spec": "technical_docs",
    "api_documentation": "technical_docs",
    "code_documentation": "technical_docs",
    
    # General documents
    "memo": "standard",
    "email": "standard",
    "meeting_notes": "standard",
    
    # Large documents needing full context
    "whitepaper": "full_section",
    "research_paper": "full_section",
    "book": "full_section",
    "manual": "full_section"
}

# Hierarchical chunking configuration
HIERARCHICAL_CHUNKING = {
    "enabled": True,
    "levels": [
        {
            "name": "paragraph",
            "size": 500,
            "overlap": 100
        },
        {
            "name": "section", 
            "size": 3000,
            "overlap": 500
        },
        {
            "name": "chapter",
            "size": 10000,
            "overlap": 2000
        },
        {
            "name": "document",
            "size": 50000,  # Full document summary
            "overlap": 0
        }
    ]
}

# Advanced retrieval configuration
RETRIEVAL_CONFIG = {
    "multi_query": True,  # Generate multiple query variations
    "query_expansion": True,  # Expand queries with synonyms/related terms
    "hierarchical_search": True,  # Search at multiple chunk levels
    "context_window_expansion": {
        "enabled": True,
        "before_chunks": 1,  # Include 1 chunk before match
        "after_chunks": 1    # Include 1 chunk after match
    },
    "reranking": {
        "enabled": True,
        "model": "cross-encoder/ms-marco-MiniLM-L-12-v2",
        "top_k": 10  # Rerank top 10 results
    }
}

# Storage optimization
STORAGE_CONFIG = {
    "compression": {
        "enabled": True,
        "algorithm": "zstd",  # Better than gzip for text
        "level": 3  # Balanced compression
    },
    "deduplication": {
        "enabled": True,
        "similarity_threshold": 0.95  # Dedupe near-identical chunks
    },
    "index_optimization": {
        "use_hnsw": True,  # Hierarchical Navigable Small World graphs
        "m": 16,  # Number of connections
        "ef_construction": 200  # Build-time accuracy
    }
}

def get_chunking_strategy(document_type: str = None, filename: str = None) -> dict:
    """
    Determine the best chunking strategy based on document type or filename.
    """
    # Try to detect document type from filename
    if filename and not document_type:
        filename_lower = filename.lower()
        for doc_type, keywords in [
            ("business_plan", ["business_plan", "bp_", "bizplan"]),
            ("strategy", ["strategy", "strategic"]),
            ("annual_report", ["annual", "yearly", "report"]),
            ("case_study", ["case_study", "case-study", "casestudy"]),
            ("proposal", ["proposal", "rfp", "bid"]),
            ("whitepaper", ["whitepaper", "white-paper"]),
            ("technical_spec", ["spec", "technical", "requirements"]),
        ]:
            if any(keyword in filename_lower for keyword in keywords):
                document_type = doc_type
                break
    
    # Get strategy
    strategy_name = DOCUMENT_TYPE_STRATEGIES.get(
        document_type, 
        "business_context"  # Default to business context for your use case
    )
    
    return CHUNKING_STRATEGIES[strategy_name]

def calculate_storage_estimate(num_documents: int, avg_doc_size_mb: float = 5) -> dict:
    """
    Estimate storage requirements for different strategies.
    """
    estimates = {}
    
    for strategy_name, config in CHUNKING_STRATEGIES.items():
        chunk_size = config["chunk_size"]
        overlap = config["chunk_overlap"]
        
        # Rough calculation of chunks per document
        avg_chars = avg_doc_size_mb * 1024 * 1024  # Rough char estimate
        chunks_per_doc = (avg_chars / (chunk_size - overlap)) * 1.2  # 20% overhead
        
        # Storage per document (chunks + embeddings + metadata)
        storage_per_chunk_mb = 0.01  # ~10KB per chunk with embedding
        storage_per_doc_mb = chunks_per_doc * storage_per_chunk_mb
        
        estimates[strategy_name] = {
            "chunks_per_doc": int(chunks_per_doc),
            "storage_per_doc_mb": round(storage_per_doc_mb, 2),
            "total_storage_gb": round((storage_per_doc_mb * num_documents) / 1024, 2)
        }
    
    return estimates