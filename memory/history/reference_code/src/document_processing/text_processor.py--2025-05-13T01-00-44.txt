# src/document_processing/text_processor.py
import os
from typing import List, Dict, Any
import logging

from .base_processor import BaseDocumentProcessor

logger = logging.getLogger(__name__)

class TextProcessor(BaseDocumentProcessor):
    """Processor for plain text files (.txt, .md, etc.)"""
    
    def can_process(self, file_path: str, content_type: str) -> bool:
        """
        Check if this processor can handle the given file type
        
        Args:
            file_path: Path to the file
            content_type: MIME type of the file
            
        Returns:
            True if this processor can handle the file, False otherwise
        """
        # Check file extension
        ext = os.path.splitext(file_path)[1].lower()
        valid_extensions = ['.txt', '.md', '.markdown', '.log', '.json', '.xml', '.csv', '.tsv']
        
        # Check content type
        valid_types = [
            'text/plain', 
            'text/markdown', 
            'text/csv', 
            'text/tab-separated-values',
            'application/json',
            'application/xml'
        ]
        
        return ext in valid_extensions or any(t in content_type for t in valid_types)
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a text file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
        """
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return text
        except UnicodeDecodeError:
            # If UTF-8 fails, try with Latin-1 (which should never fail)
            logger.warning(f"UTF-8 decoding failed for {file_path}, falling back to Latin-1")
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise