# src/services/file_service.py
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from ..db.repositories.document_repo import DocumentRepository
from ..db.repositories.project_repo import ProjectRepository
from ..document_processing.file_manager import FileManager
from .service_factory import service_factory

logger = logging.getLogger(__name__)

class FileService:
    """Service for file operations"""
    
    def __init__(self):
        """Initialize the file service"""
        # Get dependencies from service factory
        self.file_manager = service_factory.get_service('file_manager')
        self.project_repo = service_factory.get_repository('project_repo')
    
    def upload_documents(self, files, tags, descriptions, project_names=None):
        """
        Upload and process multiple documents
        
        Args:
            files: List of file objects
            tags: List of tags (P, B, or PB)
            descriptions: List of descriptions
            project_names: Optional list of project names to attach files to
            
        Returns:
            List of processed document data
        """
        results = []
        
        if not files:
            return results
        
        logger.info(f"Processing {len(files)} documents")
        
        for i, file in enumerate(files):
            # Get individual metadata
            tag = tags[i] if i < len(tags) else tags[-1]
            # Convert UI tag format (ex: "Private (P)") to database format (ex: "P")
            tag_code = tag.split("(")[1].split(")")[0] if "(" in tag else tag
            
            description = descriptions[i] if i < len(descriptions) else descriptions[-1]
            
            # Process project if provided
            project_id = None
            if project_names and i < len(project_names) and project_names[i] != "None":
                # Convert project name to ID
                project_id = self.project_repo.get_project_id_by_name(project_names[i])
            
            try:
                # Upload file to storage
                document = self.file_manager.save_uploaded_file(file, tag_code, description)
                
                if document:
                    # Process file
                    success = self.file_manager.process_file(document['id'])
                    
                    # Attach to project if needed
                    if success and project_id:
                        self.file_manager.attach_to_project(document['id'], project_id)
                    
                    # Add to results
                    status = "Active" if success else "Failed"
                    results.append({
                        'id': document['id'],
                        'filename': document['filename'],
                        'tag': tag,
                        'description': description,
                        'status': status,
                        'project': project_names[i] if project_names and i < len(project_names) else "None"
                    })
                
            except Exception as e:
                logger.error(f"Error processing file {file.name}: {e}")
                # Add failed entry
                results.append({
                    'id': None,
                    'filename': file.name,
                    'tag': tag,
                    'description': description,
                    'status': "Failed",
                    'project': project_names[i] if project_names and i < len(project_names) else "None"
                })
        
        return results
    
    def get_all_documents(self, search_text=None, tag_filter=None):
        """
        Get all documents with optional filtering
        
        Args:
            search_text: Optional search text
            tag_filter: Optional tag filter
            
        Returns:
            List of document data for display
        """
        try:
            # Get tag code if filter is specified
            tag_code = None
            if tag_filter and tag_filter != "All":
                # Convert UI tag format to database format
                tag_code = tag_filter.split("(")[1].split(")")[0] if "(" in tag_filter else tag_filter
            
            # Get documents from database
            if search_text:
                # Use search functionality
                docs = self.file_manager.document_repo.search_documents(
                    query=search_text,
                    tag=tag_code,
                    status="Active",
                    page=1,
                    page_size=100
                )
            else:
                # Get all documents
                docs, _ = self.file_manager.get_all_documents(
                    tag=tag_code,
                    status="Active",
                    page=1,
                    page_size=100
                )
            
            # Format for display
            results = []
            for doc in docs:
                # Convert tag from database format to UI format
                tag_display = doc['tag']
                if tag_display == "P":
                    tag_display = "Private (P)"
                elif tag_display == "B":
                    tag_display = "Business (B)"
                elif tag_display == "PB":
                    tag_display = "Both (PB)"
                
                # Format project names as comma-separated string
                project_names = ", ".join(doc.get('project_names', []))
                if not project_names:
                    project_names = "-"
                
                # Format file size
                from ..utils.document_formatting import format_file_size
                size_display = format_file_size(doc['file_size'])
                
                # Format timestamp
                from ..utils.document_formatting import format_timestamp
                date_display = format_timestamp(doc['created_at'])
                
                # Format actions
                actions = "🔍 View | ⬇️ Download | ❌ Delete"
                
                results.append([
                    doc['filename'],
                    doc['content_type'],
                    tag_display,
                    doc['description'][:50] + "..." if len(doc['description']) > 50 else doc['description'],
                    doc['status'],
                    size_display,
                    date_display,
                    project_names,
                    actions
                ])
            
            return results
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []