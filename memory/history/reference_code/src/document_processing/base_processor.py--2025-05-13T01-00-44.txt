# src/document_processing/base_processor.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BaseDocumentProcessor(ABC):
    """
    Abstract base class for document processors.
    All specific file type processors must inherit from this class.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document processor
        
        Args:
            chunk_size: Target size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @abstractmethod
    def can_process(self, file_path: str, content_type: str) -> bool:
        """
        Check if this processor can handle the given file type
        
        Args:
            file_path: Path to the file
            content_type: MIME type of the file
            
        Returns:
            True if this processor can handle the file, False otherwise
        """
        pass
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extract raw text from the document
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
        """
        pass
    
    def process(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process the document into chunks with metadata
        
        Args:
            file_path: Path to the file
            metadata: Optional metadata to include with each chunk
            
        Returns:
            List of chunks with metadata
        """
        try:
            # Extract text from the document
            logger.info(f"Extracting text from {file_path}")
            text = self.extract_text(file_path)
            
            if not text:
                logger.warning(f"No text extracted from {file_path}")
                return []
            
            # Create chunks with metadata
            logger.info(f"Chunking text from {file_path} (size: {self.chunk_size}, overlap: {self.chunk_overlap})")
            chunks = self.create_chunks(text)
            
            # Add metadata to chunks
            result = []
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    "chunk_index": i,
                    "text": chunk,
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path)
                }
                
                # Add optional metadata if provided
                if metadata:
                    chunk_data["metadata"] = metadata
                
                result.append(chunk_data)
            
            logger.info(f"Created {len(result)} chunks from {file_path}")
            return result
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise
    
    def create_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to split into chunks
            
        Returns:
            List of text chunks
        """
        # Simple chunking - split by newlines first, then by characters
        chunks = []
        paragraphs = text.split('\n')
        
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            # Skip empty paragraphs
            if not paragraph.strip():
                continue
            
            # If adding this paragraph would exceed chunk size, add the current chunk and start a new one
            if current_size + len(paragraph) > self.chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                
                # Keep some overlap from the end of the previous chunk
                overlap_size = 0
                overlap_chunks = []
                
                # Add paragraphs from the end until we reach desired overlap
                for p in reversed(current_chunk):
                    if overlap_size + len(p) > self.chunk_overlap:
                        break
                    overlap_chunks.insert(0, p)
                    overlap_size += len(p)
                
                current_chunk = overlap_chunks
                current_size = overlap_size
            
            # Add the paragraph to the current chunk
            current_chunk.append(paragraph)
            current_size += len(paragraph)
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks