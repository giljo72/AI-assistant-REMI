# src/services/chat_service.py
import logging
from typing import List, Dict, Any, Optional, Tuple

from ..chat.chat_manager import ChatManager
from .service_factory import service_factory

logger = logging.getLogger(__name__)

class ChatService:
    """Service for chat operations with the UI"""
    
    def __init__(self):
        """Initialize the chat service"""
        # Get dependencies from service factory
        self.chat_manager = service_factory.get_service('chat_manager')
        self.file_manager = service_factory.get_service('file_manager')
    
    def get_chat(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a chat by ID
        
        Args:
            chat_id: ID of chat to retrieve
            
        Returns:
            Chat data if found, None otherwise
        """
        try:
            return self.chat_manager.get_chat(chat_id)
        except Exception as e:
            logger.error(f"Error getting chat {chat_id}: {e}")
            return None
    
    def get_chat_messages(self, chat_id: int) -> List[Dict[str, Any]]:
        """
        Get all messages for a chat
        
        Args:
            chat_id: ID of chat to get messages for
            
        Returns:
            List of chat messages
        """
        try:
            # Get messages from the chat manager
            messages = self.chat_manager.get_chat_messages(chat_id)
            
            # Format messages for Gradio Chatbot component (role, content format)
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            return formatted_messages
        except Exception as e:
            logger.error(f"Error getting chat messages: {e}")
            return []
    
    def add_user_message(self, chat_id: int, content: str) -> Dict[str, Any]:
        """
        Add a user message to a chat
        
        Args:
            chat_id: ID of chat to add message to
            content: Message content
            
        Returns:
            Message data if successful
        """
        try:
            # Add message to chat
            message = self.chat_manager.add_user_message(chat_id, content)
            
            logger.info(f"Added user message to chat {chat_id}")
            return message
        except Exception as e:
            logger.error(f"Error adding user message: {e}")
            raise
    
    def process_user_message(self, 
                           chat_id: int, 
                           content: str, 
                           temperature: float = 0.7,
                           memory_scope: str = "project") -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process a user message and generate a response
        
        Args:
            chat_id: ID of chat to process message for
            content: Message content
            temperature: Temperature for response generation
            memory_scope: Memory scope ('project', 'global', 'all')
            
        Returns:
            Tuple of (assistant message, metadata)
        """
        try:
            # Add and process the message using chat manager
            assistant_message, metadata = self.chat_manager.process_user_message(
                chat_id=chat_id,
                content=content,
                temperature=temperature
            )
            
            logger.info(f"Processed message for chat {chat_id} with scope: {memory_scope}")
            return assistant_message, metadata
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            
            # Return error message
            error_msg = {
                "id": 0,
                "chat_id": chat_id,
                "role": "assistant",
                "content": f"Sorry, I encountered an error while processing your message: {str(e)}. Please try again or contact support if the issue persists."
            }
            
            return error_msg, {"error": str(e)}
    
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
            return self.chat_manager.get_document_context(chat_id)
        except Exception as e:
            logger.error(f"Error getting document context: {e}")
            return []
    
    def update_chat_name(self, chat_id: int, name: str) -> Dict[str, Any]:
        """
        Update a chat's name
        
        Args:
            chat_id: ID of chat to update
            name: New chat name
            
        Returns:
            Updated chat data if successful
        """
        try:
            # Update chat name
            updated_chat = self.chat_manager.update_chat_name(chat_id, name)
            
            logger.info(f"Updated chat {chat_id} name to '{name}'")
            return updated_chat
        except Exception as e:
            logger.error(f"Error updating chat name: {e}")
            raise
    
    def get_documents_for_chat(self, chat_id: int) -> List[Dict[str, Any]]:
        """
        Get documents associated with a chat's context
        
        Args:
            chat_id: ID of chat to get documents for
            
        Returns:
            List of documents in context
        """
        try:
            # Get document IDs from chat context
            document_ids = self.chat_manager.get_document_context(chat_id)
            
            if not document_ids:
                return []
                
            # Get document details
            documents = []
            for doc_id in document_ids:
                # Get document metadata
                doc = self.file_manager.document_repo.get_document(doc_id)
                if doc:
                    documents.append(doc)
            
            return documents
        except Exception as e:
            logger.error(f"Error getting documents for chat: {e}")
            return []
    
    def update_memory_scope(self, chat_id: int, memory_scope: str) -> bool:
        """
        Update the memory scope for a chat
        
        Args:
            chat_id: ID of chat to update
            memory_scope: Memory scope ('project', 'global', 'all')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This is a placeholder - in a real implementation, this would
            # update a setting in the database for the current chat
            # For now, we'll just log it
            logger.info(f"Updated memory scope for chat {chat_id} to '{memory_scope}'")
            return True
        except Exception as e:
            logger.error(f"Error updating memory scope: {e}")
            return False