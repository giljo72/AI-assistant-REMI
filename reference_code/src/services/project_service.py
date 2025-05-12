# src/services/project_service.py
import logging
from typing import List, Dict, Any, Optional, Tuple

from ..chat.project_manager import ProjectManager
from ..chat.chat_manager import ChatManager
from .service_factory import service_factory

logger = logging.getLogger(__name__)

class ProjectService:
    """Service for project and chat operations with the UI"""
    
    def __init__(self):
        """Initialize the project service"""
        # Get dependencies from service factory
        self.project_manager = service_factory.get_service('project_manager')
        self.chat_manager = service_factory.get_service('chat_manager')
        self.file_manager = service_factory.get_service('file_manager')
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects with their chats
        
        Returns:
            List of projects with nested chat lists
        """
        try:
            # Get all projects
            projects = self.project_manager.get_all_projects()
            
            # Enrich with chat information
            for project in projects:
                chats = self.project_manager.get_project_chats(project['id'])
                project['chats'] = chats
                
                # Get document count if file_manager is available
                try:
                    if hasattr(self.project_manager, 'get_project_documents'):
                        project_docs = self.project_manager.get_project_documents(project['id'])
                        project['document_count'] = len(project_docs)
                    else:
                        project['document_count'] = 0
                except Exception as e:
                    logger.error(f"Error getting document count for project {project['id']}: {e}")
                    project['document_count'] = 0
            
            return projects
        except Exception as e:
            logger.error(f"Error getting all projects: {e}")
            return []
    
    def create_project(self, name: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new project
        
        Args:
            name: Project name
            custom_prompt: Optional custom system prompt
            
        Returns:
            New project data with nested chats
        """
        try:
            # Create the project
            project = self.project_manager.create_project(name, custom_prompt)
            
            # Get the initial chat that was created with the project
            chats = self.project_manager.get_project_chats(project['id'])
            project['chats'] = chats
            project['document_count'] = 0
            
            logger.info(f"Created project '{name}' with ID {project['id']}")
            return project
        except Exception as e:
            logger.error(f"Error creating project: {e}")
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
            Updated project data
        """
        try:
            # Update the project
            project = self.project_manager.update_project(project_id, name, custom_prompt)
            
            # Get chats for the project
            chats = self.project_manager.get_project_chats(project_id)
            project['chats'] = chats
            
            # Get document count
            try:
                if hasattr(self.project_manager, 'get_project_documents'):
                    project_docs = self.project_manager.get_project_documents(project_id)
                    project['document_count'] = len(project_docs)
                else:
                    project['document_count'] = 0
            except Exception as e:
                logger.error(f"Error getting document count for project {project_id}: {e}")
                project['document_count'] = 0
            
            logger.info(f"Updated project ID {project_id}")
            return project
        except Exception as e:
            logger.error(f"Error updating project: {e}")
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
            # Delete the project (cascades to chats)
            success = self.project_manager.delete_project(project_id)
            
            if success:
                logger.info(f"Deleted project ID {project_id}")
            else:
                logger.warning(f"Failed to delete project ID {project_id}")
                
            return success
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return False
    
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a project by ID with its chats
        
        Args:
            project_id: ID of project to retrieve
            
        Returns:
            Project data with nested chats if found, None otherwise
        """
        try:
            # Get the project
            project = self.project_manager.get_project(project_id)
            
            if not project:
                return None
                
            # Get chats for the project
            chats = self.project_manager.get_project_chats(project_id)
            project['chats'] = chats
            
            # Get document count
            try:
                if hasattr(self.project_manager, 'get_project_documents'):
                    project_docs = self.project_manager.get_project_documents(project_id)
                    project['document_count'] = len(project_docs)
                else:
                    project['document_count'] = 0
            except Exception as e:
                logger.error(f"Error getting document count for project {project_id}: {e}")
                project['document_count'] = 0
            
            return project
        except Exception as e:
            logger.error(f"Error getting project: {e}")
            return None
    
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
            # Create the chat
            chat = self.project_manager.create_chat(project_id, name)
            
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
            # Delete the chat
            success = self.project_manager.delete_chat(chat_id)
            
            if success:
                logger.info(f"Deleted chat ID {chat_id}")
            else:
                logger.warning(f"Failed to delete chat ID {chat_id}")
                
            return success
        except Exception as e:
            logger.error(f"Error deleting chat: {e}")
            return False
    
    def rename_chat(self, chat_id: int, name: str) -> Dict[str, Any]:
        """
        Rename a chat
        
        Args:
            chat_id: ID of chat to rename
            name: New chat name
            
        Returns:
            Updated chat data if successful
        """
        try:
            # Get the chat
            chat = self.chat_manager.get_chat(chat_id)
            
            if not chat:
                raise ValueError(f"Chat ID {chat_id} not found")
                
            # Update the chat name
            updated_chat = self.chat_manager.update_chat_name(chat_id, name)
            
            logger.info(f"Renamed chat ID {chat_id} to '{name}'")
            return updated_chat
        except Exception as e:
            logger.error(f"Error renaming chat: {e}")
            raise
    
    def get_chat_messages(self, chat_id: int) -> List[Dict[str, Any]]:
        """
        Get all messages for a chat
        
        Args:
            chat_id: ID of chat to get messages for
            
        Returns:
            List of chat messages
        """
        try:
            # Get messages for the chat
            messages = self.chat_manager.get_chat_messages(chat_id)
            
            return messages
        except Exception as e:
            logger.error(f"Error getting chat messages: {e}")
            return []
    
    def attach_documents_to_project(self, project_id: int, document_ids: List[int]) -> Tuple[int, List[int]]:
        """
        Attach documents to a project
        
        Args:
            project_id: ID of project to attach documents to
            document_ids: List of document IDs to attach
            
        Returns:
            Tuple of (success count, list of failed document IDs)
        """
        success_count = 0
        failed_ids = []
        
        for doc_id in document_ids:
            try:
                # Check if document is already attached to the project
                if self.file_manager.is_document_in_project(doc_id, project_id):
                    # Already attached, count as success
                    success_count += 1
                    continue
                    
                # Attach document to project
                success = self.file_manager.attach_to_project(doc_id, project_id)
                
                if success:
                    success_count += 1
                else:
                    failed_ids.append(doc_id)
            except Exception as e:
                logger.error(f"Error attaching document {doc_id} to project {project_id}: {e}")
                failed_ids.append(doc_id)
        
        logger.info(f"Attached {success_count} documents to project {project_id}")
        if failed_ids:
            logger.warning(f"Failed to attach {len(failed_ids)} documents to project {project_id}")
            
        return success_count, failed_ids
    
    def detach_documents_from_project(self, project_id: int, document_ids: List[int]) -> Tuple[int, List[int]]:
        """
        Detach documents from a project
        
        Args:
            project_id: ID of project to detach documents from
            document_ids: List of document IDs to detach
            
        Returns:
            Tuple of (success count, list of failed document IDs)
        """
        success_count = 0
        failed_ids = []
        
        for doc_id in document_ids:
            try:
                # Detach document from project
                success = self.file_manager.remove_document_from_project(doc_id, project_id)
                
                if success:
                    success_count += 1
                else:
                    failed_ids.append(doc_id)
            except Exception as e:
                logger.error(f"Error detaching document {doc_id} from project {project_id}: {e}")
                failed_ids.append(doc_id)
        
        logger.info(f"Detached {success_count} documents from project {project_id}")
        if failed_ids:
            logger.warning(f"Failed to detach {len(failed_ids)} documents from project {project_id}")
            
        return success_count, failed_ids
    
    def get_project_documents(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all documents attached to a project
        
        Args:
            project_id: ID of project to get documents for
            
        Returns:
            List of documents attached to the project
        """
        try:
            if hasattr(self.project_manager, 'get_project_documents'):
                # Use project manager if it has the method
                return self.project_manager.get_project_documents(project_id)
            else:
                # Fall back to document repository through file manager
                docs, _ = self.file_manager.get_all_documents(project_id=project_id)
                return docs
        except Exception as e:
            logger.error(f"Error getting project documents: {e}")
            return []
    
    def set_document_context(self, chat_id: int, document_ids: List[int]) -> bool:
        """
        Set the document context for a chat
        
        Args:
            chat_id: ID of chat to set context for
            document_ids: List of document IDs to include in context
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Set document context
            self.chat_manager.set_document_context(chat_id, document_ids)
            
            logger.info(f"Set document context for chat {chat_id}: {document_ids}")
            return True
        except Exception as e:
            logger.error(f"Error setting document context: {e}")
            return False
    
    def get_document_context(self, chat_id: int) -> List[int]:
        """
        Get the document context for a chat
        
        Args:
            chat_id: ID of chat to get context for
            
        Returns:
            List of document IDs in context
        """
        try:
            # Get document context
            return self.chat_manager.get_document_context(chat_id)
        except Exception as e:
            logger.error(f"Error getting document context: {e}")
            return []