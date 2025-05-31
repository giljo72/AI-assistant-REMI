from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db.repositories.user_prompt_repository import user_prompt_repository
from ...db.repositories.project_repository import project_repository
from ...schemas.user_prompt import UserPrompt, UserPromptCreate, UserPromptUpdate

router = APIRouter()


@router.get("/", response_model=List[UserPrompt])
def read_user_prompts(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    project_id: str = None
) -> Any:
    """
    Retrieve all user prompts with pagination.
    If project_id is provided, only return prompts for that project.
    """
    if project_id:
        # Check if project exists
        project = project_repository.get(db, id=project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        user_prompts = user_prompt_repository.get_by_project(db, project_id=project_id, skip=skip, limit=limit)
    else:
        user_prompts = user_prompt_repository.get_multi(db, skip=skip, limit=limit)
    
    return user_prompts


@router.post("/", response_model=UserPrompt)
def create_user_prompt(
    *,
    db: Session = Depends(get_db),
    user_prompt_in: UserPromptCreate
) -> Any:
    """
    Create new user prompt.
    """
    # Check if project exists if project_id is provided
    if user_prompt_in.project_id:
        project = project_repository.get(db, id=user_prompt_in.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    
    user_prompt = user_prompt_repository.create(db, obj_in=user_prompt_in)
    return user_prompt


@router.get("/{user_prompt_id}", response_model=UserPrompt)
def read_user_prompt(
    *,
    db: Session = Depends(get_db),
    user_prompt_id: str
) -> Any:
    """
    Get a specific user prompt by id.
    """
    user_prompt = user_prompt_repository.get(db, id=user_prompt_id)
    if not user_prompt:
        raise HTTPException(status_code=404, detail="User prompt not found")
    return user_prompt


@router.put("/{user_prompt_id}", response_model=UserPrompt)
def update_user_prompt(
    *,
    db: Session = Depends(get_db),
    user_prompt_id: str,
    user_prompt_in: UserPromptUpdate
) -> Any:
    """
    Update a user prompt.
    """
    user_prompt = user_prompt_repository.get(db, id=user_prompt_id)
    if not user_prompt:
        raise HTTPException(status_code=404, detail="User prompt not found")
    
    # Check if project exists if project_id is provided and changed
    if user_prompt_in.project_id and user_prompt_in.project_id != user_prompt.project_id:
        project = project_repository.get(db, id=user_prompt_in.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    
    # If is_active is being set to True, deactivate other prompts for the project
    if user_prompt_in.is_active and not user_prompt.is_active:
        project_id = user_prompt_in.project_id or user_prompt.project_id
        if project_id:
            user_prompt_repository.deactivate_all_for_project(db, project_id=project_id)
    
    user_prompt = user_prompt_repository.update(db, db_obj=user_prompt, obj_in=user_prompt_in)
    return user_prompt


@router.delete("/{user_prompt_id}", response_model=UserPrompt)
def delete_user_prompt(
    *,
    db: Session = Depends(get_db),
    user_prompt_id: str
) -> Any:
    """
    Delete a user prompt.
    """
    user_prompt = user_prompt_repository.get(db, id=user_prompt_id)
    if not user_prompt:
        raise HTTPException(status_code=404, detail="User prompt not found")
    
    user_prompt = user_prompt_repository.remove(db, id=user_prompt_id)
    return user_prompt


@router.post("/{user_prompt_id}/activate", response_model=UserPrompt)
def activate_user_prompt(
    *,
    db: Session = Depends(get_db),
    user_prompt_id: str
) -> Any:
    """
    Activate a specific user prompt and deactivate all others.
    For project prompts: deactivates other prompts in the same project.
    For global prompts: deactivates all other global prompts.
    """
    user_prompt = user_prompt_repository.get(db, id=user_prompt_id)
    if not user_prompt:
        raise HTTPException(status_code=404, detail="User prompt not found")
    
    if user_prompt.project_id:
        # Project-specific prompt
        user_prompt = user_prompt_repository.activate_prompt(
            db, prompt_id=user_prompt_id, project_id=user_prompt.project_id
        )
    else:
        # Global prompt - deactivate all other global prompts
        user_prompt = user_prompt_repository.activate_global_prompt(
            db, prompt_id=user_prompt_id
        )
    
    return user_prompt