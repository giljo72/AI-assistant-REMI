from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from enum import Enum


class VisibilityLevel(str, Enum):
    """Visibility levels for personal profiles"""
    PRIVATE = "private"
    SHARED = "shared"
    GLOBAL = "global"


class PersonalProfileBase(BaseModel):
    """Base schema for personal profile"""
    # Identity
    name: str = Field(..., description="Full name of the person")
    preferred_name: Optional[str] = Field(None, description="Preferred name or nickname")
    
    # Relationship context
    relationship: str = Field(..., description="Type of relationship: colleague, family, friend, client")
    organization: Optional[str] = Field(None, description="Company or organization")
    role: Optional[str] = Field(None, description="Professional role or title")
    
    # Key dates
    birthday: Optional[date] = Field(None, description="Birthday")
    first_met: Optional[date] = Field(None, description="When you first met")
    
    # Communication
    preferred_contact: Optional[str] = Field(None, description="Preferred contact method: email, phone, teams, slack")
    timezone: Optional[str] = Field(None, description="Timezone (e.g., GMT+1, EST)")
    
    # Current context
    current_focus: Optional[str] = Field(None, description="What they're currently working on")
    
    # Free-form notes
    notes: Optional[str] = Field(None, description="Additional notes (markdown supported)")
    
    # Visibility
    visibility: VisibilityLevel = Field(VisibilityLevel.PRIVATE, description="Who can see this profile")
    
    @validator('relationship')
    def validate_relationship(cls, v):
        allowed = ['colleague', 'family', 'friend', 'client', 'acquaintance', 'other']
        if v.lower() not in allowed:
            raise ValueError(f"Relationship must be one of: {', '.join(allowed)}")
        return v.lower()


class PersonalProfileCreate(PersonalProfileBase):
    """Schema for creating a personal profile"""
    pass


class PersonalProfileUpdate(BaseModel):
    """Schema for updating a personal profile"""
    name: Optional[str] = None
    preferred_name: Optional[str] = None
    relationship: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    birthday: Optional[date] = None
    first_met: Optional[date] = None
    preferred_contact: Optional[str] = None
    timezone: Optional[str] = None
    current_focus: Optional[str] = None
    notes: Optional[str] = None
    visibility: Optional[VisibilityLevel] = None
    is_active: Optional[bool] = None


class PersonalProfileInDB(PersonalProfileBase):
    """Schema for personal profile in database"""
    id: UUID
    user_id: str = "default_user"
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonalProfile(PersonalProfileInDB):
    """Schema for personal profile responses"""
    
    def format_for_context(self) -> str:
        """Format profile as context for LLM"""
        context_parts = [f"Person: {self.name}"]
        
        if self.preferred_name and self.preferred_name != self.name:
            context_parts.append(f"Prefers to be called: {self.preferred_name}")
        
        context_parts.append(f"Relationship: {self.relationship}")
        
        if self.organization:
            context_parts.append(f"Organization: {self.organization}")
        if self.role:
            context_parts.append(f"Role: {self.role}")
        
        if self.birthday:
            context_parts.append(f"Birthday: {self.birthday.strftime('%B %d')}")
        
        if self.current_focus:
            context_parts.append(f"Currently focused on: {self.current_focus}")
        
        if self.notes:
            context_parts.append(f"Additional context: {self.notes}")
        
        return "\n".join(context_parts)

    class Config:
        from_attributes = True