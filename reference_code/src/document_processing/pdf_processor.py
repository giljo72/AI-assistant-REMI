# src/document_processing/pdf_processor.py
import os
from typing import List, Dict, Any
import logging
import pypdf

from .base_processor import BaseDocumentProcessor

logger = logging.getLogger(__name__)

class PDFProcessor(BaseDocumentProcessor):
    """Processor for PDF files"""
    
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
        return ext == '.pdf' or 'application/pdf' in content_type
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a PDF file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
        """
        try:
            text = ""
            
            with open(file_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)
                
                # Get total number of pages
                num_pages = len(pdf.pages)
                logger.info(f"PDF has {num_pages} pages")
                
                # Extract text from each page
                for i in range(num_pages):
                    page = pdf.pages[i]
                    page_text = page.extract_text()
                    
                    if page_text:
                        text += page_text + "\n\n"
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise