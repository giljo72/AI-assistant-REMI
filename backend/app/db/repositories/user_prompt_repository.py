from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .base_repository import BaseRepository
from ..models.user_prompt import UserPrompt
from ...schemas.user_prompt import UserPromptCreate, UserPromptUpdate


class UserPromptRepository(BaseRepository[UserPrompt, UserPromptCreate, UserPromptUpdate]):
    """
    Repository for UserPrompt model with custom methods.
    """
    
    def __init__(self):
        super().__init__(UserPrompt)
    
    def get_by_project(self, db: Session, project_id: str, skip: int = 0, limit: int = 100) -> List[UserPrompt]:
        """Get all user prompts for a specific project."""
        try:
            return db.query(UserPrompt).filter(UserPrompt.project_id == project_id).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def get_active_for_project(self, db: Session, project_id: str) -> Optional[UserPrompt]:
        """Get the active user prompt for a project, if any."""
        try:
            return db.query(UserPrompt).filter(
                UserPrompt.project_id == project_id,
                UserPrompt.is_active == True
            ).first()
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def activate_prompt(self, db: Session, prompt_id: str, project_id: str) -> UserPrompt:
        """
        Activate a prompt for a project and deactivate all others.
        """
        try:
            # Deactivate all prompts for the project
            db.query(UserPrompt).filter(
                UserPrompt.project_id == project_id,
                UserPrompt.is_active == True
            ).update({"is_active": False})
            
            # Activate the requested prompt
            prompt = db.query(UserPrompt).filter(UserPrompt.id == prompt_id).first()
            prompt.is_active = True
            
            db.commit()
            db.refresh(prompt)
            return prompt
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def deactivate_all_for_project(self, db: Session, project_id: str) -> None:
        """
        Deactivate all prompts for a project.
        """
        try:
            db.query(UserPrompt).filter(
                UserPrompt.project_id == project_id,
                UserPrompt.is_active == True
            ).update({"is_active": False})
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise e


user_prompt_repository = UserPromptRepository()