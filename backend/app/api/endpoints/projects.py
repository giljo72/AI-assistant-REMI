from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db.repositories.project_repository import project_repository
from ...schemas.project import Project, ProjectCreate, ProjectUpdate

router = APIRouter()


@router.get("/", response_model=List[Project])
def read_projects(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> Any:
    """
    Retrieve all projects with pagination.
    """
    projects = project_repository.get_multi_with_counts(db, skip=skip, limit=limit)
    return projects


@router.post("/", response_model=Project)
def create_project(
    *,
    db: Session = Depends(get_db),
    project_in: ProjectCreate
) -> Any:
    """
    Create new project.
    """
    project = project_repository.create(db, obj_in=project_in)
    # We need to initialize the counts to 0
    setattr(project, "chat_count", 0)
    setattr(project, "document_count", 0)
    return project


@router.get("/{project_id}", response_model=Project)
def read_project(
    *,
    db: Session = Depends(get_db),
    project_id: str
) -> Any:
    """
    Get a specific project by id.
    """
    project = project_repository.get_with_counts(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=Project)
def update_project(
    *,
    db: Session = Depends(get_db),
    project_id: str,
    project_in: ProjectUpdate
) -> Any:
    """
    Update a project.
    """
    project = project_repository.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = project_repository.update(db, db_obj=project, obj_in=project_in)
    
    # We need to get the counts after update
    chat_count = getattr(project, "chat_count", 0)
    document_count = getattr(project, "document_count", 0)
    
    # Refresh the project with counts
    project = project_repository.get_with_counts(db, project_id=project_id)
    return project


@router.delete("/{project_id}", response_model=Project)
def delete_project(
    *,
    db: Session = Depends(get_db),
    project_id: str
) -> Any:
    """
    Delete a project.
    """
    project = project_repository.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get chat and document counts before deletion
    chat_count = getattr(project, "chat_count", 0)
    document_count = getattr(project, "document_count", 0)
    
    # Delete the project (this will cascade to related entities)
    project = project_repository.remove(db, id=project_id)
    
    # Set the counts on the return object
    setattr(project, "chat_count", chat_count)
    setattr(project, "document_count", document_count)
    
    return project