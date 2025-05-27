"""
Document chunking strategies API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ...db.database import get_db
from ...document_processing.advanced_chunking_config import (
    CHUNKING_STRATEGIES,
    get_chunking_strategy,
    calculate_storage_estimate
)

router = APIRouter()

@router.get("/chunking-strategies", response_model=Dict[str, Any])
async def get_available_strategies():
    """Get all available chunking strategies."""
    strategies = {}
    for name, config in CHUNKING_STRATEGIES.items():
        strategies[name] = {
            "name": name,
            "chunk_size": config["chunk_size"],
            "chunk_overlap": config["chunk_overlap"],
            "description": config["description"],
            "typical_use_cases": _get_use_cases(name)
        }
    return {"strategies": strategies}

@router.post("/detect-strategy", response_model=Dict[str, Any])
async def detect_document_strategy(filename: str):
    """Detect the best chunking strategy for a filename."""
    strategy = get_chunking_strategy(filename=filename)
    return {
        "filename": filename,
        "detected_strategy": strategy,
        "can_override": True
    }

@router.get("/storage-estimate", response_model=Dict[str, Any])
async def estimate_storage(
    num_documents: int = 100,
    avg_doc_size_mb: float = 5.0
):
    """Estimate storage requirements for different strategies."""
    estimates = calculate_storage_estimate(num_documents, avg_doc_size_mb)
    
    return {
        "parameters": {
            "num_documents": num_documents,
            "avg_doc_size_mb": avg_doc_size_mb
        },
        "estimates": estimates,
        "recommendation": _get_storage_recommendation(estimates)
    }

def _get_use_cases(strategy_name: str) -> List[str]:
    """Get typical use cases for a strategy."""
    use_cases = {
        "standard": [
            "General documents",
            "Emails and memos",
            "Short reports",
            "Meeting notes"
        ],
        "business_context": [
            "Business plans",
            "Strategy documents",
            "Annual reports",
            "Case studies",
            "Proposals"
        ],
        "full_section": [
            "Research papers",
            "Books and manuals",
            "Comprehensive reports",
            "Legal documents"
        ],
        "technical_docs": [
            "API documentation",
            "Technical specifications",
            "Code documentation",
            "Architecture documents"
        ]
    }
    return use_cases.get(strategy_name, [])

def _get_storage_recommendation(estimates: Dict) -> str:
    """Get storage recommendation based on estimates."""
    total_gb = sum(e["total_storage_gb"] for e in estimates.values())
    
    if total_gb < 10:
        return "Storage requirements are minimal. Use the most context-preserving strategy."
    elif total_gb < 100:
        return "Storage requirements are moderate. Consider using business_context as default."
    else:
        return "Storage requirements are significant. Consider a mixed approach based on document importance."