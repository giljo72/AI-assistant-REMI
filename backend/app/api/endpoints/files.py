import os
import shutil
import logging
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
import uuid

from ...db.database import get_db
from ...db.repositories.document_repository import document_repository
from ...db.repositories.project_repository import project_repository
from ...schemas.document import (
    Document, DocumentCreate, DocumentUpdate, ProcessingStats,
    FileSearchRequest, FileSearchResult, FileBulkOperationRequest,
    FileBulkOperationResult, FileProcessRequest
)

router = APIRouter()

logger = logging.getLogger(__name__)

# Define upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Define function for background processing of documents
async def process_document_background(db: Session, document_id: str, filepath: Optional[str] = None, filename: Optional[str] = None, filetype: Optional[str] = None, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None, use_auto_chunking: bool = True):
    """Background task to process a document and generate embeddings."""
    # Import here to avoid circular imports
    from ...document_processing.processor import document_processor
    from ...document_processing.status_tracker import status_tracker
    from ...db.models.document import DocumentChunk
    from ...services.embedding_service import get_embedding_service
    import time
    import random
    
    document = document_repository.get(db, id=document_id)
    if not document:
        return
    
    # Use passed parameters if document fields are missing (session issues)
    doc_filepath = filepath or document.filepath
    doc_filename = filename or document.filename
    doc_filetype = filetype or document.filetype
    
    # Validate we have required fields
    if not doc_filepath:
        logger.error(f"No filepath available for document {document_id}")
        status_tracker.finish_processing(document_id, success=False)
        document.is_processing_failed = True
        db.commit()
        return
    
    # Track processing status
    status_tracker.start_processing(document_id)
        
    try:
        # Update progress
        status_tracker.update_progress(document_id, 10)
        
        # Use auto-chunking for better context preservation
        if use_auto_chunking:
            from ...document_processing.auto_chunk_processor import process_document_auto
            
            result = await process_document_auto(
                document_path=doc_filepath,
                document_id=document.id,
                filename=doc_filename,
                filetype=doc_filetype,
                db_session=db
            )
            
            # Update document metadata with chunking info
            document.meta_data = document.meta_data or {}
            document.meta_data["chunking_plan"] = result["chunking_plan"]
            document.meta_data["chunks_by_level"] = result["chunks_created"]
            
            # Skip the old processing since auto_chunk handles everything
            status_tracker.update_progress(document_id, 90)
            
            # Mark as processed
            document.is_processed = True
            document.is_processing_failed = False
            document.chunk_count = result["total_chunks"]
            db.commit()
            
            status_tracker.finish_processing(document_id, success=True)
            return
            
        # Fall back to old processing if auto-chunking disabled
        chunks = document_processor.process_document(
            document_path=document.filepath,
            document_id=document.id,
            filetype=document.filetype,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Update progress
        status_tracker.update_progress(document_id, 50)
        
        # Simulate GPU activity
        status_tracker.set_gpu_usage(random.uniform(30, 80))
        
        # Set up embedding service for document processor
        embedding_service = get_embedding_service()
        document_processor.embedding_service = embedding_service
        
        # Generate embeddings for the chunks using pgvector
        chunks_with_embeddings = await document_processor.generate_embeddings(chunks, db_session=db)
        
        # Update progress
        status_tracker.update_progress(document_id, 80)
        
        # Store chunks in the database
        for chunk_data in chunks_with_embeddings:
            # Parse the embedding if it's a JSON string
            embedding_data = chunk_data.get("embedding")
            if embedding_data and isinstance(embedding_data, str):
                import json
                try:
                    # Parse JSON string to list
                    embedding_list = json.loads(embedding_data)
                    # pgvector expects a list of floats directly
                    embedding_data = embedding_list
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"Failed to parse embedding for chunk {chunk_data['chunk_index']}")
                    embedding_data = None
            
            chunk = DocumentChunk(
                document_id=document.id,
                content=chunk_data["content"],
                chunk_index=chunk_data["chunk_index"],
                meta_data=chunk_data["meta_data"],
                embedding=embedding_data  # Now properly formatted for pgvector
            )
            db.add(chunk)
        
        # Update document with processing status
        document.is_processed = True
        document.chunk_count = len(chunks)
        
        # Commit changes
        db.commit()
        db.refresh(document)
        
        # Update progress
        status_tracker.update_progress(document_id, 95)
        
        # Move the file to the processed directory
        document_processor.cleanup_processed_file(document.filepath)
        
        # Mark processing as complete in the tracker
        status_tracker.finish_processing(document_id, True, chunk_count=len(chunks))
        
        # Reduce GPU usage
        status_tracker.set_gpu_usage(random.uniform(5, 20))
        
    except Exception as e:
        # If processing fails, update document status
        document.is_processing_failed = True
        db.commit()
        
        # Mark processing as failed in the tracker
        status_tracker.finish_processing(document_id, False)
        
        # Log the error
        print(f"Error processing document {document_id}: {str(e)}")


@router.get("/", response_model=List[Document])
def get_files(
    db: Session = Depends(get_db),
    project_id: Optional[str] = None,
    file_type: Optional[List[str]] = Query(None),
    processed: Optional[bool] = None,
    active: Optional[bool] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    tag: Optional[List[str]] = Query(None),
    processing_status: Optional[str] = None,
    sort_field: Optional[str] = "created_at",
    sort_direction: Optional[str] = "desc",
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> Any:
    """
    Retrieve files with optional filtering and sorting.
    """
    # Build filter options
    filters = {}
    
    if project_id is not None:
        filters["project_id"] = project_id
        
    if file_type:
        filters["file_types"] = file_type
        
    if processed is not None:
        filters["processed_only"] = processed
        
    if active is not None:
        filters["active_only"] = active
        
    if date_start or date_end:
        filters["date_range"] = {
            "start": date_start,
            "end": date_end
        }
        
    if tag:
        filters["tags"] = tag
        
    if processing_status:
        filters["processing_status"] = processing_status
    
    # Get documents with filters
    documents = document_repository.get_multi_with_filters(
        db, skip=skip, limit=limit, **filters
    )
    
    # Transform Document models to Document schemas
    result = []
    for doc in documents:
        # Check if the document is attached to a project
        project_document = None
        if project_id and project_id != "null":
            project_document = next(
                (pd for pd in doc.project_documents if pd.project_id == project_id),
                None
            )
        
        # Check project details if the document is associated with any project
        project_name = None
        project_id_value = None
        
        # Project reference for this specific query if applicable
        if project_id and project_id != "null" and project_document:
            project_id_value = project_id
            # Try to get the project name
            from ...db.models.project import Project
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project_name = project.name
        # Otherwise check if document is associated with any project
        elif doc.project_documents:
            # Get first associated project
            from ...db.models.project import Project
            pd = doc.project_documents[0]
            project_id_value = pd.project_id
            project = db.query(Project).filter(Project.id == pd.project_id).first()
            if project:
                project_name = project.name
        
        # Map to response schema
        doc_dict = {
            "id": doc.id,
            "filename": doc.filename,
            "name": doc.filename,  # Frontend expects 'name'
            "description": doc.description,
            "type": doc.filetype,
            "filetype": doc.filetype,  # Add to satisfy schema
            "size": doc.filesize,
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
            "filepath": doc.filepath,
            "processed": doc.is_processed,
            "processing_failed": doc.is_processing_failed,
            "chunk_count": doc.chunk_count,
            "project_id": project_id_value,  # Use the determined project ID
            "project_name": project_name,    # Include project name for UI
            "active": project_document.is_active if project_document else doc.is_active,
            "tags": doc.tags,
            "meta_data": doc.meta_data
        }
        result.append(doc_dict)
    
    return result


@router.get("/{file_id}", response_model=Document)
def get_file(
    file_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a specific file by id.
    """
    document = document_repository.get(db, id=file_id)
    if not document:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get project name if document is linked to a project
    project_name = None
    project_id = None
    
    if document.project_documents:
        project_id = document.project_documents[0].project_id
        
        # Get project name from the database
        from ...db.models.project import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project_name = project.name
    
    # Map to response schema
    result = {
        "id": document.id,
        "filename": document.filename,
        "name": document.filename,  # Frontend expects 'name'
        "description": document.description,
        "type": document.filetype,
        "filetype": document.filetype,  # Add to satisfy schema
        "size": document.filesize,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat() if document.updated_at else None,
        "filepath": document.filepath,
        "processed": document.is_processed,
        "processing_failed": document.is_processing_failed,
        "chunk_count": document.chunk_count,
        "project_id": project_id,
        "project_name": project_name, # Add project name for UI display
        "active": document.project_documents[0].is_active if document.project_documents else document.is_active,
        "tags": document.tags,
        "meta_data": document.meta_data
    }
    
    return result


@router.post("/simple-upload")
async def simple_upload(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    file: UploadFile = File(...)
) -> Any:
    """Simplified file upload endpoint that doesn't use form parameters."""
    try:
        # Just return file info without trying to save it
        return {
            "filename": file.filename,
            "size": file.size,
            "content_type": file.content_type,
            "status": "received"
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/direct-upload")
async def direct_upload(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    display_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
) -> Any:
    """
    Simplified file upload endpoint that handles the naming issue more directly.
    """
    try:
        # Create a unique ID
        file_id = str(uuid.uuid4())
        original_filename = file.filename
        storage_filename = f"{file_id}_{original_filename}"
        
        # Create upload directory path
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file to disk
        filepath = os.path.join(upload_dir, storage_filename)
        with open(filepath, "wb") as f:
            # Read the file in chunks
            for chunk in iter(lambda: file.file.read(8192), b""):
                f.write(chunk)
        
        # Get file size and type
        filesize = os.path.getsize(filepath)
        filetype = os.path.splitext(original_filename)[1].lstrip(".").lower() or "txt"
        
        # Create a document directly using valid fields
        from ...db.models.document import Document
        
        document = Document(
            id=file_id,
            filename=display_name or original_filename,
            filepath=filepath,
            filetype=filetype,
            filesize=filesize,
            description=description
        )
        
        # Add to database
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Return success with document details
        return {
            "id": document.id,
            "filename": document.filename,
            "type": document.filetype,
            "size": document.filesize,
            "path": document.filepath,
            "description": document.description
        }
        
    except Exception as e:
        # Log the error for debugging
        import traceback
        traceback.print_exc()
        
        # Return error message
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "status": "failed"
        }

@router.post("/upload")  # Remove response_model to avoid Pydantic validation issues
async def upload_file(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),  # This is the frontend's name parameter - we'll map to filename
    description: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)  # Changed to str to handle JSON string from frontend
) -> Any:
    """
    Upload a new file.
    """
    # Import status tracker and json for parsing tags
    from ...document_processing.status_tracker import status_tracker
    import json
    
    # Parse tags if provided as a JSON string
    parsed_tags = None
    if tags:
        try:
            parsed_tags = json.loads(tags)
        except json.JSONDecodeError:
            # If not valid JSON, treat as a single tag
            parsed_tags = [tags]
    
    # Verify project if provided
    if project_id:
        project = project_repository.get(db, id=project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    
    # Create a unique filename for storage
    file_id = str(uuid.uuid4())
    original_filename = file.filename
    storage_filename = f"{file_id}_{original_filename}"
    
    # Determine file type
    filetype = os.path.splitext(original_filename)[1].lstrip(".").lower()
    if not filetype:
        filetype = "unknown"
    
    # Save file to disk
    filepath = os.path.join(UPLOAD_DIR, storage_filename)
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "wb") as f:
            # Read the file in chunks to handle large files
            for chunk in iter(lambda: file.file.read(8192), b""):
                f.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Get file size
    filesize = os.path.getsize(filepath)
    
    try:
        # Create document manually to ensure correct field mapping
        from ...db.models.document import Document
        
        # Create a new document
        document = Document(
            id=file_id,  # Use the same ID for document and filename
            filename=name or original_filename,  # Use provided name or fallback to original
            filepath=filepath,
            filetype=filetype,
            filesize=filesize,
            description=description,
            tags=parsed_tags,  # Using parsed tags from JSON string
            is_processed=False,
            is_processing_failed=False,
            is_active=True,
            chunk_count=0
        )
        
        # Add to database
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Verify the filepath is set correctly
        if not document.filepath or document.filepath == "":
            logger.error(f"Document {document.id} has empty filepath after save")
            raise HTTPException(status_code=500, detail="Failed to save document filepath")
        
        # Link to project if provided
        if project_id:
            document_repository.link_document_to_project(
                db, document_id=document.id, project_id=project_id
            )
        
        # Add to processing queue in status tracker
        status_tracker.add_to_queue(document.id, document.filename, document.filesize)
        
        # Schedule background processing with all necessary data
        # Pass filepath explicitly to avoid session issues
        background_tasks.add_task(
            process_document_background, 
            db=db, 
            document_id=document.id,
            filepath=document.filepath,
            filename=document.filename,
            filetype=document.filetype
        )
        
        # Map to response schema with both name and filename fields
        result = {
            "id": document.id,
            "filename": document.filename,
            "name": document.filename,  # Frontend expects 'name'
            "description": document.description,
            "type": document.filetype,
            "filetype": document.filetype, # Add to satisfy schema
            "size": document.filesize,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None,
            "filepath": document.filepath,
            "processed": document.is_processed or False,
            "processing_failed": document.is_processing_failed or False,
            "chunk_count": document.chunk_count or 0,
            "project_id": project_id,
            "active": True,
            "tags": document.tags,
            "meta_data": None
        }
        
        return result
    
    except Exception as e:
        # Clean up the file if the database operation fails
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(status_code=500, detail=f"Failed to create document record: {str(e)}")


