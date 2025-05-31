from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import uuid

# Project schemas
class ProjectBase(BaseModel):
    """Base project schema with common attributes."""
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectInDB(ProjectBase):
    """Schema for project as stored in the database."""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Project(ProjectInDB):
    """Schema for project responses."""
    chat_count: int = 0
    document_count: int = 0
    
    class Config:
        from_attributes = True