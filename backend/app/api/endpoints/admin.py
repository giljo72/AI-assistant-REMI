import os
import shutil
from typing import Any, Dict, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...db.database import get_db

router = APIRouter()

# Helper function to reset database tables
async def reset_database_tables(db: Session, tables: list = None):
    """Reset specified database tables or all tables if none specified."""
    try:
        # Get all table names if not specified
        if not tables:
            result = db.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            ))
            tables = [row[0] for row in result]
        
        # Disable foreign key checks temporarily
        db.execute(text("SET session_replication_role = 'replica'"))
        
        try:
            # Truncate each table
            for table in tables:
                # Skip pgvector extension tables
                if table.startswith('pg_') or table == 'vector':
                    continue
                
                db.execute(text(f'TRUNCATE TABLE "{table}" CASCADE'))
            
            db.commit()
        finally:
            # Re-enable foreign key checks
            db.execute(text("SET session_replication_role = 'origin'"))
            
        return {"success": True, "message": f"Reset {len(tables)} tables successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database reset failed: {str(e)}")

# Helper function to reset vector embeddings
async def reset_vector_store(db: Session):
    """Reset vector embeddings in the database."""
    try:
        # Drop vector embeddings from document chunks
        db.execute(text("UPDATE document_chunks SET embedding = NULL"))
        db.commit()
        
        return {"success": True, "message": "Vector embeddings reset successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Vector store reset failed: {str(e)}")

# Helper function to clear file uploads
async def clear_uploaded_files():
    """Delete all uploaded files."""
    try:
        # Define paths to file directories
        UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "uploads")
        PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "processed")
        
        # Clear upload directory
        if os.path.exists(UPLOAD_DIR):
            for file in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        
        # Clear processed directory
        if os.path.exists(PROCESSED_DIR):
            for file in os.listdir(PROCESSED_DIR):
                file_path = os.path.join(PROCESSED_DIR, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        
        return {"success": True, "message": "All uploaded files cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File cleanup failed: {str(e)}")

@router.post("/reset/database", response_model=Dict[str, Any])
async def reset_database(
    background_tasks: BackgroundTasks,
    preserve_prompts: bool = True,
    db: Session = Depends(get_db)
):
    """
    Reset the database by truncating project-related tables.
    By default, preserves system prompts, user prompts, and personal profiles.
    """
    # Tables to preserve when preserve_prompts is True
    preserved_tables = ['system_prompts', 'user_prompts', 'personal_profiles', 'user_preferences']
    
    # Get all tables and filter out preserved ones if needed
    result = db.execute(text(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
    ))
    all_tables = [row[0] for row in result]
    
    if preserve_prompts:
        tables_to_reset = [t for t in all_tables if t not in preserved_tables]
    else:
        tables_to_reset = all_tables
    
    # This is a potentially destructive operation, so we run it in the background
    background_tasks.add_task(reset_database_tables, db, tables_to_reset)
    
    return {
        "success": True, 
        "message": f"Database reset initiated. {'Preserving prompts and profiles.' if preserve_prompts else 'Clearing ALL data.'}"
    }

@router.post("/reset/vector-store", response_model=Dict[str, Any])
async def reset_vectors(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Reset the vector store by removing all vector embeddings.
    """
    background_tasks.add_task(reset_vector_store, db)
    
    return {
        "success": True, 
        "message": "Vector store reset initiated in the background"
    }

@router.post("/reset/files", response_model=Dict[str, Any])
async def reset_files(
    background_tasks: BackgroundTasks,
):
    """
    Delete all uploaded and processed files from the file system.
    """
    background_tasks.add_task(clear_uploaded_files)
    
    return {
        "success": True, 
        "message": "File cleanup initiated in the background"
    }

@router.post("/reset/all", response_model=Dict[str, Any])
async def reset_everything(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Reset everything: database, vector store, and files.
    """
    background_tasks.add_task(reset_database_tables, db)
    background_tasks.add_task(reset_vector_store, db)
    background_tasks.add_task(clear_uploaded_files)
    
    return {
        "success": True, 
        "message": "Complete system reset initiated in the background"
    }

@router.get("/system-info", response_model=Dict[str, Any])
async def get_system_info(
    db: Session = Depends(get_db)
):
    """
    Get information about the system state.
    """
    # Get database stats
    try:
        # Count tables
        table_result = db.execute(text(
            "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'"
        ))
        table_count = table_result.scalar()
        
        # Count records in key tables
        document_result = db.execute(text("SELECT COUNT(*) FROM documents"))
        document_count = document_result.scalar()
        
        project_result = db.execute(text("SELECT COUNT(*) FROM projects"))
        project_count = project_result.scalar()
        
        chunk_result = db.execute(text("SELECT COUNT(*) FROM document_chunks"))
        chunk_count = chunk_result.scalar()
        
        # Count vector embeddings
        embedding_result = db.execute(text(
            "SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL"
        ))
        embedding_count = embedding_result.scalar()
        
        # File system info
        UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "uploads")
        PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "processed")
        
        upload_file_count = 0
        upload_size = 0
        if os.path.exists(UPLOAD_DIR):
            upload_files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
            upload_file_count = len(upload_files)
            upload_size = sum(os.path.getsize(os.path.join(UPLOAD_DIR, f)) for f in upload_files)
        
        processed_file_count = 0
        processed_size = 0
        if os.path.exists(PROCESSED_DIR):
            processed_files = [f for f in os.listdir(PROCESSED_DIR) if os.path.isfile(os.path.join(PROCESSED_DIR, f))]
            processed_file_count = len(processed_files)
            processed_size = sum(os.path.getsize(os.path.join(PROCESSED_DIR, f)) for f in processed_files)
        
        return {
            "database": {
                "table_count": table_count,
                "document_count": document_count,
                "project_count": project_count,
                "chunk_count": chunk_count,
                "embedding_count": embedding_count,
            },
            "files": {
                "upload_count": upload_file_count,
                "upload_size_bytes": upload_size,
                "processed_count": processed_file_count,
                "processed_size_bytes": processed_size,
                "total_count": upload_file_count + processed_file_count,
                "total_size_bytes": upload_size + processed_size,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")