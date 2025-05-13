# src/db/repositories/project_repo.py
from typing import List, Dict, Any, Optional
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError
import logging

from ...core.db_interface import get_db_session
from ..models import Project, Chat, DocumentProject, Document

logger = logging.getLogger(__name__)

class ProjectRepository:
    """Repository for project operations"""
    
    def create_project(self, name: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new project
        
        Args:
            name: Project name
            custom_prompt: Optional custom system prompt for this project
            
        Returns:
            Project as dictionary if successful, None otherwise
        """
        try:
            with get_db_session() as session:
                project = Project(
                    name=name,
                    custom_prompt=custom_prompt
                )
                
                session.add(project)
                session.flush()  # To get the ID
                
                logger.info(f"Created project: {name} (ID: {project.id})")
                
                # Make a copy to return, as the session will be closed
                result = {
                    'id': project.id,
                    'name': project.name,
                    'custom_prompt': project.custom_prompt,
                    'created_at': project.created_at,
                    'updated_at': project.updated_at
                }
                
                return result
        except SQLAlchemyError as e:
            logger.error(f"Database error creating project: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating project: {e}")
            raise
    
    def update_project(self, 
                      project_id: int, 
                      name: Optional[str] = None, 
                      custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a project
        
        Args:
            project_id: ID of project to update
            name: New project name (if provided)
            custom_prompt: New custom prompt (if provided)
            
        Returns:
            Updated project as dictionary if successful
        """
        try:
            with get_db_session() as session:
                # Prepare update values
                update_values = {}
                if name is not None:
                    update_values['name'] = name
                if custom_prompt is not None:
                    update_values['custom_prompt'] = custom_prompt
                
                # Skip if no updates
                if not update_values:
                    # Just return the current project
                    return self.get_project(project_id)
                
                # Update the project
                stmt = (
                    update(Project)
                    .where(Project.id == project_id)
                    .values(**update_values)
                    .returning(Project)
                )
                
                result = session.execute(stmt).scalar_one_or_none()
                
                if result:
                    logger.info(f"Updated project ID {project_id}")
                    
                    # Convert to dictionary
                    return {
                        'id': result.id,
                        'name': result.name,
                        'custom_prompt': result.custom_prompt,
                        'created_at': result.created_at,
                        'updated_at': result.updated_at
                    }
                else:
                    logger.warning(f"Project ID {project_id} not found for update")
                    raise ValueError(f"Project ID {project_id} not found")
        except SQLAlchemyError as e:
            logger.error(f"Database error updating project: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating project: {e}")
            raise
    
    def delete_project(self, project_id: int) -> bool:
        """
        Delete a project and all its chats
        
        Args:
            project_id: ID of project to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_session() as session:
                # Delete the project (cascades to chats and associations)
                stmt = delete(Project).where(Project.id == project_id)
                result = session.execute(stmt)
                
                if result.rowcount > 0:
                    logger.info(f"Deleted project ID {project_id}")
                    return True
                else:
                    logger.warning(f"Project ID {project_id} not found for deletion")
                    return False
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting project: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting project: {e}")
            return False
    
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a project by ID
        
        Args:
            project_id: ID of project to retrieve
            
        Returns:
            Project as dictionary if found, None otherwise
        """
        try:
            with get_db_session() as session:
                stmt = select(Project).where(Project.id == project_id)
                result = session.execute(stmt).scalar_one_or_none()
                
                if result:
                    return {
                        'id': result.id,
                        'name': result.name,
                        'custom_prompt': result.custom_prompt,
                        'created_at': result.created_at,
                        'updated_at': result.updated_at
                    }
                else:
                    logger.warning(f"Project ID {project_id} not found")
                    return None
        except SQLAlchemyError as e:
            logger.error(f"Database error getting project: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting project: {e}")
            return None
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects
        
        Returns:
            List of all projects as dictionaries
        """
        try:
            with get_db_session() as session:
                stmt = select(Project).order_by(Project.updated_at.desc())
                results = session.execute(stmt).scalars().all()
                
                # Convert to dictionaries
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
        except SQLAlchemyError as e:
            logger.error(f"Database error getting all projects: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting all projects: {e}")
            return []
    
    def get_project_chats(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all chats for a project
        
        Args:
            project_id: ID of project to get chats for
            
        Returns:
            List of chats as dictionaries
        """
        try:
            with get_db_session() as session:
                stmt = select(Chat).where(Chat.project_id == project_id).order_by(Chat.created_at)
                results = session.execute(stmt).scalars().all()
                
                # Convert to dictionaries
                chats = []
                for chat in results:
                    chats.append({
                        'id': chat.id,
                        'name': chat.name,
                        'project_id': chat.project_id,
                        'created_at': chat.created_at,
                        'updated_at': chat.updated_at
                    })
                
                return chats
        except SQLAlchemyError as e:
            logger.error(f"Database error getting project chats: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting project chats: {e}")
            return []
    
    def get_project_documents(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all documents attached to a project
        
        Args:
            project_id: ID of project to get documents for
            
        Returns:
            List of documents as dictionaries
        """
        try:
            with get_db_session() as session:
                # Join Document with DocumentProject to get attached documents
                stmt = (
                    select(Document)
                    .join(DocumentProject, Document.id == DocumentProject.document_id)
                    .where(DocumentProject.project_id == project_id)
                    .order_by(Document.filename)
                )
                
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
                        'created_at': doc.created_at,
                        'updated_at': doc.updated_at
                    })
                
                return documents
        except SQLAlchemyError as e:
            logger.error(f"Database error getting project documents: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting project documents: {e}")
            return []