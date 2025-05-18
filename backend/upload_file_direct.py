"""
Standalone script to upload a file directly to the database.
Run this script directly to upload a file without going through the API.
"""
import os
import sys
import uuid
from sqlalchemy.orm import Session
import argparse
import datetime

# Ensure app modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the necessary modules
from app.db.database import engine, get_db
from app.db.models.document import Document
from app.db.repositories.document_repository import document_repository
from app.db.repositories.project_repository import project_repository

def upload_file(file_path, name=None, description=None, project_id=None):
    """
    Upload a file directly to the database.
    
    Args:
        file_path (str): Path to the file to upload
        name (str, optional): Display name for the file. Defaults to the filename.
        description (str, optional): File description. Defaults to None.
        project_id (str, optional): Project to link the file to. Defaults to None.
    
    Returns:
        str: ID of the created document
    """
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    # Create a session
    db = Session(engine)
    
    try:
        # Get file info
        file_id = str(uuid.uuid4())
        original_filename = os.path.basename(file_path)
        display_name = name or original_filename
        
        # Determine file type
        filetype = os.path.splitext(original_filename)[1].lstrip(".").lower()
        if not filetype:
            filetype = "unknown"
        
        # Get file size
        filesize = os.path.getsize(file_path)
        
        # Set up destination directory and file path
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create a unique storage filename
        storage_filename = f"{file_id}_{original_filename}"
        dest_path = os.path.join(upload_dir, storage_filename)
        
        # Copy file to uploads directory
        with open(file_path, "rb") as src, open(dest_path, "wb") as dst:
            dst.write(src.read())
            
        print(f"✅ File copied to: {dest_path}")
        
        # Create document record
        document = Document(
            id=file_id,
            filename=display_name,
            filepath=dest_path,
            filetype=filetype,
            filesize=filesize,
            description=description,
            is_processed=False,
            is_processing_failed=False,
            is_active=True,
            created_at=datetime.datetime.now()
        )
        
        # Add to database
        db.add(document)
        db.commit()
        db.refresh(document)
        
        print(f"✅ Document record created with ID: {document.id}")
        
        # Link to project if provided
        if project_id:
            # Check if project exists
            project = project_repository.get(db, id=project_id)
            if not project:
                print(f"❌ Project not found: {project_id}")
            else:
                # Link document to project
                link = document_repository.link_document_to_project(
                    db, document_id=document.id, project_id=project_id
                )
                print(f"✅ Document linked to project: {project_id}")
        
        # Print document info
        print("\nDocument details:")
        print(f"  - ID: {document.id}")
        print(f"  - Filename: {document.filename}")
        print(f"  - File path: {document.filepath}")
        print(f"  - File type: {document.filetype}")
        print(f"  - File size: {document.filesize} bytes")
        print(f"  - Description: {document.description}")
        print(f"  - Created at: {document.created_at}")
        
        return document.id
        
    except Exception as e:
        # Roll back on error
        db.rollback()
        print(f"❌ Error uploading file: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        # Close the session
        db.close()

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Upload a file directly to the database")
    parser.add_argument("file_path", help="Path to the file to upload")
    parser.add_argument("--name", help="Display name for the file (defaults to filename)")
    parser.add_argument("--description", help="File description")
    parser.add_argument("--project", help="Project ID to link the file to")
    
    args = parser.parse_args()
    
    # Upload the file
    print(f"Uploading file: {args.file_path}")
    document_id = upload_file(
        args.file_path, 
        name=args.name, 
        description=args.description, 
        project_id=args.project
    )
    
    if document_id:
        print(f"\n✅ File uploaded successfully with ID: {document_id}")
    else:
        print("\n❌ File upload failed")