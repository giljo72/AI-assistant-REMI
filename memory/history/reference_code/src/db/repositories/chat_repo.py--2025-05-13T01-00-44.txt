# src/db/repositories/chat_repo.py
from typing import List, Dict, Any, Optional
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError
import logging

from ...core.db_interface import get_db_session
from ..models import Chat, Message

logger = logging.getLogger(__name__)

class ChatRepository:
    """Repository for chat operations"""
    
    def create_chat(self, name: str, project_id: int) -> Dict[str, Any]:
        """
        Create a new chat
        
        Args:
            name: Chat name
            project_id: ID of the project this chat belongs to
            
        Returns:
            Chat as dictionary if successful
        """
        try:
            with get_db_session() as session:
                chat = Chat(
                    name=name,
                    project_id=project_id
                )
                
                session.add(chat)
                session.flush()  # To get the ID
                
                logger.info(f"Created chat: {name} in project {project_id} (ID: {chat.id})")
                
                # Make a copy to return, as the session will be closed
                result = {
                    'id': chat.id,
                    'name': chat.name,
                    'project_id': chat.project_id,
                    'created_at': chat.created_at,
                    'updated_at': chat.updated_at
                }
                
                return result
        except SQLAlchemyError as e:
            logger.error(f"Database error creating chat: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating chat: {e}")
            raise
    
    def update_chat(self, chat_id: int, name: str) -> Dict[str, Any]:
        """
        Update a chat
        
        Args:
            chat_id: ID of chat to update
            name: New chat name
            
        Returns:
            Updated chat as dictionary if successful
        """
        try:
            with get_db_session() as session:
                # Update the chat
                stmt = (
                    update(Chat)
                    .where(Chat.id == chat_id)
                    .values(name=name)
                    .returning(Chat)
                )
                
                result = session.execute(stmt).scalar_one_or_none()
                
                if result:
                    logger.info(f"Updated chat ID {chat_id}")
                    
                    # Convert to dictionary
                    return {
                        'id': result.id,
                        'name': result.name,
                        'project_id': result.project_id,
                        'created_at': result.created_at,
                        'updated_at': result.updated_at
                    }
                else:
                    logger.warning(f"Chat ID {chat_id} not found for update")
                    raise ValueError(f"Chat ID {chat_id} not found")
        except SQLAlchemyError as e:
            logger.error(f"Database error updating chat: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating chat: {e}")
            raise
    
    def delete_chat(self, chat_id: int) -> bool:
        """
        Delete a chat and all its messages
        
        Args:
            chat_id: ID of chat to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_session() as session:
                # Delete the chat (cascades to messages)
                stmt = delete(Chat).where(Chat.id == chat_id)
                result = session.execute(stmt)
                
                if result.rowcount > 0:
                    logger.info(f"Deleted chat ID {chat_id}")
                    return True
                else:
                    logger.warning(f"Chat ID {chat_id} not found for deletion")
                    return False
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting chat: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting chat: {e}")
            return False
    
    def get_chat(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a chat by ID
        
        Args:
            chat_id: ID of chat to retrieve
            
        Returns:
            Chat as dictionary if found, None otherwise
        """
        try:
            with get_db_session() as session:
                stmt = select(Chat).where(Chat.id == chat_id)
                result = session.execute(stmt).scalar_one_or_none()
                
                if result:
                    return {
                        'id': result.id,
                        'name': result.name,
                        'project_id': result.project_id,
                        'created_at': result.created_at,
                        'updated_at': result.updated_at
                    }
                else:
                    logger.warning(f"Chat ID {chat_id} not found")
                    return None
        except SQLAlchemyError as e:
            logger.error(f"Database error getting chat: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting chat: {e}")
            return None
    
    def add_message(self, chat_id: int, role: str, content: str) -> Dict[str, Any]:
        """
        Add a message to a chat
        
        Args:
            chat_id: ID of chat to add message to
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Returns:
            Message as dictionary if successful
        """
        try:
            with get_db_session() as session:
                message = Message(
                    chat_id=chat_id,
                    role=role,
                    content=content
                )
                
                session.add(message)
                session.flush()  # To get the ID
                
                logger.info(f"Added {role} message to chat {chat_id} (ID: {message.id})")
                
                # Make a copy to return, as the session will be closed
                result = {
                    'id': message.id,
                    'chat_id': message.chat_id,
                    'role': message.role,
                    'content': message.content,
                    'created_at': message.created_at
                }
                
                return result
        except SQLAlchemyError as e:
            logger.error(f"Database error adding message: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding message: {e}")
            raise
    
    def get_chat_messages(self, chat_id: int) -> List[Dict[str, Any]]:
        """
        Get all messages for a chat
        
        Args:
            chat_id: ID of chat to get messages for
            
        Returns:
            List of messages as dictionaries
        """
        try:
            with get_db_session() as session:
                stmt = select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)
                results = session.execute(stmt).scalars().all()
                
                # Convert to dictionaries
                messages = []
                for msg in results:
                    messages.append({
                        'id': msg.id,
                        'chat_id': msg.chat_id,
                        'role': msg.role,
                        'content': msg.content,
                        'created_at': msg.created_at
                    })
                
                return messages
        except SQLAlchemyError as e:
            logger.error(f"Database error getting chat messages: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting chat messages: {e}")
            return []