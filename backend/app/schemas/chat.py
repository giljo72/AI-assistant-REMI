from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

# Chat Message schemas
class ChatMessageBase(BaseModel):
    """Base chat message schema with common attributes."""
    content: str
    is_user: bool = True


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message."""
    chat_id: str


class ChatMessageInDB(ChatMessageBase):
    """Schema for chat message as stored in the database."""
    id: str
    chat_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True


class ChatMessage(ChatMessageInDB):
    """Schema for chat message responses."""
    
    class Config:
        orm_mode = True


# Chat schemas
class ChatBase(BaseModel):
    """Base chat schema with common attributes."""
    name: str
    project_id: str


class ChatCreate(ChatBase):
    """Schema for creating a new chat."""
    pass


class ChatUpdate(BaseModel):
    """Schema for updating an existing chat."""
    name: Optional[str] = None


class ChatInDB(ChatBase):
    """Schema for chat as stored in the database."""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class Chat(ChatInDB):
    """Schema for chat responses."""
    messages: List[ChatMessage] = []
    
    class Config:
        orm_mode = True