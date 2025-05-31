"""
API endpoints for System Prompts management
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repositories.system_prompt_repository import SystemPromptRepository
from app.schemas.system_prompt import (
    SystemPromptCreate,
    SystemPromptUpdate,
    SystemPromptResponse,
    SystemPromptActivate
)

router = APIRouter(tags=["system-prompts"])


@router.get("/", response_model=List[SystemPromptResponse])
async def get_all_system_prompts(
    category: str = None,
    db: Session = Depends(get_db)
):
    """Get all system prompts, optionally filtered by category"""
    repo = SystemPromptRepository()
    
    if category:
        prompts = repo.get_by_category(db, category)
    else:
        prompts = repo.get_all(db)
    
    return prompts


@router.get("/active", response_model=SystemPromptResponse)
async def get_active_system_prompt(db: Session = Depends(get_db)):
    """Get the currently active system prompt"""
    repo = SystemPromptRepository()
    active_prompt = repo.get_active(db)
    
    if not active_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active system prompt found"
        )
    
    return active_prompt


@router.get("/{prompt_id}", response_model=SystemPromptResponse)
async def get_system_prompt(
    prompt_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific system prompt by ID"""
    repo = SystemPromptRepository()
    prompt = repo.get(db, prompt_id)
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"System prompt with id {prompt_id} not found"
        )
    
    return prompt


@router.post("/", response_model=SystemPromptResponse, status_code=status.HTTP_201_CREATED)
async def create_system_prompt(
    prompt_data: SystemPromptCreate,
    db: Session = Depends(get_db)
):
    """Create a new system prompt"""
    repo = SystemPromptRepository()
    
    # Check if name already exists
    existing = db.query(repo.model).filter(
        repo.model.name == prompt_data.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"System prompt with name '{prompt_data.name}' already exists"
        )
    
    prompt = repo.create(db, obj_in=prompt_data)
    return prompt


@router.put("/{prompt_id}", response_model=SystemPromptResponse)
async def update_system_prompt(
    prompt_id: UUID,
    prompt_data: SystemPromptUpdate,
    db: Session = Depends(get_db)
):
    """Update a system prompt"""
    repo = SystemPromptRepository()
    prompt = repo.get(db, prompt_id)
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"System prompt with id {prompt_id} not found"
        )
    
    # Don't allow updating default prompts
    if prompt.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify default system prompts"
        )
    
    # Check if new name already exists (if name is being changed)
    if prompt_data.name and prompt_data.name != prompt.name:
        existing = db.query(repo.model).filter(
            repo.model.name == prompt_data.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"System prompt with name '{prompt_data.name}' already exists"
            )
    
    updated_prompt = repo.update(db, db_obj=prompt, obj_in=prompt_data.model_dump(exclude_unset=True))
    return updated_prompt


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_prompt(
    prompt_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a system prompt"""
    repo = SystemPromptRepository()
    prompt = repo.get(db, prompt_id)
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"System prompt with id {prompt_id} not found"
        )
    
    # Don't allow deleting default prompts
    if prompt.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default system prompts"
        )
    
    # Don't allow deleting the active prompt
    if prompt.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the active system prompt. Please activate another prompt first."
        )
    
    repo.remove(db, id=prompt_id)
    return None


@router.post("/activate/{prompt_id}", response_model=SystemPromptResponse)
async def activate_system_prompt(
    prompt_id: UUID,
    db: Session = Depends(get_db)
):
    """Activate a system prompt (deactivates all others)"""
    repo = SystemPromptRepository()
    
    try:
        activated_prompt = repo.set_active(db, prompt_id)
        return activated_prompt
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_all_system_prompts(db: Session = Depends(get_db)):
    """Deactivate all system prompts"""
    repo = SystemPromptRepository()
    repo.deactivate_all(db)
    return None


@router.post("/seed-defaults", response_model=List[SystemPromptResponse])
async def seed_default_prompts(db: Session = Depends(get_db)):
    """Create default system prompts if they don't exist"""
    repo = SystemPromptRepository()
    created_prompts = repo.create_default_prompts(db)
    
    # If no prompts were created, return all existing prompts
    if not created_prompts:
        return repo.get_all(db)
    
    return created_prompts