from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Document schemas
class DocumentBase(BaseModel):
    """Base document schema with common attributes."""
    filename: str  # Changed from name to filename to match Document model
    description: Optional[str] = None
    project_id: Optional[str] = None  # null for unattached documents


class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""
    # Frontend sends these fields during creation
    type: str  # file extension: PDF, DOCX, etc.
    size: int  # in bytes


class DocumentUpdate(BaseModel):
    """Schema for updating an existing document."""
    filename: Optional[str] = None  # Changed from name to filename to match Document model
    description: Optional[str] = None
    active: Optional[bool] = None
    project_id: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentInDB(DocumentBase):
    """Schema for document as stored in the database."""
    id: str
    filename: str  # Original filename
    filepath: str  # Stored path
    filetype: str  # File extension
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_processed: bool = False
    meta_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True  # Use this instead of orm_mode in Pydantic v2


class Document(BaseModel):
    """Schema for document responses to match frontend expectations."""
    id: str
    filename: str  # Original filename for database
    name: str  # Frontend expects this field 
    description: Optional[str] = None
    filepath: str  # Stored path
    filetype: str  # File extension for database
    type: str  # Frontend expects this field
    size: int  # File size in bytes
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed: bool  # Mapped from is_processed
    active: bool = False  # Whether document is active in context
    processing_failed: Optional[bool] = None
    chunk_count: Optional[int] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None  # Added project name for UI display
    tags: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class FileSearchRequest(BaseModel):
    """Schema for file search requests."""
    query: str
    project_id: Optional[str] = None
    file_types: Optional[List[str]] = None
    date_range: Optional[Dict[str, str]] = None
    limit: Optional[int] = 10
    include_content: Optional[bool] = False


class FileSearchResult(Document):
    """Schema for search results."""
    relevance: float  # 0-100 relevance score
    content_snippets: Optional[List[str]] = None  # Relevant text snippets


class ProcessingStats(BaseModel):
    """Schema for document processing statistics."""
    total_files: int
    processed_files: int
    failed_files: int
    processing_files: int
    total_chunks: int
    gpu_usage: Optional[float] = None
    eta: Optional[float] = None


class FileBulkOperationRequest(BaseModel):
    """Schema for bulk operations on files."""
    file_ids: List[str]
    project_id: Optional[str] = None


class FileBulkOperationResult(BaseModel):
    """Schema for results of bulk operations."""
    success: List[str]
    failed: List[Dict[str, str]]
    project_id: Optional[str] = None
    project_name: Optional[str] = None


class FileProcessRequest(BaseModel):
    """Schema for file processing requests."""
    file_id: str
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None