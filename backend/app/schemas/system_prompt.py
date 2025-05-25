"""
Pydantic schemas for System Prompts
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class SystemPromptBase(BaseModel):
    """Base schema for system prompts"""
    name: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)


class SystemPromptCreate(SystemPromptBase):
    """Schema for creating a system prompt"""
    pass


class SystemPromptUpdate(BaseModel):
    """Schema for updating a system prompt"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)


class SystemPromptInDB(SystemPromptBase):
    """Schema for system prompt from database"""
    id: UUID
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SystemPromptResponse(SystemPromptInDB):
    """Schema for system prompt API response"""
    pass


class SystemPromptActivate(BaseModel):
    """Schema for activating a system prompt"""
    prompt_id: UUID