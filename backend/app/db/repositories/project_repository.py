from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from .base_repository import BaseRepository
from ..models.project import Project
from ..models.chat import Chat
from ..models.document import ProjectDocument
from ...schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectUpdate]):
    """
    Repository for Project model with custom methods specific to projects.
    """
    
    def __init__(self):
        super().__init__(Project)
    
    def get_with_counts(self, db: Session, project_id: str) -> Optional[Project]:
        """Get a project by ID with chat and document counts."""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return None
            
            # Count number of chats
            chat_count = db.query(func.count(Chat.id)).filter(Chat.project_id == project_id).scalar()
            
            # Count number of documents
            doc_count = db.query(func.count(ProjectDocument.id)).filter(ProjectDocument.project_id == project_id).scalar()
            
            # Add counts to project
            setattr(project, "chat_count", chat_count)
            setattr(project, "document_count", doc_count)
            
            return project
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def get_multi_with_counts(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """Get multiple projects with chat and document counts."""
        try:
            projects = db.query(Project).offset(skip).limit(limit).all()
            
            for project in projects:
                # Count number of chats
                chat_count = db.query(func.count(Chat.id)).filter(Chat.project_id == project.id).scalar()
                
                # Count number of documents
                doc_count = db.query(func.count(ProjectDocument.id)).filter(ProjectDocument.project_id == project.id).scalar()
                
                # Add counts to project
                setattr(project, "chat_count", chat_count)
                setattr(project, "document_count", doc_count)
            
            return projects
        except SQLAlchemyError as e:
            db.rollback()
            raise e


project_repository = ProjectRepository()