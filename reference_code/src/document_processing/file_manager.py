# src/document_processing/file_manager.py
import os
import shutil
from typing import List, Dict, Any, Optional, Tuple
import uuid
import logging
from datetime import datetime
from pathlib import Path
import mimetypes

from ..core.config import get_settings
from ..core.logger import Logger
from ..db.repositories.document_repo import DocumentRepository
from .text_processor import TextProcessor
from .pdf_processor import PDFProcessor
from .docx_processor import DocxProcessor
from .spreadsheet_processor import SpreadsheetProcessor

# Make sure mimetype database is initialized
mimetypes.init()

logger = logging.getLogger(__name__)

class FileManager:
    """Manages file uploads, processing, and storage"""
    
    def __init__(self, document_repo: DocumentRepository, custom_logger: Logger):
        """
        Initialize file manager
        
        Args:
            document_repo: Repository for document operations
            custom_logger: Custom logger for file processing logs
        """
        self.settings = get_settings()
        self.upload_path = Path(self.settings['upload_path'])
        self.processed_path = Path(self.settings['processed_path'])
        self.document_repo = document_repo
        self.logger = custom_logger
        
        # Create directories if they don't exist
        self.upload_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize document processors
        self.processors = [
            TextProcessor(),
            PDFProcessor(),
            DocxProcessor(),
            SpreadsheetProcessor()
        ]
    
    def check_if_filename_exists(self, filename: str) -> bool:
        """
        Check if a filename already exists in the database
        
        Args:
            filename: The filename to check
            
        Returns:
            True if the filename exists, False otherwise
        """
        try:
            # Query the database for documents with this filename
            documents = self.document_repo.get_documents_by_filename(filename)
            return len(documents) > 0
        except Exception as e:
            logger.error(f"Error checking if filename exists: {e}")
            return False
    
    def save_uploaded_file(self, file, tag: str, description: str) -> Dict[str, Any]:
        """
        Save an uploaded file and register it in the database
        
        Args:
            file: File object (from Streamlit or similar)
            tag: Document tag (P, B, or PB)
            description: User-provided description
            
        Returns:
            Document metadata if successful
        """
        # Get the original filename
        original_filename = file.name
        
        # Check if this filename already exists
        if self.check_if_filename_exists(original_filename):
            # Generate a new filename with date suffix
            date_suffix = datetime.now().strftime("%d%m%y")
            name_parts = os.path.splitext(original_filename)
            modified_filename = f"{name_parts[0]}_Duplicate_{date_suffix}{name_parts[1]}"
        else:
            modified_filename = original_filename
        
        # Generate a unique storage filename
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Determine content type
        content_type = file.type
        if not content_type:
            content_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'
        
        # Save to upload directory
        upload_path = self.upload_path / unique_filename
        
        with open(upload_path, "wb") as f:
            f.write(file.read())
        
        # Get file size
        file_size = os.path.getsize(upload_path)
        
        # Register in database with potentially modified filename
        document = self.document_repo.create_document(
            filename=modified_filename,
            content_type=content_type,
            tag=tag,
            description=description,
            status="Uploaded",  # Initial status
            file_path=str(upload_path),
            file_size=file_size
        )
        
        # Log the upload
        self.logger.log_file_process(
            filename=modified_filename,
            tag=tag,
            description=description,
            success=True
        )
        
        return document
    
    def delete_document(self, document_id: int) -> bool:
        """
        Delete a document and its associated file
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the document to retrieve file path
            document = self.document_repo.get_document(document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                return False
            
            # Delete the physical file if it exists
            file_path = Path(document['file_path'])
            if file_path.exists():
                try:
                    file_path.unlink()  # Delete the file
                    logger.info(f"Deleted file: {file_path}")
                except Exception as e:
                    logger.error(f"Error deleting file {file_path}: {e}")
                    # Continue with database deletion even if file delete fails
            
            # Delete from database (this will cascade to embeddings due to foreign key constraints)
            success = self.document_repo.delete_document(document_id)
            
            if success:
                # Log the deletion
                self.logger.log_file_process(
                    filename=document['filename'],
                    tag=document['tag'],
                    description="Document deleted by user",
                    success=True
                )
                logger.info(f"Document {document_id} deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete document {document_id} from database")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def process_file(self, document_id: int) -> bool:
        """
        Process a file and move it to the processed directory
        
        Args:
            document_id: ID of document to process
            
        Returns:
            True if successful, False otherwise
        """
        document = self.document_repo.get_document(document_id)
        if not document:
            logger.error(f"Document not found: {document_id}")
            return False
        
        try:
            # Find appropriate processor
            file_path = document['file_path']
            content_type = document['content_type']
            
            processor = None
            for p in self.processors:
                if p.can_process(file_path, content_type):
                    processor = p
                    break
            
            if not processor:
                error_msg = f"No processor found for file type: {content_type}"
                logger.error(error_msg)
                
                # Update document with error
                self.document_repo.update_document(
                    document_id=document_id,
                    status="Failed",
                    processing_error=error_msg
                )
                
                # Log failure
                self.logger.log_file_process(
                    filename=document['filename'],
                    tag=document['tag'],
                    description=document['description'],
                    success=False,
                    error_details=error_msg
                )
                
                return False
            
            # Generate processed path
            current_path = Path(document['file_path'])
            processed_filename = current_path.name
            processed_path = self.processed_path / processed_filename
            
            # Move the file
            shutil.move(current_path, processed_path)
            
            # Update the document
            self.document_repo.update_document(
                document_id=document_id,
                file_path=str(processed_path),
                status="Active"
            )
            
            # Log success
            self.logger.log_file_process(
                filename=document['filename'],
                tag=document['tag'],
                description=document['description'],
                success=True
            )
            
            return True
        except Exception as e:
            # Log failure
            self.logger.log_file_process(
                filename=document['filename'],
                tag=document['tag'],
                description=document['description'],
                success=False,
                error_details=str(e)
            )
            
            # Update document status
            self.document_repo.update_document(
                document_id=document_id,
                status="Failed",
                processing_error=str(e)
            )
            
            logger.error(f"Error processing document {document_id}: {e}")
            return False
    
    def get_text_from_document(self, document_id: int) -> Optional[str]:
        """
        Extract text from a document
        
        Args:
            document_id: ID of document to extract text from
            
        Returns:
            Extracted text if successful, None otherwise
        """
        document = self.document_repo.get_document(document_id)
        if not document:
            logger.error(f"Document not found: {document_id}")
            return None
        
        # Find appropriate processor
        file_path = document['file_path']
        content_type = document['content_type']
        
        for processor in self.processors:
            if processor.can_process(file_path, content_type):
                try:
                    return processor.extract_text(file_path)
                except Exception as e:
                    logger.error(f"Error extracting text from document {document_id}: {e}")
                    return None
        
        logger.error(f"No processor found for document {document_id}")
        return None
    
    def get_chunks_from_document(self, 
                                document_id: int, 
                                chunk_size: Optional[int] = None,
                                chunk_overlap: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Extract and chunk text from a document
        
        Args:
            document_id: ID of document to process
            chunk_size: Optional custom chunk size
            chunk_overlap: Optional custom chunk overlap
            
        Returns:
            List of text chunks with metadata if successful, empty list otherwise
        """
        document = self.document_repo.get_document(document_id)
        if not document:
            logger.error(f"Document not found: {document_id}")
            return []
        
        # Find appropriate processor
        file_path = document['file_path']
        content_type = document['content_type']
        
        for processor in self.processors:
            if processor.can_process(file_path, content_type):
                # Set custom chunk parameters if provided
                if chunk_size is not None:
                    processor.chunk_size = chunk_size
                if chunk_overlap is not None:
                    processor.chunk_overlap = chunk_overlap
                
                try:
                    # Create metadata for chunks
                    metadata = {
                        "document_id": document_id,
                        "filename": document['filename'],
                        "content_type": content_type,
                        "tag": document['tag']
                    }
                    
                    # Process the document into chunks
                    chunks = processor.process(file_path, metadata)
                    return chunks
                except Exception as e:
                    logger.error(f"Error processing document {document_id} into chunks: {e}")
                    return []
        
        logger.error(f"No processor found for document {document_id}")
        return []
    
    def attach_to_project(self, document_id: int, project_id: int) -> bool:
        """
        Attach a document to a project
        
        Args:
            document_id: ID of document to attach
            project_id: ID of project to attach to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.document_repo.attach_to_project(document_id, project_id)
            return True
        except Exception as e:
            logger.error(f"Error attaching document to project: {e}")
            return False
    
    def is_document_in_project(self, document_id: int, project_id: int) -> bool:
        """
        Check if a document is associated with a project
        
        Args:
            document_id: ID of the document to check
            project_id: ID of the project to check
            
        Returns:
            True if the document is in the project, False otherwise
        """
        try:
            # Get project documents
            project_docs, _ = self.get_all_documents(project_id=project_id)
            
            # Check if document is in the list of project documents
            return any(doc['id'] == document_id for doc in project_docs)
        except Exception as e:
            logger.error(f"Error checking if document {document_id} is in project {project_id}: {e}")
            return False
    
    def remove_document_from_project(self, document_id: int, project_id: int) -> bool:
        """
        Remove a document from a project
        
        Args:
            document_id: ID of document to remove
            project_id: ID of project to remove from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if document is in the project first
            if not self.is_document_in_project(document_id, project_id):
                logger.info(f"Document {document_id} is not in project {project_id}, nothing to remove")
                return True
            
            # Remove the document from project
            self.document_repo.detach_from_project(document_id, project_id)
            
            # Log the removal
            self.logger.log_file_process(
                filename=f"Document ID {document_id}",
                tag="System",
                description=f"Removed from project ID {project_id}",
                success=True
            )
            
            logger.info(f"Document {document_id} removed from project {project_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing document {document_id} from project {project_id}: {e}")
            return False
    
    def get_all_documents(
        self,
        tag: Optional[str] = None,
        status: Optional[str] = None,
        project_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get all documents with optional filters, pagination, and sorting.
        Returns a tuple of (documents list, total count).
        """
        try:
            documents = self.document_repo.get_documents(
                tag=tag,
                status=status,
                project_id=project_id,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order
            )
            total_count = self.document_repo.count_documents(tag=tag, status=status, project_id=project_id)

            # Enrich each document with project names
            for doc in documents:
                try:
                    projects = self.document_repo.get_projects_for_document(doc['id'])
                    doc['project_names'] = [p['name'] for p in projects] if projects else []
                except Exception as e:
                    logger.error(f"Failed to load project names for document {doc['id']}: {e}")
                    doc['project_names'] = []

            return documents, total_count

        except Exception as e:
            logger.error(f"Error getting all documents: {e}", exc_info=True)
            return [], 0 
        
    def delete_document_keep_embeddings(self, document_id: int) -> bool:
        """
        Delete a document but keep its embeddings for future use
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the document to retrieve file path
            document = self.document_repo.get_document(document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                return False
            
            # Delete the physical file if it exists
            file_path = Path(document['file_path'])
            if file_path.exists():
                try:
                    file_path.unlink()  # Delete the file
                    logger.info(f"Deleted file: {file_path}")
                except Exception as e:
                    logger.error(f"Error deleting file {file_path}: {e}")
                    # Continue with database update even if file delete fails
            
            # Update document status to "Detached" instead of deleting
            updated = self.document_repo.update_document(
                document_id=document_id,
                status="Detached",
                processing_error="File deleted but embeddings preserved for reference"
            )
            
            if updated:
                # Log the operation
                self.logger.log_file_process(
                    filename=document['filename'],
                    tag=document['tag'],
                    description="Document detached - embeddings preserved",
                    success=True
                )
                logger.info(f"Document {document_id} detached successfully, embeddings preserved")
                return True
            else:
                logger.error(f"Failed to update document {document_id} status in database")
                return False
                    
        except Exception as e:
            logger.error(f"Error detaching document {document_id}: {e}")
            return False
