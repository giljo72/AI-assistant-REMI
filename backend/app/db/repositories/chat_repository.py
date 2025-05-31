from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import uuid4

from .base_repository import BaseRepository
from ..models.chat import Chat, ChatMessage
from ..models.message_context import MessageContext
from ...schemas.chat import ChatCreate, ChatUpdate, ChatMessageCreate

class ChatRepository(BaseRepository[Chat, ChatCreate, ChatUpdate]):
    """Repository for managing chats."""
    
    def get_multi_by_project(
        self, db: Session, *, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[Chat]:
        """
        Get multiple chats by project ID.
        """
        return db.query(self.model)\
                .filter(self.model.project_id == project_id)\
                .order_by(self.model.created_at.desc())\
                .offset(skip)\
                .limit(limit)\
                .all()

    def create_message(self, db: Session, *, obj_in: ChatMessageCreate, context_data: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """
        Create a new chat message with optional context tracking.
        """
        # Ensure the chat exists
        chat = db.query(Chat).filter(Chat.id == obj_in.chat_id).first()
        if not chat:
            raise ValueError(f"Chat with ID {obj_in.chat_id} not found")
        
        db_obj = ChatMessage(
            id=str(uuid4()),
            content=obj_in.content,
            is_user=obj_in.is_user,
            chat_id=obj_in.chat_id,
            model_info=obj_in.model_info if hasattr(obj_in, 'model_info') else None
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Create message context if provided
        if context_data and not obj_in.is_user:  # Only track context for assistant messages
            message_context = MessageContext(
                message_id=db_obj.id,
                active_prompt_ids=context_data.get("active_prompt_ids", []),
                active_document_ids=context_data.get("active_document_ids", []),
                personal_profile_id=context_data.get("personal_profile_id"),
                model_name=context_data.get("model_name", "unknown"),
                model_settings=context_data.get("model_settings", {}),
                system_prompt=context_data.get("system_prompt"),
                user_prompts=context_data.get("user_prompts", []),
                document_chunks=context_data.get("document_chunks", [])
            )
            db.add(message_context)
            db.commit()
        
        return db_obj
    
    def get_chat_messages(
        self, db: Session, *, chat_id: str, skip: int = 0, limit: int = 100
    ) -> List[ChatMessage]:
        """
        Get messages for a specific chat.
        """
        return db.query(ChatMessage)\
                .filter(ChatMessage.chat_id == chat_id)\
                .order_by(ChatMessage.created_at.asc())\
                .offset(skip)\
                .limit(limit)\
                .all()
                
                
chat_repository = ChatRepository(Chat)