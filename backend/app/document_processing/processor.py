import os
import shutil
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define constants
DEFAULT_CHUNK_SIZE = 3000  # Increased for better context
DEFAULT_CHUNK_OVERLAP = 500  # More overlap for continuity

class DocumentProcessor:
    """Handles document processing, chunking, and embedding generation."""
    
    def __init__(self, upload_dir: str, processed_dir: str, embedding_service=None):
        """Initialize the document processor."""
        self.upload_dir = upload_dir
        self.processed_dir = processed_dir
        self.embedding_service = embedding_service
        
        # Create directories if they don't exist
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)
    
    def save_uploaded_file(self, file_content: bytes, original_filename: str) -> Dict[str, Any]:
        """
        Save an uploaded file to disk and return file information.
        
        Args:
            file_content: The binary content of the file
            original_filename: The original filename
            
        Returns:
            Dict containing file information (id, path, size, type)
        """
        try:
            # Create a unique filename
            file_id = str(uuid.uuid4())
            filename = f"{file_id}_{original_filename}"
            
            # Determine file type
            file_extension = os.path.splitext(original_filename)[1].lstrip(".").lower()
            if not file_extension:
                file_extension = "unknown"
            
            # Save file to disk
            filepath = os.path.join(self.upload_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(file_content)
            
            # Get file size
            filesize = os.path.getsize(filepath)
            
            return {
                "id": file_id,
                "filepath": filepath,
                "filename": original_filename,
                "filetype": file_extension,
                "filesize": filesize
            }
        
        except Exception as e:
            logger.error(f"Error saving uploaded file: {str(e)}")
            raise
    
    def process_document(
        self, 
        document_path: str, 
        document_id: str, 
        filetype: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a document to extract text and generate chunks.
        
        Args:
            document_path: Path to the document file
            document_id: ID of the document
            filetype: Type of the document (pdf, docx, txt, etc.)
            chunk_size: Size of chunks to generate (in characters)
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of chunks with text content and metadata
        """
        # Use default chunk parameters if not provided
        chunk_size = chunk_size or DEFAULT_CHUNK_SIZE
        chunk_overlap = chunk_overlap or DEFAULT_CHUNK_OVERLAP
        
        try:
            # Extract text from document based on filetype
            text = self._extract_text(document_path, filetype)
            
            # Split text into chunks
            chunks = self._split_text(text, chunk_size, chunk_overlap)
            
            # Create chunk objects
            chunk_objects = []
            for i, chunk_text in enumerate(chunks):
                chunk_objects.append({
                    "chunk_index": i,
                    "content": chunk_text,
                    "document_id": document_id,
                    "meta_data": {
                        "chunk_size": len(chunk_text),
                        "processed_at": datetime.now().isoformat()
                    }
                })
            
            # In a real implementation, we would generate embeddings here
            # For now, we'll just return the chunks
            
            return chunk_objects
        
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            raise
    
    def _extract_text(self, file_path: str, filetype: str) -> str:
        """
        Extract text from a document based on its filetype.
        
        Args:
            file_path: Path to the document file
            filetype: Type of the document (pdf, docx, txt, etc.)
            
        Returns:
            Extracted text content
        """
        if filetype == "txt":
            # For text files, simply read the content
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        
        elif filetype == "pdf":
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = []
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text.append(page.extract_text())
                    return '\n'.join(text)
            except Exception as e:
                logger.error(f"Error extracting text from PDF: {str(e)}")
                return f"[Error extracting PDF: {str(e)}]"
        
        elif filetype in ["docx", "doc"]:
            try:
                from docx import Document
                doc = Document(file_path)
                full_text = []
                for para in doc.paragraphs:
                    if para.text.strip():
                        full_text.append(para.text)
                return '\n'.join(full_text)
            except Exception as e:
                logger.error(f"Error extracting text from DOCX: {str(e)}")
                return f"[Error extracting Word document: {str(e)}]"
        
        elif filetype in ["csv", "xlsx", "xls"]:
            try:
                import pandas as pd
                if filetype == "csv":
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                # Convert dataframe to text representation
                return df.to_string()
            except Exception as e:
                logger.error(f"Error extracting text from spreadsheet: {str(e)}")
                return f"[Error extracting spreadsheet: {str(e)}]"
        
        else:
            # For unsupported file types
            return f"[Unsupported file type: {filetype}]"
    
    def _split_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: The text to split
            chunk_size: Size of chunks to generate (in characters)
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        # Simple character-based chunking for now
        chunks = []
        start = 0
        
        while start < len(text):
            # Get the chunk of text
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            
            # Add to chunks list
            chunks.append(chunk)
            
            # Move start position, accounting for overlap
            start = start + chunk_size - chunk_overlap
        
        return chunks
    
    async def generate_embeddings(self, chunks: List[Dict[str, Any]], db_session=None) -> List[Dict[str, Any]]:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of chunk objects with text content
            db_session: Optional SQLAlchemy database session
            
        Returns:
            List of chunk objects with embeddings
        """
        try:
            # Import here to avoid circular imports
            from ..rag.vector_store import get_vector_store
            
            if db_session:
                # Get the vector store with embedding service
                vector_store = get_vector_store(db_session, self.embedding_service)
                
                # Generate embeddings for each chunk
                for chunk in chunks:
                    # Generate embedding
                    text = chunk["content"]
                    embedding = await vector_store.generate_embedding(text)
                    
                    # Store the embedding as a string
                    chunk["embedding"] = json.dumps(embedding)
            else:
                # Fallback to mock embeddings if no DB session provided
                for chunk in chunks:
                    # Create a mock embedding (just a placeholder)
                    chunk["embedding"] = f"mock_embedding_{uuid.uuid4()}"
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # Fallback to mock embeddings
            for chunk in chunks:
                chunk["embedding"] = f"mock_embedding_{uuid.uuid4()}"
            return chunks
    
    def cleanup_processed_file(self, file_path: str) -> bool:
        """
        Move a processed file to the processed directory.
        
        Args:
            file_path: Path to the processed file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get destination path
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.processed_dir, filename)
            
            # Move file
            shutil.move(file_path, dest_path)
            return True
        
        except Exception as e:
            logger.error(f"Error cleaning up processed file {file_path}: {str(e)}")
            return False


# Create a singleton instance for the application
# Will be initialized with embedding service in main.py
document_processor = DocumentProcessor(
    upload_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "uploads"),
    processed_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed")
)