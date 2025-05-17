from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db.repositories.chat_repository import chat_repository
from ...schemas.chat import Chat, ChatCreate, ChatUpdate, ChatMessage, ChatMessageCreate

router = APIRouter()


@router.get("/", response_model=List[Chat])
def read_chats(
    db: Session = Depends(get_db),
    project_id: str = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> Any:
    """
    Retrieve all chats with optional project filtering.
    """
    if project_id:
        chats = chat_repository.get_multi_by_project(db, project_id=project_id, skip=skip, limit=limit)
    else:
        chats = chat_repository.get_multi(db, skip=skip, limit=limit)
    return chats


@router.post("/", response_model=Chat)
def create_chat(
    *,
    db: Session = Depends(get_db),
    chat_in: ChatCreate
) -> Any:
    """
    Create new chat.
    """
    chat = chat_repository.create(db, obj_in=chat_in)
    return chat


@router.get("/{chat_id}", response_model=Chat)
def read_chat(
    *,
    db: Session = Depends(get_db),
    chat_id: str
) -> Any:
    """
    Get a specific chat by id.
    """
    chat = chat_repository.get(db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.put("/{chat_id}", response_model=Chat)
def update_chat(
    *,
    db: Session = Depends(get_db),
    chat_id: str,
    chat_in: ChatUpdate
) -> Any:
    """
    Update a chat.
    """
    chat = chat_repository.get(db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat = chat_repository.update(db, db_obj=chat, obj_in=chat_in)
    return chat


@router.delete("/{chat_id}", response_model=Chat)
def delete_chat(
    *,
    db: Session = Depends(get_db),
    chat_id: str
) -> Any:
    """
    Delete a chat.
    """
    chat = chat_repository.get(db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat = chat_repository.remove(db, id=chat_id)
    return chat


@router.post("/messages/", response_model=ChatMessage)
def create_chat_message(
    *,
    db: Session = Depends(get_db),
    message_in: ChatMessageCreate
) -> Any:
    """
    Create a new chat message.
    """
    message = chat_repository.create_message(db, obj_in=message_in)
    return message


@router.get("/{chat_id}/messages/", response_model=List[ChatMessage])
def read_chat_messages(
    *,
    db: Session = Depends(get_db),
    chat_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> Any:
    """
    Get messages for a specific chat.
    """
    messages = chat_repository.get_chat_messages(db, chat_id=chat_id, skip=skip, limit=limit)
    return messages