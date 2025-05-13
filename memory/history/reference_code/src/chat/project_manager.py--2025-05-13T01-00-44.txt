# src/chat/project_manager.py
from typing import List, Dict, Any, Optional
import logging

from ..db.repositories.project_repo import ProjectRepository
from ..db.repositories.chat_repo import ChatRepository
from ..db.repositories.document_repo import DocumentRepository

logger = logging.getLogger(__name__)

class ProjectManager:
    """Manages projects and their chats"""
    
    def __init__(self, project_repo: ProjectRepository, chat_repo: ChatRepository, document_repo: Optional[DocumentRepository] = None):
        """
        Initialize the project manager
        
        Args:
            project_repo: Repository for project operations
            chat_repo: Repository for chat operations
            document_repo: Repository for document operations (optional)
        """
        self.project_repo = project_repo
        self.chat_repo = chat_repo
        self.document_repo = document_repo
    
    def create_project(self, name: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new project
        
        Args:
            name: Project name
            custom_prompt: Optional custom system prompt
            
        Returns:
            Project data if successful
        """
        try:
            project = self.project_repo.create_project(
                name=name,
                custom_prompt=custom_prompt
            )
            
            # Create an initial chat for this project
            chat = self.chat_repo.create_chat(
                name="Chat 1",
                project_id=project["id"]
            )
            
            logger.info(f"Created project '{name}' with initial chat")
            return project
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise
    
    def update_project(self, project_id: int, name: Optional[str] = None, 
                      custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a project
        
        Args:
            project_id: ID of project to update
            name: New project name (if provided)
            custom_prompt: New custom prompt (if provided)
            
        Returns:
            Updated project data if successful
        """
        try:
            project = self.project_repo.update_project(
                project_id=project_id,
                name=name,
                custom_prompt=custom_prompt
            )
            
            logger.info(f"Updated project {project_id}")
            return project
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            raise
    
    def delete_project(self, project_id: int) -> bool:
        """
        Delete a project and all its chats, but preserve its documents
        
        Args:
            project_id: ID of project to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First detach any documents associated with this project
            if self.document_repo:
                try:
                    # Get all documents associated with this project
                    project_documents = self.project_repo.get_project_documents(project_id)
                    
                    # Detach each document from the project
                    for doc in project_documents:
                        try:
                            self.document_repo.detach_from_project(doc['id'], project_id)
                            logger.info(f"Detached document {doc['id']} from project {project_id} before deletion")
                        except Exception as e:
                            logger.warning(f"Error detaching document {doc['id']} from project {project_id}: {e}")
                except Exception as e:
                    logger.warning(f"Error retrieving project documents for detachment: {e}")
            
            # This will cascade delete all chats due to FK constraints
            result = self.project_repo.delete_project(project_id)
            
            if result:
                logger.info(f"Deleted project {project_id}")
            else:
                logger.warning(f"Project {project_id} not found for deletion")
            
            return result
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return False
    
    def create_chat(self, project_id: int, name: str) -> Dict[str, Any]:
        """
        Create a new chat in a project
        
        Args:
            project_id: ID of project to create chat in
            name: Chat name
            
        Returns:
            Chat data if successful
        """
        try:
            chat = self.chat_repo.create_chat(
                name=name,
                project_id=project_id
            )
            
            logger.info(f"Created chat '{name}' in project {project_id}")
            return chat
        except Exception as e:
            logger.error(f"Error creating chat: {e}")
            raise
    
    def delete_chat(self, chat_id: int) -> bool:
        """
        Delete a chat
        
        Args:
            chat_id: ID of chat to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.chat_repo.delete_chat(chat_id)
            
            if result:
                logger.info(f"Deleted chat {chat_id}")
            else:
                logger.warning(f"Chat {chat_id} not found for deletion")
                
            return result
        except Exception as e:
            logger.error(f"Error deleting chat: {e}")
            return False
    
    def get_project_chats(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all chats for a project
        
        Args:
            project_id: ID of project to get chats for
            
        Returns:
            List of chats
        """
        return self.project_repo.get_project_chats(project_id)
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects
        
        Returns:
            List of all projects
        """
        return self.project_repo.get_all_projects()
    
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific project by ID
        
        Args:
            project_id: ID of project to retrieve
            
        Returns:
            Project data if found, None otherwise
        """
        return self.project_repo.get_project(project_id)
    
    def get_project_documents(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all documents for a project
        
        Args:
            project_id: ID of project to get documents for
            
        Returns:
            List of documents
        """
        if self.project_repo:
            return self.project_repo.get_project_documents(project_id)
        return []