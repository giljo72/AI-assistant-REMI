from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.db.models.personal_profile import PersonalProfile
from app.schemas.personal_profile import (
    PersonalProfileCreate,
    PersonalProfileUpdate,
    PersonalProfileResponse
)

router = APIRouter()


@router.get("/", response_model=List[PersonalProfileResponse])
def get_personal_profiles(
    user_id: str,
    include_shared: bool = False,
    db: Session = Depends(get_db)
):
    """Get all personal profiles for a user."""
    query = db.query(PersonalProfile).filter(
        PersonalProfile.is_active == True
    )
    
    if include_shared:
        # Include profiles shared with team
        query = query.filter(
            (PersonalProfile.user_id == user_id) | 
            (PersonalProfile.shared_with_team == True)
        )
    else:
        # Only user's own profiles
        query = query.filter(PersonalProfile.user_id == user_id)
    
    profiles = query.all()
    return profiles


@router.get("/{profile_id}", response_model=PersonalProfileResponse)
def get_personal_profile(
    profile_id: UUID,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific personal profile."""
    profile = db.query(PersonalProfile).filter(
        PersonalProfile.id == profile_id,
        PersonalProfile.is_active == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal profile not found"
        )
    
    # Check access permissions
    if profile.user_id != user_id and not profile.shared_with_team:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this profile"
        )
    
    return profile


@router.post("/", response_model=PersonalProfileResponse)
def create_personal_profile(
    profile: PersonalProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new personal profile."""
    # If this is the first profile for the user, make it default
    existing_profiles = db.query(PersonalProfile).filter(
        PersonalProfile.user_id == profile.user_id,
        PersonalProfile.is_active == True
    ).count()
    
    if existing_profiles == 0:
        profile.is_default = True
    elif profile.is_default:
        # If setting as default, unset other defaults
        db.query(PersonalProfile).filter(
            PersonalProfile.user_id == profile.user_id,
            PersonalProfile.is_active == True
        ).update({"is_default": False})
    
    db_profile = PersonalProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile


@router.put("/{profile_id}", response_model=PersonalProfileResponse)
def update_personal_profile(
    profile_id: UUID,
    profile_update: PersonalProfileUpdate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Update a personal profile."""
    db_profile = db.query(PersonalProfile).filter(
        PersonalProfile.id == profile_id,
        PersonalProfile.user_id == user_id,
        PersonalProfile.is_active == True
    ).first()
    
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal profile not found or access denied"
        )
    
    # Handle default setting
    if profile_update.is_default is True:
        # Unset other defaults
        db.query(PersonalProfile).filter(
            PersonalProfile.user_id == user_id,
            PersonalProfile.id != profile_id,
            PersonalProfile.is_active == True
        ).update({"is_default": False})
    
    # Update fields
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    db.commit()
    db.refresh(db_profile)
    
    return db_profile


@router.delete("/{profile_id}")
def delete_personal_profile(
    profile_id: UUID,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Delete a personal profile (soft delete)."""
    db_profile = db.query(PersonalProfile).filter(
        PersonalProfile.id == profile_id,
        PersonalProfile.user_id == user_id,
        PersonalProfile.is_active == True
    ).first()
    
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal profile not found or access denied"
        )
    
    # Soft delete
    db_profile.is_active = False
    
    # If this was the default, make another profile default
    if db_profile.is_default:
        other_profile = db.query(PersonalProfile).filter(
            PersonalProfile.user_id == user_id,
            PersonalProfile.id != profile_id,
            PersonalProfile.is_active == True
        ).first()
        
        if other_profile:
            other_profile.is_default = True
    
    db.commit()
    
    return {"message": "Personal profile deleted successfully"}


@router.get("/default/{user_id}", response_model=PersonalProfileResponse)
def get_default_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get the default personal profile for a user."""
    profile = db.query(PersonalProfile).filter(
        PersonalProfile.user_id == user_id,
        PersonalProfile.is_default == True,
        PersonalProfile.is_active == True
    ).first()
    
    if not profile:
        # Return the first profile if no default is set
        profile = db.query(PersonalProfile).filter(
            PersonalProfile.user_id == user_id,
            PersonalProfile.is_active == True
        ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No personal profiles found for this user"
        )
    
    return profile