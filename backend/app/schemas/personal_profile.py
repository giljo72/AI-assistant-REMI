from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID


class PersonalProfileBase(BaseModel):
    name: str
    role: Optional[str] = None
    custom_fields: List[Dict[str, str]] = []
    is_default: bool = False
    is_private: bool = True
    shared_with_team: bool = False


class PersonalProfileCreate(PersonalProfileBase):
    user_id: str


class PersonalProfileUpdate(PersonalProfileBase):
    name: Optional[str] = None
    is_default: Optional[bool] = None


class PersonalProfileResponse(PersonalProfileBase):
    id: UUID
    user_id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True