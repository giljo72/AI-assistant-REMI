"""
Personal Profile Service
Handles profile formatting and integration with chat context
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from ..db.repositories.personal_profile_repository import personal_profile_repository
from ..schemas.personal_profile import PersonalProfile


class PersonalProfileService:
    """Service for personal profile operations and chat integration"""
    
    def get_profiles_context(
        self,
        db: Session,
        user_id: str = "default_user",
        project_id: Optional[str] = None,
        include_global: bool = True
    ) -> str:
        """Get formatted profiles context for chat"""
        profiles = personal_profile_repository.get_profiles_for_context(
            db=db,
            user_id=user_id,
            project_id=project_id,
            include_global=include_global
        )
        
        if not profiles:
            return ""
        
        context_parts = ["Personal Context Information:"]
        context_parts.append("=" * 40)
        
        for profile in profiles:
            profile_schema = PersonalProfile.from_orm(profile)
            context_parts.append(profile_schema.format_for_context())
            context_parts.append("-" * 20)
        
        return "\n".join(context_parts)
    
    def format_profiles_for_prompt(self, profiles: List[PersonalProfile]) -> str:
        """Format a list of profiles for inclusion in LLM prompt"""
        if not profiles:
            return ""
        
        formatted = ["Known People:"]
        for profile in profiles:
            formatted.append(f"\n- {profile.format_for_context()}")
        
        return "\n".join(formatted)
    
    def get_default_profile(
        self,
        db: Session,
        user_id: str = "default_user"
    ) -> Optional[PersonalProfile]:
        """Get the default profile for a user"""
        profiles = personal_profile_repository.get_by_user(
            db=db,
            user_id=user_id,
            limit=1
        )
        return PersonalProfile.from_orm(profiles[0]) if profiles else None


# Singleton instance
personal_profile_service = PersonalProfileService()