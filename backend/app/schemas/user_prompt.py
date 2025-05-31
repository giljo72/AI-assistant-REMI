from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

# User Prompt schemas
class UserPromptBase(BaseModel):
    """Base user prompt schema with common attributes."""
    name: str
    content: str
    project_id: Optional[str] = None


class UserPromptCreate(UserPromptBase):
    """Schema for creating a new user prompt."""
    pass


class UserPromptUpdate(BaseModel):
    """Schema for updating an existing user prompt."""
    name: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None
    project_id: Optional[str] = None


class UserPromptInDB(UserPromptBase):
    """Schema for user prompt as stored in the database."""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = False
    
    class Config:
        from_attributes = True


class UserPrompt(UserPromptInDB):
    """Schema for user prompt responses."""
    
    class Config:
        from_attributes = True