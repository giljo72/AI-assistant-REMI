from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import uuid4

from .base_repository import BaseRepository
from ..models.chat import Chat, ChatMessage
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

    def create_message(self, db: Session, *, obj_in: ChatMessageCreate) -> ChatMessage:
        """
        Create a new chat message.
        """
        # Ensure the chat exists
        chat = db.query(Chat).filter(Chat.id == obj_in.chat_id).first()
        if not chat:
            raise ValueError(f"Chat with ID {obj_in.chat_id} not found")
        
        db_obj = ChatMessage(
            id=str(uuid4()),
            content=obj_in.content,
            is_user=obj_in.is_user,
            chat_id=obj_in.chat_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
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