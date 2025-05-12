# src/chat/chat_manager.py
from typing import List, Dict, Any, Optional, Tuple
import logging

from ..db.repositories.chat_repo import ChatRepository
from ..rag.generation import ResponseGenerator

logger = logging.getLogger(__name__)

class ChatManager:
    """Manages chats and their messages"""
    
    def __init__(self, 
                chat_repo: ChatRepository,
                response_generator: ResponseGenerator):
        """
        Initialize the chat manager
        
        Args:
            chat_repo: Repository for chat operations
            response_generator: Generator for LLM responses
        """
        self.chat_repo = chat_repo
        self.response_generator = response_generator
        self.document_contexts = {}  # Store document selections for each chat
    
    def get_chat(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a chat by ID
        
        Args:
            chat_id: ID of chat to retrieve
            
        Returns:
            Chat data if found, None otherwise
        """
        return self.chat_repo.get_chat(chat_id)
    
    def update_chat_name(self, chat_id: int, name: str) -> Dict[str, Any]:
        """
        Update a chat's name
        
        Args:
            chat_id: ID of chat to update
            name: New chat name
            
        Returns:
            Updated chat data if successful
        """
        return self.chat_repo.update_chat(chat_id, name)
    
    def add_user_message(self, chat_id: int, content: str) -> Dict[str, Any]:
        """
        Add a user message to a chat
        
        Args:
            chat_id: ID of chat to add message to
            content: Message content
            
        Returns:
            Message data if successful
        """
        return self.chat_repo.add_message(chat_id, "user", content)
    
    def add_assistant_message(self, chat_id: int, content: str) -> Dict[str, Any]:
        """
        Add an assistant message to a chat
        
        Args:
            chat_id: ID of chat to add message to
            content: Message content
            
        Returns:
            Message data if successful
        """
        return self.chat_repo.add_message(chat_id, "assistant", content)
    
    def get_chat_messages(self, chat_id: int) -> List[Dict[str, Any]]:
        """
        Get all messages for a chat
        
        Args:
            chat_id: ID of chat to get messages for
            
        Returns:
            List of messages
        """
        return self.chat_repo.get_chat_messages(chat_id)
    
    def set_document_context(self, chat_id: int, document_ids: List[int]) -> None:
        """
        Set the document context for a chat
        
        Args:
            chat_id: ID of chat to set context for
            document_ids: List of document IDs to include in context
        """
        self.document_contexts[chat_id] = document_ids
        logger.info(f"Set document context for chat {chat_id}: {document_ids}")
    
    def get_document_context(self, chat_id: int) -> List[int]:
        """
        Get the document context for a chat
        
        Args:
            chat_id: ID of chat to get context for
            
        Returns:
            List of document IDs in context
        """
        return self.document_contexts.get(chat_id, [])
    
    def process_user_message(self, 
                           chat_id: int, 
                           content: str, 
                           temperature: float = 0.7) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process a user message and generate a response
        
        Args:
            chat_id: ID of chat to process message for
            content: Message content
            temperature: Temperature for response generation
            
        Returns:
            Tuple of (assistant message, metadata)
        """
        # Get chat info for project ID
        chat = self.chat_repo.get_chat(chat_id)
        if not chat:
            logger.error(f"Chat {chat_id} not found")
            raise ValueError(f"Chat {chat_id} not found")
        
        project_id = chat.get('project_id')
        
        # Add user message to chat
        user_message = self.add_user_message(chat_id, content)
        
        # Get chat history for context
        chat_history = self.get_chat_messages(chat_id)
        
        # Get document context if available
        document_ids = self.get_document_context(chat_id)
        
        # Generate response
        response_text, metadata = self.response_generator.generate_response(
            query=content,
            project_id=project_id,
            chat_history=chat_history,
            temperature=temperature,
            document_ids=document_ids  # Pass selected document IDs
        )
        
        # Add assistant message to chat
        assistant_message = self.add_assistant_message(chat_id, response_text)
        
        return assistant_message, metadata