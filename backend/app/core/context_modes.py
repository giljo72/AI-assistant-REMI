"""
Context modes configuration that ties to chunking strategies.
"""

from typing import Dict, List, Optional
from enum import Enum

class ContextMode(str, Enum):
    """Available context modes."""
    QUICK_ANSWER = "quick_answer"
    STANDARD = "standard"
    DEEP_RESEARCH = "deep_research"
    CUSTOM = "custom"

# Context mode configurations
CONTEXT_MODES = {
    "quick_answer": {
        "name": "Quick Answer",
        "description": "Fast responses using key facts and summaries",
        "context_depth": 0.2,
        "chunk_preferences": {
            "primary": "micro",  # 500 chars
            "secondary": "standard",  # 3000 chars
            "include_summaries": True
        },
        "search_config": {
            "limit": 3,
            "similarity_threshold": 0.02,
            "prefer_recent": True
        }
    },
    "standard": {
        "name": "Standard",
        "description": "Balanced depth and context",
        "context_depth": 0.5,
        "chunk_preferences": {
            "primary": "standard",  # 3000 chars
            "secondary": "large",  # 8000 chars
            "include_summaries": False
        },
        "search_config": {
            "limit": 5,
            "similarity_threshold": 0.01,
            "prefer_recent": False
        }
    },
    "deep_research": {
        "name": "Deep Research", 
        "description": "Comprehensive analysis using all available knowledge",
        "context_depth": 0.8,
        "chunk_preferences": {
            "primary": "large",  # 8000 chars
            "secondary": "full_section",  # 15000 chars
            "include_summaries": True,
            "include_neighbors": True  # Include chunks before/after
        },
        "search_config": {
            "limit": 10,
            "similarity_threshold": 0.005,  # Very low threshold
            "prefer_recent": False,
            "expand_context": True  # Get surrounding chunks
        }
    }
}

def get_chunk_strategy_for_mode(mode: str, available_chunks: Dict[str, List]) -> Dict:
    """
    Determine which chunks to search based on context mode.
    
    Args:
        mode: Context mode name
        available_chunks: Dict of available chunk levels for the document
        
    Returns:
        Search strategy configuration
    """
    mode_config = CONTEXT_MODES.get(mode, CONTEXT_MODES["standard"])
    
    # Build search strategy
    strategy = {
        "search_levels": [],
        "weights": {},
        "config": mode_config["search_config"]
    }
    
    # Determine which chunk levels to search
    chunk_prefs = mode_config["chunk_preferences"]
    
    # Primary level gets highest weight
    if chunk_prefs["primary"] in available_chunks:
        strategy["search_levels"].append(chunk_prefs["primary"])
        strategy["weights"][chunk_prefs["primary"]] = 1.0
    
    # Secondary level gets lower weight
    if chunk_prefs["secondary"] in available_chunks:
        strategy["search_levels"].append(chunk_prefs["secondary"])
        strategy["weights"][chunk_prefs["secondary"]] = 0.7
    
    # For deep research, include all available levels
    if mode == "deep_research":
        for level in available_chunks:
            if level not in strategy["search_levels"]:
                strategy["search_levels"].append(level)
                strategy["weights"][level] = 0.5
    
    return strategy

def should_create_multiple_chunks(document_type: str, filename: str) -> List[str]:
    """
    Determine which chunk sizes to create for a document.
    
    Returns list of chunk levels to create.
    """
    # Business documents get all sizes
    business_keywords = ["strategy", "plan", "report", "proposal", "analysis"]
    if any(keyword in filename.lower() for keyword in business_keywords):
        return ["micro", "standard", "large", "full_section"]
    
    # Technical docs get medium sizes
    tech_keywords = ["api", "spec", "documentation", "technical"]
    if any(keyword in filename.lower() for keyword in tech_keywords):
        return ["standard", "large"]
    
    # Default: just standard
    return ["standard"]

# Chunk level definitions
CHUNK_LEVELS = {
    "micro": {
        "size": 500,
        "overlap": 100,
        "description": "Precise facts and figures"
    },
    "standard": {
        "size": 3000,
        "overlap": 500,
        "description": "Balanced context"
    },
    "large": {
        "size": 8000,
        "overlap": 1500,
        "description": "Full business context"
    },
    "full_section": {
        "size": 15000,
        "overlap": 3000,
        "description": "Complete sections"
    }
}