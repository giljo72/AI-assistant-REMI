# src/document_processing/docx_processor.py
import os
from typing import List, Dict, Any
import logging
import docx2txt

from .base_processor import BaseDocumentProcessor

logger = logging.getLogger(__name__)

class DocxProcessor(BaseDocumentProcessor):
    """Processor for Microsoft Word (.docx) files"""
    
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
        
        # Check content type
        valid_types = [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword'
        ]
        
        return ext == '.docx' or any(t in content_type for t in valid_types)
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a DOCX file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
        """
        try:
            # Extract text and images (text only will be returned)
            text = docx2txt.process(file_path)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            raise