from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class UserPreferencesBase(BaseModel):
    active_prompt_ids: List[str] = []
    active_document_ids: List[str] = []
    ui_settings: Dict[str, Any] = {}
    preferred_model: Optional[str] = None
    model_settings: Dict[str, Any] = {}


class UserPreferencesCreate(UserPreferencesBase):
    user_id: str
    project_id: str


class UserPreferencesUpdate(UserPreferencesBase):
    active_prompt_ids: Optional[List[str]] = None
    active_document_ids: Optional[List[str]] = None
    ui_settings: Optional[Dict[str, Any]] = None
    preferred_model: Optional[str] = None
    model_settings: Optional[Dict[str, Any]] = None


class UserPreferencesResponse(UserPreferencesBase):
    id: UUID
    user_id: str
    project_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True