@router.get("/{file_id}/download", response_class=FileResponse)
def download_file(
    file_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Download a file.
    """
    document = document_repository.get(db, id=file_id)
    if not document:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not os.path.exists(document.filepath):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=document.filepath,
        filename=document.filename,
        media_type="application/octet-stream"
    )


@router.post("/process", response_model=Document)
def process_file(
    background_tasks: BackgroundTasks,
    process_request: FileProcessRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Process a file to generate embeddings.
    """
    document = document_repository.get(db, id=process_request.file_id)
    if not document:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Allow re-processing for testing
    if document.is_processed:
        logger.info(f"Re-processing already processed file: {document.id}")
        # Reset the processed flag to allow re-processing
        document.is_processed = False
        document.chunk_count = 0
        # Delete existing chunks
        from ...db.models.document import DocumentChunk
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()
        db.commit()
    
    # Reset processing status if it failed before
    if document.is_processing_failed:
        document.is_processing_failed = False
        db.commit()
    
    # Schedule background processing
    background_tasks.add_task(
        process_document_background,
        db=db,
        document_id=document.id,
        chunk_size=process_request.chunk_size,
        chunk_overlap=process_request.chunk_overlap
    )
    
    # Get project name if document is linked to a project
    project_name = None
    project_id = None
    
    if document.project_documents:
        project_id = document.project_documents[0].project_id
        
        # Get project name from the database
        from ...db.models.project import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project_name = project.name
    
    # Map to response schema
    result = {
        "id": document.id,
        "filename": document.filename,
        "name": document.filename,  # Frontend expects 'name'
        "description": document.description,
        "type": document.filetype,
        "filetype": document.filetype,  # Add to satisfy schema
        "size": document.filesize,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat() if document.updated_at else None,
        "filepath": document.filepath,
        "processed": document.is_processed,
        "processing_failed": document.is_processing_failed,
        "chunk_count": document.chunk_count,
        "project_id": project_id,
        "project_name": project_name, # Add project name for UI display
        "active": document.project_documents[0].is_active if document.project_documents else document.is_active,
        "tags": document.tags,
        "meta_data": document.meta_data
    }
    
    return result


@router.post("/{file_id}/retry-processing", response_model=Document)
def retry_processing(
    file_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """
    Retry processing for a file that failed.
    """
    document = document_repository.get(db, id=file_id)
    if not document:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Allow re-processing for testing
    if document.is_processed:
        logger.info(f"Re-processing already processed file via retry: {document.id}")
        # Delete existing chunks before re-processing
        from ...db.models.document import DocumentChunk
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()
        document.chunk_count = 0
        db.commit()
    
    # Reset processing status
    document.is_processing_failed = False
    document.is_processed = False
    db.commit()
    
    # Schedule background processing
    background_tasks.add_task(
        process_document_background,
        db=db,
        document_id=document.id
    )
    
    # Get project name if document is linked to a project
    project_name = None
    project_id = None
    
    if document.project_documents:
        project_id = document.project_documents[0].project_id
        
        # Get project name from the database
        from ...db.models.project import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project_name = project.name
    
    # Map to response schema
    result = {
        "id": document.id,
        "filename": document.filename,
        "name": document.filename,  # Frontend expects 'name'
        "description": document.description,
        "type": document.filetype,
        "filetype": document.filetype,  # Add to satisfy schema
        "size": document.filesize,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat() if document.updated_at else None,
        "filepath": document.filepath,
        "processed": document.is_processed,
        "processing_failed": document.is_processing_failed,
        "chunk_count": document.chunk_count,
        "project_id": project_id,
        "project_name": project_name, # Add project name for UI display
        "active": document.project_documents[0].is_active if document.project_documents else document.is_active,
        "tags": document.tags,
        "meta_data": document.meta_data
    }
    
    return result


@router.patch("/{file_id}", response_model=Document)
def update_file(
    file_id: str,
    update_data: DocumentUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Update file metadata.
    """
    document = document_repository.get(db, id=file_id)
    if not document:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Update document fields
    if update_data.filename is not None:
        document.filename = update_data.filename
    
    if update_data.description is not None:
        document.description = update_data.description
    
    if update_data.active is not None:
        # Update activity status in project_document if project_id is provided
        if update_data.project_id:
            for pd in document.project_documents:
                if pd.project_id == update_data.project_id:
                    pd.is_active = update_data.active
                    break
        else:
            # Otherwise update the document's own active status
            document.is_active = update_data.active
    
    if update_data.tags is not None:
        document.tags = update_data.tags
    
    # If project_id is provided and different from current project, handle project change
    if update_data.project_id is not None:
        if update_data.project_id == "":
            # Remove from all projects
            for pd in document.project_documents:
                db.delete(pd)
        else:
            # Verify project exists
            project = project_repository.get(db, id=update_data.project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Check if already linked to this project
            existing_link = False
            for pd in document.project_documents:
                if pd.project_id == update_data.project_id:
                    existing_link = True
                    break
            
            # If not linked, create the link
            if not existing_link:
                document_repository.link_document_to_project(
                    db, document_id=document.id, project_id=update_data.project_id
                )
    
    db.commit()
    db.refresh(document)
    
    # Get project name if document is linked to a project
    project_name = None
    project_id = None
    
    if document.project_documents:
        project_id = document.project_documents[0].project_id
        
        # Get project name from the database
        from ...db.models.project import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project_name = project.name
    
    # Map to response schema
    result = {
        "id": document.id,
        "filename": document.filename,
        "name": document.filename,  # Frontend expects 'name'
        "description": document.description,
        "type": document.filetype,
        "filetype": document.filetype,  # Add to satisfy schema
        "size": document.filesize,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat() if document.updated_at else None,
        "filepath": document.filepath,
        "processed": document.is_processed,
        "processing_failed": document.is_processing_failed,
        "chunk_count": document.chunk_count,
        "project_id": project_id,
        "project_name": project_name, # Add project name for UI display
        "active": document.project_documents[0].is_active if document.project_documents else document.is_active,
        "tags": document.tags,
        "meta_data": document.meta_data
    }
    
    return result


@router.delete("/{file_id}", response_model=dict)
def delete_file(
    file_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a file.
    """
    document = document_repository.get(db, id=file_id)
    if not document:
        raise HTTPException(status_code=404, detail="File not found")
    
    filepath = document.filepath
    
    # Remove from database
    document_repository.remove(db, id=file_id)
    
    # Remove file from disk if it exists
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Error removing file {filepath}: {str(e)}")
    
    return {"success": True}


@router.post("/bulk-delete", response_model=FileBulkOperationResult)
def bulk_delete_files(
    request: FileBulkOperationRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete multiple files at once.
    """
    success = []
    failed = []
    
    for file_id in request.file_ids:
        try:
            document = document_repository.get(db, id=file_id)
            if document:
                filepath = document.filepath
                
                # Remove from database
                document_repository.remove(db, id=file_id)
                
                # Remove file from disk if it exists
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        # Log the error but don't fail the entire operation
                        print(f"Error removing file {filepath}: {str(e)}")
                
                success.append(file_id)
            else:
                failed.append({"id": file_id, "error": "File not found"})
        except Exception as e:
            failed.append({"id": file_id, "error": str(e)})
    
    return {"success": success, "failed": failed}


@router.post("/link", response_model=FileBulkOperationResult)
def link_files_to_project(
    request: FileBulkOperationRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Link multiple files to a project.
    """
    if not request.project_id:
        raise HTTPException(status_code=400, detail="Project ID is required")
    
    # Verify project exists
    project = project_repository.get(db, id=request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    success = []
    failed = []
    
    # Get project name for including in the response
    project_name = project.name
    
    for file_id in request.file_ids:
        try:
            document = document_repository.get(db, id=file_id)
            if document:
                # Link to project
                document_repository.link_document_to_project(
                    db, document_id=file_id, project_id=request.project_id
                )
                success.append(file_id)
            else:
                failed.append({"id": file_id, "error": "File not found"})
        except Exception as e:
            failed.append({"id": file_id, "error": str(e)})
    
    return {
        "success": success, 
        "failed": failed,
        "project_id": request.project_id,
        "project_name": project_name
    }


@router.post("/unlink", response_model=FileBulkOperationResult)
def unlink_files_from_project(
    request: FileBulkOperationRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Unlink multiple files from a project.
    """
    if not request.project_id:
        raise HTTPException(status_code=400, detail="Project ID is required")
    
    # Verify project exists
    project = project_repository.get(db, id=request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    success = []
    failed = []
    
    # Get project name for including in the response
    project_name = project.name
    
    for file_id in request.file_ids:
        try:
            # Unlink from project
            result = document_repository.unlink_document_from_project(
                db, document_id=file_id, project_id=request.project_id
            )
            
            if result:
                success.append(file_id)
            else:
                failed.append({"id": file_id, "error": "File not linked to project"})
        except Exception as e:
            failed.append({"id": file_id, "error": str(e)})
    
    return {
        "success": success, 
        "failed": failed,
        "project_id": request.project_id,
        "project_name": project_name
    }


@router.post("/search", response_model=List[FileSearchResult])
def search_files(
    search_request: FileSearchRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Search for files based on content and metadata.
    """
    try:
        # Import models for direct querying
        from sqlalchemy import func, distinct
        from ...db.models.document import Document, DocumentChunk, ProjectDocument
        
        # Start with a base query to get documents and their relevance
        query = (
            db.query(
                Document,
                func.count(distinct(DocumentChunk.id)).label("relevance")
            )
            .join(DocumentChunk)
            .filter(DocumentChunk.content.ilike(f"%{search_request.query}%"))
            .group_by(Document.id)
        )
        
        # Apply filters
        if search_request.project_id:
            query = query.join(ProjectDocument).filter(
                ProjectDocument.project_id == search_request.project_id
            )
        
        if search_request.file_types:
            query = query.filter(Document.filetype.in_(search_request.file_types))
        
        if search_request.date_range and search_request.date_range.get("start"):
            query = query.filter(Document.created_at >= search_request.date_range["start"])
        
        if search_request.date_range and search_request.date_range.get("end"):
            query = query.filter(Document.created_at <= search_request.date_range["end"])
        
        # Get the documents with relevance counts
        documents_with_relevance = query.order_by(
            func.count(distinct(DocumentChunk.id)).desc()
        ).limit(search_request.limit or 10).all()
        
        # Map to response schema
        results = []
        for document, relevance_count in documents_with_relevance:
            # Calculate a relevance score between 0-100
            # This is simplistic - in a real implementation, you'd use the embedding similarity
            relevance_score = min(100, int(relevance_count * 20))
            
            # Get content snippets if requested
            content_snippets = []
            if search_request.include_content:
                # Find chunks that match the search query
                matching_chunks = db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == document.id,
                    DocumentChunk.content.ilike(f"%{search_request.query}%")
                ).limit(3).all()
                
                # Extract the relevant parts of the chunks
                for chunk in matching_chunks:
                    # Find the search term in the chunk
                    content = chunk.content
                    query_lower = search_request.query.lower()
                    content_lower = content.lower()
                    
                    # Find position of search term
                    pos = content_lower.find(query_lower)
                    if pos >= 0:
                        # Get context around the search term
                        start = max(0, pos - 50)
                        end = min(len(content), pos + len(search_request.query) + 50)
                        
                        # Create snippet with context
                        snippet = content[start:end]
                        if start > 0:
                            snippet = "..." + snippet
                        if end < len(content):
                            snippet = snippet + "..."
                        
                        content_snippets.append(snippet)
            
            # Get project name if document is linked to a project
            project_name = None
            if document.project_documents:
                project_id = document.project_documents[0].project_id
                # Get project details
                from ...db.models.project import Project
                project = db.query(Project).filter(Project.id == project_id).first()
                if project:
                    project_name = project.name

            # Create result object
            result = {
                "id": document.id,
                "filename": document.filename,
                "name": document.filename,  # Frontend expects 'name'
                "description": document.description,
                "type": document.filetype,
                "filetype": document.filetype,  # Add to satisfy schema
                "size": document.filesize,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat() if document.updated_at else None,
                "filepath": document.filepath,
                "processed": document.is_processed,
                "processing_failed": document.is_processing_failed,
                "chunk_count": document.chunk_count,
                "project_id": document.project_documents[0].project_id if document.project_documents else None,
                "project_name": project_name,  # Include project name for UI display
                "active": document.project_documents[0].is_active if document.project_documents else document.is_active,
                "tags": document.tags,
                "meta_data": document.meta_data,
                "relevance": relevance_score,
                "content_snippets": content_snippets
            }
            results.append(result)
        
        return results
    
    except Exception as e:
        # Log the error
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/{file_id}/preview", response_model=dict)
def get_file_preview(
    file_id: str,
    max_length: Optional[int] = 10000,
    page: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a preview of file contents.
    """
    document = document_repository.get(db, id=file_id)
    if not document:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if document has been processed
    if document.is_processed:
        # Return chunks as preview
        from ...db.models.document import DocumentChunk
        
        # Build query for chunks
        query = db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id)
        
        # Filter by page if provided
        if page is not None:
            query = query.filter(DocumentChunk.page_number == page)
        
        # Order chunks by index
        query = query.order_by(DocumentChunk.chunk_index)
        
        # Get chunks
        chunks = query.all()
        
        if chunks:
            # Build a preview from chunks
            content = "\n\n".join([f"Chunk {chunk.chunk_index + 1}:\n{chunk.content}" for chunk in chunks])
            return {"content": content[:max_length]}
    
    # If document not processed or no chunks found, try direct file reading
    if not os.path.exists(document.filepath):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # For text files, return content directly
    if document.filetype.lower() in ["txt", "md", "csv", "json", "py", "js", "html", "css"]:
        try:
            with open(document.filepath, "r", encoding="utf-8") as f:
                content = f.read(max_length)
                return {"content": content}
        except UnicodeDecodeError:
            # If UTF-8 decode fails, try different encoding or fallback to binary
            try:
                # Try with latin-1 encoding which never fails but might display incorrectly
                with open(document.filepath, "r", encoding="latin-1") as f:
                    content = f.read(max_length)
                    return {"content": content}
            except Exception:
                pass
    
    # For non-text files or files that failed reading, return placeholder with processing status
    filetype = document.filetype.lower()
    status = ""
    
    if document.is_processed:
        status = "The file has been processed. "
    elif document.is_processing_failed:
        status = "Processing failed. Please retry processing. "
    else:
        status = "The file has not been processed yet. "
    
    if filetype in ["pdf", "docx", "doc"]:
        if document.is_processed:
            return {"content": f"[{status}Use the document chunk view to see the content.]"}
        else:
            return {"content": f"[{status}{document.filetype.upper()} file must be processed first.]"}
    elif filetype in ["jpg", "jpeg", "png", "gif"]:
        return {"content": f"[{status}Image preview not available. Use download endpoint to retrieve the {document.filetype.upper()} file.]"}
    else:
        return {"content": f"[{status}Preview not available for {document.filetype.upper()} files.]"}


# Simple test endpoints that don't require database access
@router.get("/test-status")
def test_status():
    """
    Simple test endpoint to verify routing is working.
    """
    return {"status": "ok", "message": "Test endpoint is working"}

@router.get("/test-ping")
def test_ping():
    """
    Simple ping endpoint to verify routing is working.
    """
    return {"ping": "pong", "time": "now"}

# Processing status endpoints
@router.get("/processing-status", response_model=ProcessingStats)
def get_processing_status(db: Session = Depends(get_db)) -> Any:
    """
    Get current processing status for all files.
    """
    # Import status tracker
    from ...document_processing.status_tracker import status_tracker
    
    # Default values as fallback
    default_stats = {
        "total_files": 0,
        "processed_files": 0,
        "failed_files": 0,
        "processing_files": 0,
        "total_chunks": 0,
        "gpu_usage": 0,
        "eta": 0
    }
    
    try:
        # Get status from tracker
        tracker_status = status_tracker.get_status()
        if not tracker_status:
            print("Warning: status_tracker.get_status() returned empty or None")
            return default_stats
            
        # Build response with fallbacks for missing keys
        return {
            "total_files": tracker_status.get("total_files", 0),
            "processed_files": tracker_status.get("processed_files", 0),
            "failed_files": tracker_status.get("failed_files", 0),
            "processing_files": tracker_status.get("processing_files", 0),
            "total_chunks": tracker_status.get("total_chunks", 0),
            "gpu_usage": tracker_status.get("gpu_usage", 0),
            "eta": tracker_status.get("eta", 0)
        }
        
    except Exception as e:
        # Log the error but don't propagate it to the client
        print(f"Error getting processing status: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return default stats instead of raising an error
        return default_stats


@router.get("/tags", response_model=List[str])
def get_all_tags(
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all file tags in the system.
    """
    # In a real implementation, this would query unique tags from the database
    # For now, return a mock list
    return ["document", "report", "code", "research", "presentation"]


@router.get("/debug/project-documents/{project_id}")
def debug_project_documents(
    project_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Debug endpoint to check document status for a project.
    """
    from ...db.models.document import Document, DocumentChunk
    from ...db.models.project import ProjectDocument
    
    # Get all documents for the project
    documents = db.query(Document).join(ProjectDocument).filter(
        ProjectDocument.project_id == project_id
    ).all()
    
    result = {
        "project_id": project_id,
        "total_documents": len(documents),
        "documents": []
    }
    
    for doc in documents:
        # Count chunks
        chunk_count = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == doc.id
        ).count()
        
        # Check if chunks have embeddings
        chunks_with_embeddings = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == doc.id,
            DocumentChunk.embedding != None
        ).count()
        
        doc_info = {
            "id": doc.id,
            "filename": doc.filename,
            "filetype": doc.filetype,
            "is_processed": doc.is_processed,
            "is_processing_failed": doc.is_processing_failed,
            "chunk_count": chunk_count,
            "chunks_with_embeddings": chunks_with_embeddings,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        }
        result["documents"].append(doc_info)
    
    return result