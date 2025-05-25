from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.db.models.user_preferences import UserPreferences
from app.schemas.user_preferences import (
    UserPreferencesCreate,
    UserPreferencesUpdate,
    UserPreferencesResponse
)

router = APIRouter()


@router.get("/project/{project_id}", response_model=UserPreferencesResponse)
def get_user_preferences(
    project_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user preferences for a specific project."""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.project_id == project_id,
        UserPreferences.user_id == user_id
    ).first()
    
    if not preferences:
        # Create default preferences if none exist
        preferences = UserPreferences(
            user_id=user_id,
            project_id=project_id
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    return preferences


@router.put("/project/{project_id}", response_model=UserPreferencesResponse)
def update_user_preferences(
    project_id: str,
    user_id: str,
    preferences_update: UserPreferencesUpdate,
    db: Session = Depends(get_db)
):
    """Update user preferences for a specific project."""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.project_id == project_id,
        UserPreferences.user_id == user_id
    ).first()
    
    if not preferences:
        # Create new preferences if none exist
        preferences = UserPreferences(
            user_id=user_id,
            project_id=project_id
        )
        db.add(preferences)
    
    # Update fields
    update_data = preferences_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)
    
    db.commit()
    db.refresh(preferences)
    
    return preferences


@router.post("/project/{project_id}/prompts/{prompt_id}")
def toggle_prompt_active(
    project_id: str,
    prompt_id: str,
    user_id: str,
    active: bool = True,
    db: Session = Depends(get_db)
):
    """Toggle a prompt as active/inactive for a project."""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.project_id == project_id,
        UserPreferences.user_id == user_id
    ).first()
    
    if not preferences:
        preferences = UserPreferences(
            user_id=user_id,
            project_id=project_id,
            active_prompt_ids=[]
        )
        db.add(preferences)
    
    # Update active prompts list
    if active and prompt_id not in preferences.active_prompt_ids:
        preferences.active_prompt_ids.append(prompt_id)
    elif not active and prompt_id in preferences.active_prompt_ids:
        preferences.active_prompt_ids.remove(prompt_id)
    
    db.commit()
    
    return {"message": f"Prompt {'activated' if active else 'deactivated'} successfully"}


@router.post("/project/{project_id}/documents/{document_id}")
def toggle_document_active(
    project_id: str,
    document_id: str,
    user_id: str,
    active: bool = True,
    db: Session = Depends(get_db)
):
    """Toggle a document as active/inactive for a project."""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.project_id == project_id,
        UserPreferences.user_id == user_id
    ).first()
    
    if not preferences:
        preferences = UserPreferences(
            user_id=user_id,
            project_id=project_id,
            active_document_ids=[]
        )
        db.add(preferences)
    
    # Update active documents list
    if active and document_id not in preferences.active_document_ids:
        preferences.active_document_ids.append(document_id)
    elif not active and document_id in preferences.active_document_ids:
        preferences.active_document_ids.remove(document_id)
    
    db.commit()
    
    return {"message": f"Document {'activated' if active else 'deactivated'} successfully"}