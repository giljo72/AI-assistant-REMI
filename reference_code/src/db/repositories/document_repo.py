from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy import select, update, delete, func, and_, text
from sqlalchemy.exc import SQLAlchemyError
import logging

from ...core.db_interface import get_db_session
# Update this line to include Project
from ..models import Document, DocumentProject, DocumentEmbedding, Project

logger = logging.getLogger(__name__)

class DocumentRepository:
    """Repository for document operations"""
    
    def create_document(self, 
                       filename: str, 
                       content_type: str, 
                       tag: str, 
                       description: str,
                       status: str,
                       file_path: str,
                       file_size: int) -> Optional[Document]:
        """
        Create a new document in the database
        
        Args:
            filename: Original filename
            content_type: MIME type of the file
            tag: Document tag (P, B, or PB)
            description: User-provided description
            status: Initial status (usually 'Uploaded')
            file_path: Path to the file on disk
            file_size: Size of file in bytes
            
        Returns:
            Document object if successful, None otherwise
        """
        try:
            with get_db_session() as session:
                document = Document(
                    filename=filename,
                    content_type=content_type,
                    tag=tag,
                    description=description,
                    status=status,
                    file_path=file_path,
                    file_size=file_size
                )
                
                session.add(document)
                session.flush()  # To get the ID
                
                logger.info(f"Created document: {filename} (ID: {document.id})")
                
                # Make a copy to return, as the session will be closed
                result = {
                    'id': document.id,
                    'filename': document.filename,
                    'content_type': document.content_type,
                    'tag': document.tag,
                    'description': document.description,
                    'status': document.status,
                    'file_path': document.file_path,
                    'file_size': document.file_size,
                    'created_at': document.created_at,
                    'updated_at': document.updated_at
                }
                
                return result
        except SQLAlchemyError as e:
            logger.error(f"Database error creating document: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating document: {e}")
            return None
    
    def update_document(self, 
                       document_id: int,
                       **kwargs) -> Optional[Dict[str, Any]]:
        """
        Update a document in the database
        
        Args:
            document_id: ID of the document to update
            **kwargs: Fields to update (filename, status, etc.)
            
        Returns:
            Updated document as dictionary if successful, None otherwise
        """
        try:
            with get_db_session() as session:
                # Update the document
                stmt = (
                    update(Document)
                    .where(Document.id == document_id)
                    .values(**kwargs)
                    .returning(Document)
                )
                
                result = session.execute(stmt).scalar_one_or_none()
                
                if result:
                    logger.info(f"Updated document ID {document_id}")
                    
                    # Convert to dictionary
                    return {
                        'id': result.id,
                        'filename': result.filename,
                        'content_type': result.content_type,
                        'tag': result.tag,
                        'description': result.description,
                        'status': result.status,
                        'file_path': result.file_path,
                        'file_size': result.file_size,
                        'chunk_count': result.chunk_count,
                        'processing_error': result.processing_error,
                        'created_at': result.created_at,
                        'updated_at': result.updated_at
                    }
                else:
                    logger.warning(f"Document ID {document_id} not found for update")
                    return None
        except SQLAlchemyError as e:
            logger.error(f"Database error updating document: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error updating document: {e}")
            return None
    
    def delete_document(self, document_id: int) -> bool:
        """
        Delete a document and its embeddings
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_session() as session:
                # Delete the document (cascades to embeddings)
                stmt = delete(Document).where(Document.id == document_id)
                result = session.execute(stmt)
                
                if result.rowcount > 0:
                    logger.info(f"Deleted document ID {document_id}")
                    return True
                else:
                    logger.warning(f"Document ID {document_id} not found for deletion")
                    return False
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting document: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting document: {e}")
            return False
    
    def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID
        
        Args:
            document_id: ID of document to retrieve
            
        Returns:
            Document as dictionary if found, None otherwise
        """
        try:
            with get_db_session() as session:
                stmt = select(Document).where(Document.id == document_id)
                result = session.execute(stmt).scalar_one_or_none()
                
                if result:
                    return {
                        'id': result.id,
                        'filename': result.filename,
                        'content_type': result.content_type,
                        'tag': result.tag,
                        'description': result.description,
                        'status': result.status,
                        'file_path': result.file_path,
                        'file_size': result.file_size,
                        'chunk_count': result.chunk_count,
                        'processing_error': result.processing_error,
                        'created_at': result.created_at,
                        'updated_at': result.updated_at
                    }
                else:
                    logger.warning(f"Document ID {document_id} not found")
                    return None
        except SQLAlchemyError as e:
            logger.error(f"Database error getting document: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting document: {e}")
            return None
    
    def get_documents_by_filename(self, filename: str) -> List[Dict[str, Any]]:
        """
        Get documents by filename
        
        Args:
            filename: The filename to search for
            
        Returns:
            List of documents with matching filename
        """
        try:
            with get_db_session() as session:
                stmt = select(Document).where(Document.filename == filename)
                results = session.execute(stmt).scalars().all()
                
                # Convert to dictionaries
                documents = []
                for doc in results:
                    documents.append({
                        'id': doc.id,
                        'filename': doc.filename,
                        'content_type': doc.content_type,
                        'tag': doc.tag,
                        'description': doc.description,
                        'status': doc.status,
                        'file_path': doc.file_path,
                        'file_size': doc.file_size,
                        'chunk_count': doc.chunk_count,
                        'processing_error': doc.processing_error,
                        'created_at': doc.created_at,
                        'updated_at': doc.updated_at
                    })
                
                return documents
        except Exception as e:
            logger.error(f"Error getting documents by filename: {e}")
            return []
    
    def get_documents(
        self,
        tag: Optional[str] = None,
        status: Optional[str] = None,
        project_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Get documents with optional filtering, pagination, and sorting
        """
        try:
            with get_db_session() as session:
                query = select(Document)

                filters = []
                if tag:
                    filters.append(Document.tag == tag)
                if status:
                    filters.append(Document.status == status)
                if project_id:
                    query = query.join(DocumentProject, Document.id == DocumentProject.document_id)
                    filters.append(DocumentProject.project_id == project_id)
                if filters:
                    query = query.filter(and_(*filters))

                # Validate sort field and order
                sort_field = getattr(Document, sort_by, Document.created_at)
                sort_expr = sort_field.desc() if sort_order.lower() == "desc" else sort_field.asc()

                offset = (page - 1) * page_size
                query = query.order_by(sort_expr).offset(offset).limit(page_size)

                results = session.execute(query).scalars().all()

                documents = []
                for doc in results:
                    documents.append({
                        'id': doc.id,
                        'filename': doc.filename,
                        'content_type': doc.content_type,
                        'tag': doc.tag,
                        'description': doc.description,
                        'status': doc.status,
                        'file_path': doc.file_path,
                        'file_size': doc.file_size,
                        'chunk_count': doc.chunk_count,
                        'processing_error': doc.processing_error,
                        'created_at': doc.created_at,
                        'updated_at': doc.updated_at
                    })

                return documents
        except SQLAlchemyError as e:
            logger.error(f"Database error getting documents: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting documents: {e}")
            return []

    
    def search_documents(self, 
                    query: str,
                    tag: Optional[str] = None,
                    status: Optional[str] = None,
                    project_id: Optional[int] = None,
                    page: int = 1,
                    page_size: int = 50) -> List[Dict[str, Any]]:
        """
        Search documents using full-text search
        
        Args:
            query: Search query string
            tag: Filter by tag (P, B, or PB)
            status: Filter by status (Active, Detached, Failed)
            project_id: Filter by project ID
            page: Page number (starting from 1)
            page_size: Number of items per page
            
        Returns:
            List of documents as dictionaries, ranked by relevance
        """
        try:
            with get_db_session() as session:
                # Create the search query text
                search_query_text = query  # PostgreSQL will handle stemming, etc.
                
                # Base query with relevance ranking
                base_query = """
                SELECT 
                    d.*,
                    ts_rank(d.search_vector, to_tsquery('english', %s)) as relevance
                FROM 
                    documents d
                WHERE 
                    d.search_vector @@ to_tsquery('english', %s)
                """
                
                # Apply additional filters
                params = [search_query_text, search_query_text]
                
                if tag:
                    base_query += " AND d.tag = %s"
                    params.append(tag)
                
                if status:
                    base_query += " AND d.status = %s"
                    params.append(status)
                
                if project_id:
                    # Join with DocumentProject to filter by project
                    base_query = base_query.replace(
                        "FROM documents d",
                        """FROM documents d
                        JOIN document_projects dp ON d.id = dp.document_id"""
                    )
                    base_query += " AND dp.project_id = %s"
                    params.append(project_id)
                
                # Add ordering and pagination
                base_query += " ORDER BY relevance DESC, d.created_at DESC"
                
                # Handle pagination
                offset = (page - 1) * page_size
                base_query += " LIMIT %s OFFSET %s"
                params.extend([page_size, offset])
            
            # Execute query  
            result = session.execute(text(base_query), params)
            rows = result.fetchall()
            
            # Convert to dictionaries
            documents = []
            for row in rows:
                doc_dict = {
                    'id': row.id,
                    'filename': row.filename,
                    'content_type': row.content_type,
                    'tag': row.tag,
                    'description': row.description,
                    'status': row.status,
                    'file_path': row.file_path,
                    'file_size': row.file_size,
                    'chunk_count': row.chunk_count,
                    'processing_error': row.processing_error,
                    'created_at': row.created_at,
                    'updated_at': row.updated_at,
                    'relevance': float(row.relevance)  # Add relevance score
                }
                documents.append(doc_dict)
            
            return documents
        except SQLAlchemyError as e:
            logger.error(f"Database error searching documents: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching documents: {e}")
            return []
            
    def count_documents(self, 
                       tag: Optional[str] = None, 
                       status: Optional[str] = None,
                       project_id: Optional[int] = None) -> int:
        """
        Count documents with optional filtering
        
        Args:
            tag: Filter by tag (P, B, or PB)
            status: Filter by status (Active, Detached, Failed)
            project_id: Filter by project ID
            
        Returns:
            Count of matching documents
        """
        try:
            with get_db_session() as session:
                # Start with base query
                query = select(func.count(Document.id))
                
                # Apply filters
                filters = []
                
                if tag:
                    filters.append(Document.tag == tag)
                    
                if status:
                    filters.append(Document.status == status)
                    
                if project_id:
                    # Join with association table to filter by project
                    query = query.join(
                        DocumentProject, 
                        Document.id == DocumentProject.document_id
                    ).filter(DocumentProject.project_id == project_id)
                
                if filters:
                    query = query.filter(and_(*filters))
                
                # Execute query
                count = session.execute(query).scalar_one()
                
                return count
        except SQLAlchemyError as e:
            logger.error(f"Database error counting documents: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error counting documents: {e}")
            return 0
    
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
            with get_db_session() as session:
                # Check if association already exists
                check_stmt = select(DocumentProject).where(
                    and_(
                        DocumentProject.document_id == document_id,
                        DocumentProject.project_id == project_id
                    )
                )
                
                existing = session.execute(check_stmt).scalar_one_or_none()
                
                if existing:
                    logger.info(f"Document {document_id} already attached to project {project_id}")
                    return True
                
                # Create new association
                association = DocumentProject(
                    document_id=document_id,
                    project_id=project_id
                )
                
                session.add(association)
                
                logger.info(f"Attached document {document_id} to project {project_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Database error attaching document to project: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error attaching document to project: {e}")
            return False
            
    def detach_from_project(self, document_id: int, project_id: int) -> bool:
        """
        Detach a document from a project
        
        Args:
            document_id: ID of document to detach
            project_id: ID of project to detach from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_session() as session:
                # Delete the association
                stmt = delete(DocumentProject).where(
                    and_(
                        DocumentProject.document_id == document_id,
                        DocumentProject.project_id == project_id
                    )
                )
                
                result = session.execute(stmt)
                
                if result.rowcount > 0:
                    logger.info(f"Detached document {document_id} from project {project_id}")
                    return True
                else:
                    logger.warning(f"Document {document_id} not found in project {project_id}")
                    return True  # Return True anyway as the end state is achieved
        except SQLAlchemyError as e:
            logger.error(f"Database error detaching document from project: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error detaching document from project: {e}")
            return False
    
    def get_projects_for_document(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Get all projects associated with a given document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            List of projects as dictionaries
        """
        try:
            with get_db_session() as session:
                stmt = (
                    select(Project)
                    .join(DocumentProject, Project.id == DocumentProject.project_id)
                    .where(DocumentProject.document_id == document_id)
                )
                results = session.execute(stmt).scalars().all()
                
                projects = []
                for proj in results:
                    projects.append({
                        'id': proj.id,
                        'name': proj.name,
                        'custom_prompt': proj.custom_prompt,
                        'created_at': proj.created_at,
                        'updated_at': proj.updated_at
                    })
                
                return projects
        except Exception as e:
            logger.error(f"Error retrieving projects for document {document_id}: {e}")
            return []
        
        # Add this method to src/db/repositories/document_repo.py
    def get_project_id_by_name(self, project_name: str) -> Optional[int]:
        """
        Get a project ID by its name
        
        Args:
            project_name: The name of the project
            
        Returns:
            Project ID if found, None otherwise
        """
        try:
            with get_db_session() as session:
                stmt = select(Project).where(Project.name == project_name)
                result = session.execute(stmt).scalar_one_or_none()
                
                if result:
                    return result.id
                else:
                    return None
        except Exception as e:
            logger.error(f"Error getting project ID by name: {e}")
            return None
