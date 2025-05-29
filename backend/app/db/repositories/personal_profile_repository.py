from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID

from ..models.personal_profile import PersonalProfile, VisibilityLevel
from ...schemas.personal_profile import PersonalProfileCreate, PersonalProfileUpdate
from .base_repository import BaseRepository


class PersonalProfileRepository(BaseRepository[PersonalProfile, PersonalProfileCreate, PersonalProfileUpdate]):
    """Repository for personal profile database operations"""
    
    def __init__(self):
        super().__init__(PersonalProfile)
    
    def get_by_user(
        self,
        db: Session,
        user_id: str = "default_user",
        skip: int = 0,
        limit: int = 100,
        include_global: bool = False
    ) -> List[PersonalProfile]:
        """Get all profiles for a user, optionally including global profiles"""
        query = db.query(self.model).filter(
            self.model.is_active == True
        )
        
        if include_global:
            # Include user's profiles and all global profiles
            query = query.filter(
                or_(
                    self.model.user_id == user_id,
                    self.model.visibility == VisibilityLevel.GLOBAL.value
                )
            )
        else:
            # Only user's profiles
            query = query.filter(self.model.user_id == user_id)
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_visibility(
        self,
        db: Session,
        visibility: VisibilityLevel,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PersonalProfile]:
        """Get profiles by visibility level"""
        query = db.query(self.model).filter(
            and_(
                self.model.visibility == visibility,
                self.model.is_active == True
            )
        )
        
        # For private/shared, filter by user
        if visibility != VisibilityLevel.GLOBAL.value and user_id:
            query = query.filter(self.model.user_id == user_id)
        
        return query.offset(skip).limit(limit).all()
    
    def search_profiles(
        self,
        db: Session,
        query: str,
        user_id: str = "default_user",
        include_shared: bool = True,
        include_global: bool = True
    ) -> List[PersonalProfile]:
        """Search profiles by name, organization, or notes"""
        search_pattern = f"%{query}%"
        
        # Build visibility filter
        visibility_conditions = [
            and_(
                self.model.user_id == user_id,
                self.model.visibility == VisibilityLevel.PRIVATE.value
            )
        ]
        
        if include_shared:
            visibility_conditions.append(
                and_(
                    self.model.user_id == user_id,
                    self.model.visibility == VisibilityLevel.SHARED.value
                )
            )
        
        if include_global:
            visibility_conditions.append(
                self.model.visibility == VisibilityLevel.GLOBAL.value
            )
        
        return db.query(self.model).filter(
            and_(
                self.model.is_active == True,
                or_(*visibility_conditions),
                or_(
                    self.model.name.ilike(search_pattern),
                    self.model.organization.ilike(search_pattern),
                    self.model.notes.ilike(search_pattern),
                    self.model.role.ilike(search_pattern)
                )
            )
        ).all()
    
    def get_profiles_for_context(
        self,
        db: Session,
        user_id: str = "default_user",
        project_id: Optional[str] = None,
        include_global: bool = True
    ) -> List[PersonalProfile]:
        """Get profiles that should be included in chat context"""
        # For now, just get all active profiles for the user
        # In future, could filter by project associations
        query = db.query(self.model).filter(
            self.model.is_active == True
        )
        
        if include_global:
            query = query.filter(
                or_(
                    self.model.user_id == user_id,
                    self.model.visibility == VisibilityLevel.GLOBAL
                )
            )
        else:
            query = query.filter(self.model.user_id == user_id)
        
        return query.all()
    
    def create_with_user(
        self,
        db: Session,
        obj_in: PersonalProfileCreate,
        user_id: str = "default_user"
    ) -> PersonalProfile:
        """Create a new profile for a user"""
        db_obj = self.model(
            **obj_in.dict(),
            user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Singleton instance
personal_profile_repository = PersonalProfileRepository()