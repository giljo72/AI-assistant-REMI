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
        from_attributes = True


class ChatMessage(ChatMessageInDB):
    """Schema for chat message responses."""
    
    class Config:
        from_attributes = True


# Chat context settings schema
class ChatContextSettings(BaseModel):
    """Settings for chat context controls."""
    context_mode: str = "standard"
    is_system_prompt_enabled: bool = True
    is_user_prompt_enabled: bool = False
    active_user_prompt_id: Optional[str] = None
    active_user_prompt_name: Optional[str] = None
    is_project_prompt_enabled: bool = True
    is_global_data_enabled: bool = True
    is_project_documents_enabled: bool = True

# Chat schemas
class ChatBase(BaseModel):
    """Base chat schema with common attributes."""
    name: str
    project_id: str
    context_settings: Optional[ChatContextSettings] = None


class ChatCreate(ChatBase):
    """Schema for creating a new chat."""
    pass


class ChatUpdate(BaseModel):
    """Schema for updating an existing chat."""
    name: Optional[str] = None
    context_settings: Optional[ChatContextSettings] = None


class ChatInDB(ChatBase):
    """Schema for chat as stored in the database."""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Chat(ChatInDB):
    """Schema for chat responses."""
    messages: List[ChatMessage] = []
    
    class Config:
        from_attributes = True