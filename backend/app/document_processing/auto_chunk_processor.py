"""
Simplified auto-detect document processor with multi-chunking.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Simple chunk configurations
CHUNK_CONFIGS = {
    "business": {
        "detect_keywords": ["strategy", "plan", "proposal", "report", "analysis", "roadmap"],
        "chunks": [
            {"name": "standard", "size": 2000, "overlap": 400},
            {"name": "large", "size": 2000, "overlap": 400}  # Reduced to fit NIM limits
        ]
    },
    "technical": {
        "detect_keywords": ["api", "technical", "specification", "documentation", "architecture"],
        "chunks": [
            {"name": "standard", "size": 2000, "overlap": 400},
            {"name": "technical", "size": 2000, "overlap": 400}  # Reduced to fit NIM limits
        ]
    },
    "default": {
        "detect_keywords": [],
        "chunks": [
            {"name": "standard", "size": 2000, "overlap": 400}
        ]
    }
}

def detect_document_type(filename: str) -> str:
    """
    Simple auto-detection based on filename.
    Returns: 'business', 'technical', or 'default'
    """
    filename_lower = filename.lower()
    
    # Check business keywords
    if any(keyword in filename_lower for keyword in CHUNK_CONFIGS["business"]["detect_keywords"]):
        logger.info(f"Detected business document: {filename}")
        return "business"
    
    # Check technical keywords
    if any(keyword in filename_lower for keyword in CHUNK_CONFIGS["technical"]["detect_keywords"]):
        logger.info(f"Detected technical document: {filename}")
        return "technical"
    
    logger.info(f"Using default chunking for: {filename}")
    return "default"

def get_chunking_plan(filename: str, override_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the chunking plan for a document.
    
    Args:
        filename: Document filename
        override_type: Optional manual override ('business', 'technical', 'default')
    
    Returns:
        Chunking plan with configurations
    """
    # Use override if provided, otherwise auto-detect
    doc_type = override_type if override_type else detect_document_type(filename)
    
    config = CHUNK_CONFIGS.get(doc_type, CHUNK_CONFIGS["default"])
    
    return {
        "document_type": doc_type,
        "auto_detected": override_type is None,
        "chunk_configs": config["chunks"],
        "total_levels": len(config["chunks"])
    }

def create_multi_chunks(text: str, chunk_configs: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Create multiple chunk sizes from text.
    
    Args:
        text: Full document text
        chunk_configs: List of chunk configurations
        
    Returns:
        Dict with chunk levels as keys
    """
    from app.document_processing.processor import DocumentProcessor
    # Don't need directories for text splitting, but processor requires them
    processor = DocumentProcessor("data/uploads", "data/processed")  # Temporary instance for chunking
    
    chunks_by_level = {}
    
    for config in chunk_configs:
        level_name = config["name"]
        chunks = processor._split_text(
            text=text,
            chunk_size=config["size"],
            chunk_overlap=config["overlap"]
        )
        
        chunks_by_level[level_name] = [
            {
                "content": chunk,
                "chunk_index": i,
                "level": level_name,
                "metadata": {
                    "chunk_size": len(chunk),
                    "config": config
                }
            }
            for i, chunk in enumerate(chunks)
        ]
        
        logger.info(f"Created {len(chunks)} {level_name} chunks")
    
    return chunks_by_level

class AutoChunkProcessor:
    """
    Simplified processor that auto-detects and creates appropriate chunks.
    """
    
    def __init__(self, upload_dir: str, processed_dir: str):
        self.upload_dir = upload_dir
        self.processed_dir = processed_dir
    
    async def process_with_auto_chunking(
        self,
        document_path: str,
        document_id: str,
        filename: str,
        filetype: str,
        override_type: Optional[str] = None,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Process document with automatic multi-chunking.
        
        Args:
            document_path: Path to document
            document_id: Document ID
            filename: Original filename (for detection)
            filetype: File type
            override_type: Optional manual override
            db_session: Database session for storing chunks
            
        Returns:
            Processing results
        """
        # Validate document path
        if not document_path or document_path == "":
            raise ValueError(f"Empty document path provided for document {document_id}")
            
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document file not found at path: {document_path}")
            
        from app.document_processing.processor import DocumentProcessor
        processor = DocumentProcessor(self.upload_dir, self.processed_dir)
        
        # Get chunking plan
        plan = get_chunking_plan(filename, override_type)
        logger.info(f"Chunking plan for {filename}: {plan['document_type']} ({plan['total_levels']} levels)")
        
        # Extract text - try NV-Ingest first, then fallback
        try:
            # Try async NV-Ingest extraction
            text = await processor._extract_text_with_nv_ingest(document_path, filetype)
        except Exception as e:
            logger.warning(f"Async extraction failed, using sync fallback: {str(e)}")
            # Fallback to sync extraction
            text = processor._extract_text(document_path, filetype)
            
        if not text:
            raise ValueError("No text extracted from document")
        
        # Create chunks at different levels
        chunks_by_level = create_multi_chunks(text, plan["chunk_configs"])
        
        # Flatten chunks for storage
        all_chunks = []
        for level_name, level_chunks in chunks_by_level.items():
            for chunk in level_chunks:
                all_chunks.append({
                    "id": f"{document_id}__{level_name}__{chunk['chunk_index']}",
                    "document_id": document_id,
                    "content": chunk["content"],
                    "chunk_index": chunk["chunk_index"],
                    "chunk_level": level_name,
                    "metadata": chunk["metadata"]
                })
        
        # Store in database if session provided
        if db_session:
            from app.db.models.document import DocumentChunk
            from app.rag.vector_store import VectorStore
            from app.services.embedding_service import get_embedding_service
            
            embedding_service = get_embedding_service()
            vector_store = VectorStore(db_session, embedding_service)
            
            for chunk_data in all_chunks:
                # Generate embedding
                embedding = await vector_store.generate_embedding(chunk_data["content"])
                
                # Create chunk record
                chunk = DocumentChunk(
                    id=chunk_data["id"],
                    document_id=document_id,
                    content=chunk_data["content"],
                    chunk_index=chunk_data["chunk_index"],
                    meta_data={
                        "chunk_level": chunk_data["chunk_level"],
                        **chunk_data["metadata"]
                    },
                    embedding=embedding
                )
                db_session.add(chunk)
            
            db_session.commit()
        
        return {
            "success": True,
            "document_id": document_id,
            "chunking_plan": plan,
            "chunks_created": {
                level: len(chunks) for level, chunks in chunks_by_level.items()
            },
            "total_chunks": len(all_chunks)
        }

# Convenience function for backwards compatibility
async def process_document_auto(
    document_path: str,
    document_id: str, 
    filename: str,
    filetype: str,
    db_session = None
) -> Dict[str, Any]:
    """
    Process a document with automatic chunking detection.
    """
    processor = AutoChunkProcessor("data/uploads", "data/processed")
    return await processor.process_with_auto_chunking(
        document_path=document_path,
        document_id=document_id,
        filename=filename,
        filetype=filetype,
        db_session=db_session
    )