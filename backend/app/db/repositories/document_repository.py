from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from .base_repository import BaseRepository
from ..models.document import Document, ProjectDocument, DocumentChunk
from ...schemas.document import DocumentCreate, DocumentUpdate


class DocumentRepository(BaseRepository[Document, DocumentCreate, DocumentUpdate]):
    """Repository for Document model operations."""

    def get_by_project(
        self, db: Session, *, project_id: str, skip: int = 0, limit: int = 100, active_only: bool = False
    ) -> List[Document]:
        """Get documents for a specific project."""
        query = (
            db.query(Document)
            .join(ProjectDocument)
            .filter(ProjectDocument.project_id == project_id)
        )
        
        if active_only:
            query = query.filter(ProjectDocument.priority > 0)
            
        return query.offset(skip).limit(limit).all()

    def get_multi_with_filters(
        self,
        db: Session,
        *,
        project_id: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        processed_only: bool = False,
        active_only: bool = False,
        date_range: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        processing_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Document]:
        """Get documents with various filters."""
        query = db.query(Document)
        
        # Filter by project ID only if we're specifically looking for 
        # documents in a project or unattached documents
        if project_id is not None:
            if project_id == "null":  # Special case for unattached documents
                # Find documents that are not in any project
                subquery = db.query(ProjectDocument.document_id)
                query = query.filter(~Document.id.in_(subquery))
            else:
                # Only filter by project_id if we're specifically looking in a project
                query = query.join(ProjectDocument).filter(ProjectDocument.project_id == project_id)
                
                if active_only:
                    query = query.filter(ProjectDocument.priority > 0)
        
        # Filter by file types
        if file_types:
            query = query.filter(Document.filetype.in_(file_types))
        
        # Filter by processing status
        if processed_only:
            query = query.filter(Document.is_processed == True)
            
        if processing_status:
            if processing_status == "processed":
                query = query.filter(Document.is_processed == True)
            elif processing_status == "unprocessed":
                query = query.filter(Document.is_processed == False)
            elif processing_status == "failed":
                # We would need to add a processing_failed field to the Document model
                # For now, this is a placeholder for future implementation
                pass
        
        # Filter by date range
        if date_range:
            if date_range.get("start"):
                query = query.filter(Document.created_at >= date_range["start"])
            if date_range.get("end"):
                query = query.filter(Document.created_at <= date_range["end"])
        
        # Filter by tags
        # We would need to add a tags field to the Document model or create a separate Tags table
        # For now, this is a placeholder for future implementation
        if tags:
            # This would filter by meta_data -> tags if stored in jsonb
            pass
            
        return query.offset(skip).limit(limit).all()

    def search_documents(
        self, 
        db: Session, 
        *, 
        query_text: str,
        project_id: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Document]:
        """Search for documents based on content using document chunks."""
        search = f"%{query_text}%"
        
        # Start building the query
        query = (
            db.query(Document, func.count(DocumentChunk.id).label("relevance"))
            .join(DocumentChunk)
            .filter(DocumentChunk.content.ilike(search))
            .group_by(Document.id)
        )
        
        # Apply filters
        if project_id:
            query = query.join(ProjectDocument).filter(ProjectDocument.project_id == project_id)
            
        if file_types:
            query = query.filter(Document.filetype.in_(file_types))
            
        # Order by relevance and limit results
        results = query.order_by(func.count(DocumentChunk.id).desc()).limit(limit).all()
        
        # Extract just the Document objects
        return [doc for doc, _ in results]
    
    def get_document_with_chunks(self, db: Session, *, document_id: str) -> Optional[Document]:
        """Get a document with all its chunks for preview."""
        return (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )
    
    def get_document_stats(self, db: Session) -> Dict[str, int]:
        """Get document processing statistics."""
        total_files = db.query(func.count(Document.id)).scalar() or 0
        processed_files = db.query(func.count(Document.id)).filter(Document.is_processed == True).scalar() or 0
        
        # This would need a processing_failed field in the Document model
        failed_files = 0
        
        processing_files = total_files - processed_files - failed_files
        
        # Count the total chunks
        total_chunks = db.query(func.count(DocumentChunk.id)).scalar() or 0
        
        return {
            "total_files": total_files,
            "processed_files": processed_files,
            "failed_files": failed_files,
            "processing_files": processing_files,
            "total_chunks": total_chunks,
        }
    
    def link_document_to_project(
        self, db: Session, *, document_id: str, project_id: str, priority: float = 1.0
    ) -> ProjectDocument:
        """Link a document to a project."""
        # Check if the link already exists
        existing_link = (
            db.query(ProjectDocument)
            .filter(
                ProjectDocument.document_id == document_id,
                ProjectDocument.project_id == project_id
            )
            .first()
        )
        
        if existing_link:
            return existing_link
        
        # Create a new link
        link = ProjectDocument(
            document_id=document_id,
            project_id=project_id,
            priority=priority
        )
        
        db.add(link)
        db.commit()
        db.refresh(link)
        return link
    
    def unlink_document_from_project(
        self, db: Session, *, document_id: str, project_id: str
    ) -> bool:
        """Unlink a document from a project."""
        link = (
            db.query(ProjectDocument)
            .filter(
                ProjectDocument.document_id == document_id,
                ProjectDocument.project_id == project_id
            )
            .first()
        )
        
        if link:
            db.delete(link)
            db.commit()
            return True
        
        return False


# Create a singleton instance
document_repository = DocumentRepository(Document)