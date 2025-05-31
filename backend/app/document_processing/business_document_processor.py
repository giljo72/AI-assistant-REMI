"""
Enhanced document processor for business context preservation.
"""

import asyncio
from typing import List, Dict, Any, Optional
import logging
from .processor import DocumentProcessor
from .advanced_chunking_config import (
    get_chunking_strategy, 
    HIERARCHICAL_CHUNKING,
    RETRIEVAL_CONFIG
)

logger = logging.getLogger(__name__)

class BusinessDocumentProcessor(DocumentProcessor):
    """Enhanced processor for business documents with context preservation."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hierarchical_enabled = HIERARCHICAL_CHUNKING["enabled"]
        
    def process_document_with_strategy(
        self,
        document_path: str,
        document_id: str,
        filetype: str,
        document_type: Optional[str] = None,
        strategy_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process document with intelligent chunking strategy.
        
        Returns:
            Dict containing:
            - chunks: List of standard chunks
            - hierarchical_chunks: Dict of chunks at different levels
            - metadata: Processing metadata
        """
        # Determine chunking strategy
        if strategy_override:
            strategy = CHUNKING_STRATEGIES.get(strategy_override)
        else:
            strategy = get_chunking_strategy(document_type, document_path)
            
        logger.info(f"Using chunking strategy: {strategy['description']}")
        logger.info(f"  Chunk size: {strategy['chunk_size']}")
        logger.info(f"  Overlap: {strategy['chunk_overlap']}")
        
        # Extract full text first
        full_text = self.extract_text(document_path, filetype)
        
        result = {
            "chunks": [],
            "hierarchical_chunks": {},
            "metadata": {
                "strategy_used": strategy,
                "document_length": len(full_text),
                "processing_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Standard chunking
        standard_chunks = self.process_document(
            document_path=document_path,
            document_id=document_id,
            filetype=filetype,
            chunk_size=strategy["chunk_size"],
            chunk_overlap=strategy["chunk_overlap"]
        )
        result["chunks"] = standard_chunks
        
        # Hierarchical chunking if enabled
        if self.hierarchical_enabled:
            for level in HIERARCHICAL_CHUNKING["levels"]:
                level_chunks = self.create_chunks(
                    text=full_text,
                    chunk_size=level["size"],
                    chunk_overlap=level["overlap"]
                )
                result["hierarchical_chunks"][level["name"]] = [
                    {
                        "id": f"{document_id}__{level['name']}__{i}",
                        "content": chunk,
                        "level": level["name"],
                        "chunk_index": i,
                        "metadata": {
                            "chunk_size": len(chunk),
                            "level_config": level
                        }
                    }
                    for i, chunk in enumerate(level_chunks)
                ]
        
        # Add document summary as special chunk
        if len(full_text) > 1000:
            summary_chunk = {
                "id": f"{document_id}__summary",
                "content": full_text[:10000],  # First 10k chars as summary
                "level": "summary",
                "chunk_index": -1,
                "metadata": {
                    "is_summary": True,
                    "full_length": len(full_text)
                }
            }
            result["chunks"].append(summary_chunk)
        
        logger.info(f"Created {len(result['chunks'])} standard chunks")
        if self.hierarchical_enabled:
            for level, chunks in result["hierarchical_chunks"].items():
                logger.info(f"Created {len(chunks)} {level}-level chunks")
                
        return result
    
    def create_smart_chunks(self, text: str, document_structure: Dict) -> List[str]:
        """
        Create chunks that respect document structure (headings, sections, etc).
        """
        chunks = []
        
        # This would ideally parse the document structure
        # For now, we'll use a simple approach
        sections = text.split('\n\n')  # Split by paragraphs
        
        current_chunk = ""
        for section in sections:
            # If adding this section would exceed chunk size, save current chunk
            if len(current_chunk) + len(section) > strategy["chunk_size"]:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = section
            else:
                current_chunk += "\n\n" + section if current_chunk else section
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    async def process_with_context_windows(
        self, 
        chunks: List[Dict],
        window_before: int = 1,
        window_after: int = 1
    ) -> List[Dict]:
        """
        Add context windows to chunks for better retrieval.
        Each chunk will know about its neighbors.
        """
        enhanced_chunks = []
        
        for i, chunk in enumerate(chunks):
            enhanced_chunk = chunk.copy()
            
            # Add previous context
            prev_context = []
            for j in range(max(0, i - window_before), i):
                prev_context.append(chunks[j]["content"][:500])  # First 500 chars
            enhanced_chunk["metadata"]["previous_context"] = "\n".join(prev_context)
            
            # Add next context  
            next_context = []
            for j in range(i + 1, min(len(chunks), i + window_after + 1)):
                next_context.append(chunks[j]["content"][:500])
            enhanced_chunk["metadata"]["next_context"] = "\n".join(next_context)
            
            # Add position metadata
            enhanced_chunk["metadata"]["position"] = {
                "index": i,
                "total": len(chunks),
                "relative": i / len(chunks)  # 0.0 to 1.0
            }
            
            enhanced_chunks.append(enhanced_chunk)
            
        return enhanced_chunks


from datetime import datetime