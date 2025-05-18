"""
Batch upload script for adding multiple files to the system.
This directly interacts with the database to bypass API issues.
"""
import os
import sys
import uuid
import argparse
import csv
import glob
from sqlalchemy.orm import Session
import datetime

# Ensure app modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the necessary modules
from app.db.database import engine
from app.db.models.document import Document
from app.db.repositories.document_repository import document_repository
from app.db.repositories.project_repository import project_repository

def batch_upload(source_dir, pattern="*.*", project_id=None, description_prefix=None):
    """
    Upload multiple files matching a pattern from a source directory.
    
    Args:
        source_dir (str): Directory containing files to upload
        pattern (str): Glob pattern to match files (default: "*.*")
        project_id (str, optional): Project to link files to
        description_prefix (str, optional): Prefix for file descriptions
        
    Returns:
        list: List of document IDs that were created
    """
    # Check if source directory exists
    if not os.path.isdir(source_dir):
        print(f"❌ Source directory not found: {source_dir}")
        return []
    
    # Find files matching pattern
    file_paths = glob.glob(os.path.join(source_dir, pattern))
    if not file_paths:
        print(f"❌ No files found matching pattern: {pattern}")
        return []
    
    print(f"Found {len(file_paths)} files to upload")
    
    # Create a session
    db = Session(engine)
    
    # Check project if provided
    if project_id:
        project = project_repository.get(db, id=project_id)
        if not project:
            print(f"❌ Project not found: {project_id}")
            db.close()
            return []
        print(f"✅ Project found: {project.name} ({project_id})")
    
    # Setup upload directory
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Track results
    uploaded_files = []
    failed_files = []
    
    # Process each file
    for file_path in file_paths:
        try:
            # Get file info
            file_id = str(uuid.uuid4())
            original_filename = os.path.basename(file_path)
            
            # Determine file type
            filetype = os.path.splitext(original_filename)[1].lstrip(".").lower()
            if not filetype:
                filetype = "unknown"
            
            # Get file size
            filesize = os.path.getsize(file_path)
            
            # Create a unique storage filename
            storage_filename = f"{file_id}_{original_filename}"
            dest_path = os.path.join(upload_dir, storage_filename)
            
            # Prepare description
            if description_prefix:
                description = f"{description_prefix}: {original_filename}"
            else:
                description = f"Uploaded from batch process: {original_filename}"
            
            # Copy file to uploads directory
            with open(file_path, "rb") as src, open(dest_path, "wb") as dst:
                dst.write(src.read())
            
            # Create document record
            document = Document(
                id=file_id,
                filename=original_filename,
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
            
            # Link to project if provided
            if project_id:
                document_repository.link_document_to_project(
                    db, document_id=document.id, project_id=project_id
                )
            
            # Add to successful uploads
            uploaded_files.append({
                "id": document.id,
                "filename": document.filename,
                "filepath": document.filepath,
                "size": document.filesize,
                "type": document.filetype
            })
            
            print(f"✅ Uploaded: {original_filename} -> {document.id}")
            
        except Exception as e:
            # Log failure
            failed_files.append({
                "filename": original_filename,
                "error": str(e)
            })
            db.rollback()
            print(f"❌ Failed to upload {original_filename}: {str(e)}")
    
    # Close session
    db.close()
    
    # Return results
    return {
        "uploaded": uploaded_files,
        "failed": failed_files
    }

def export_results_to_csv(results, output_file):
    """Export upload results to a CSV file."""
    if not results["uploaded"] and not results["failed"]:
        print("No results to export")
        return
    
    # Create successful uploads CSV
    if results["uploaded"]:
        success_file = f"{output_file}_success.csv"
        with open(success_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "filename", "filepath", "size", "type"])
            writer.writeheader()
            writer.writerows(results["uploaded"])
        print(f"✅ Exported successful uploads to: {success_file}")
    
    # Create failed uploads CSV
    if results["failed"]:
        failed_file = f"{output_file}_failed.csv"
        with open(failed_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["filename", "error"])
            writer.writeheader()
            writer.writerows(results["failed"])
        print(f"✅ Exported failed uploads to: {failed_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch upload files to the system")
    parser.add_argument("source_dir", help="Directory containing files to upload")
    parser.add_argument("--pattern", default="*.*", help="Glob pattern to match files (default: *.*)")
    parser.add_argument("--project", help="Project ID to link files to")
    parser.add_argument("--description", help="Prefix for file descriptions")
    parser.add_argument("--output", default="batch_upload_results", help="Base name for output CSV files")
    
    args = parser.parse_args()
    
    print(f"Batch uploading files from: {args.source_dir}")
    print(f"Using pattern: {args.pattern}")
    
    # Perform batch upload
    results = batch_upload(
        args.source_dir,
        pattern=args.pattern,
        project_id=args.project,
        description_prefix=args.description
    )
    
    # Print summary
    print("\nUpload Summary:")
    print(f"✅ Successfully uploaded: {len(results['uploaded'])} files")
    print(f"❌ Failed to upload: {len(results['failed'])} files")
    
    # Export results
    export_results_to_csv(results, args.output)
    
    print("\nBatch upload complete!")