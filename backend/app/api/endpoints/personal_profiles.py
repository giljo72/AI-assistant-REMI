from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.db.repositories.personal_profile_repository import personal_profile_repository
from app.schemas.personal_profile import (
    PersonalProfile,
    PersonalProfileCreate,
    PersonalProfileUpdate,
    VisibilityLevel
)

router = APIRouter()


@router.get("/", response_model=List[PersonalProfile])
def get_personal_profiles(
    db: Session = Depends(get_db),
    user_id: str = Query("default_user", description="User ID (defaulting to 'default_user' for now)"),
    include_global: bool = Query(False, description="Include globally visible profiles"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all personal profiles for a user."""
    profiles = personal_profile_repository.get_by_user(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
        include_global=include_global
    )
    return profiles


@router.get("/search", response_model=List[PersonalProfile])
def search_profiles(
    query: str = Query(..., description="Search query"),
    db: Session = Depends(get_db),
    user_id: str = Query("default_user", description="User ID"),
    include_shared: bool = Query(True, description="Include shared profiles"),
    include_global: bool = Query(True, description="Include global profiles")
):
    """Search personal profiles by name, organization, role, or notes."""
    profiles = personal_profile_repository.search_profiles(
        db=db,
        query=query,
        user_id=user_id,
        include_shared=include_shared,
        include_global=include_global
    )
    return profiles


@router.get("/context", response_model=List[PersonalProfile])
def get_profiles_for_context(
    db: Session = Depends(get_db),
    user_id: str = Query("default_user", description="User ID"),
    project_id: Optional[str] = Query(None, description="Project ID"),
    include_global: bool = Query(True, description="Include global profiles")
):
    """Get profiles that should be included in chat context."""
    profiles = personal_profile_repository.get_profiles_for_context(
        db=db,
        user_id=user_id,
        project_id=project_id,
        include_global=include_global
    )
    return profiles


@router.get("/{profile_id}", response_model=PersonalProfile)
def get_personal_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Query("default_user", description="User ID")
):
    """Get a specific personal profile."""
    profile = personal_profile_repository.get(db, id=profile_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal profile not found"
        )
    
    # Check access permissions
    if profile.user_id != user_id and profile.visibility == VisibilityLevel.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this profile"
        )
    
    return profile


@router.post("/", response_model=PersonalProfile)
def create_personal_profile(
    profile: PersonalProfileCreate,
    db: Session = Depends(get_db),
    user_id: str = Query("default_user", description="User ID")
):
    """Create a new personal profile."""
    db_profile = personal_profile_repository.create_with_user(
        db=db,
        obj_in=profile,
        user_id=user_id
    )
    return db_profile


@router.put("/{profile_id}", response_model=PersonalProfile)
def update_personal_profile(
    profile_id: UUID,
    profile_update: PersonalProfileUpdate,
    db: Session = Depends(get_db),
    user_id: str = Query("default_user", description="User ID")
):
    """Update a personal profile."""
    db_profile = personal_profile_repository.get(db, id=profile_id)
    
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal profile not found"
        )
    
    # Check ownership
    if db_profile.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profiles"
        )
    
    db_profile = personal_profile_repository.update(
        db=db,
        db_obj=db_profile,
        obj_in=profile_update
    )
    
    return db_profile


@router.delete("/{profile_id}")
def delete_personal_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Query("default_user", description="User ID")
):
    """Delete a personal profile (soft delete)."""
    db_profile = personal_profile_repository.get(db, id=profile_id)
    
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal profile not found"
        )
    
    # Check ownership
    if db_profile.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own profiles"
        )
    
    # Soft delete by setting is_active to False
    update_data = PersonalProfileUpdate(is_active=False)
    personal_profile_repository.update(db=db, db_obj=db_profile, obj_in=update_data)
    
    return {"message": "Personal profile deleted successfully"}


@router.get("/formatted/{profile_id}")
def get_formatted_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Query("default_user", description="User ID")
):
    """Get a profile formatted for LLM context."""
    profile = personal_profile_repository.get(db, id=profile_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal profile not found"
        )
    
    # Check access permissions
    if profile.user_id != user_id and profile.visibility == VisibilityLevel.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this profile"
        )
    
    # Convert to schema and format
    profile_schema = PersonalProfile.from_orm(profile)
    
    return {
        "profile_id": str(profile.id),
        "name": profile.name,
        "formatted_context": profile_schema.format_for_context()
    }