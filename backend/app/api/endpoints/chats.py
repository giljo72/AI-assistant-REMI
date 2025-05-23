from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

from ...db.database import get_db
from ...db.repositories.chat_repository import chat_repository
from ...schemas.chat import Chat, ChatCreate, ChatUpdate, ChatMessage, ChatMessageCreate
from ...services.nim_service import get_nim_service
from ...services.llm_service import get_llm_service

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


class ChatGenerateRequest(BaseModel):
    """Request model for generating chat responses."""
    message: str
    max_length: int = 150
    temperature: float = 0.7
    include_context: bool = True
    model_name: Optional[str] = None
    model_type: Optional[str] = None


class ChatGenerateResponse(BaseModel):
    """Response model for chat generation."""
    response: str
    user_message_id: str
    assistant_message_id: str
    model_info: Dict[str, Any]


@router.post("/{chat_id}/generate", response_model=ChatGenerateResponse)
async def generate_chat_response_endpoint(
    *,
    db: Session = Depends(get_db),
    chat_id: str,
    request: ChatGenerateRequest,
    background_tasks: BackgroundTasks
) -> Any:
    """
    Generate AI response for a chat message using NVIDIA NIM.
    """
    # Verify chat exists
    chat = chat_repository.get(db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    try:
        # Save user message first
        user_message = ChatMessageCreate(
            chat_id=chat_id,
            content=request.message,
            is_user=True
        )
        user_msg_obj = chat_repository.create_message(db, obj_in=user_message)
        
        # Get recent messages for context if requested
        messages = []
        if request.include_context:
            recent_messages = chat_repository.get_chat_messages(
                db, chat_id=chat_id, skip=0, limit=10
            )
            # Convert to format expected by NIM (OpenAI-compatible)
            messages = [
                {"role": "user" if msg.is_user else "assistant", "content": msg.content}
                for msg in reversed(recent_messages)  # Reverse to get chronological order
            ]
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})
        
        # Generate response using Unified LLM Service
        llm_service = get_llm_service()
        
        # Use specified model or get from system state
        model_name = request.model_name
        model_type = request.model_type
        
        # If no model specified, check system for active model
        if not model_name or not model_type:
            from ...api.endpoints.system import service_states
            model_name = model_name or service_states.get('active_model', 'meta/llama-3.1-8b-instruct')
            model_type = model_type or service_states.get('active_model_type', 'nvidia-nim')
        
        logger.info(f"Generating response using {model_name} ({model_type})...")
        
        # Check service health for the model type
        health = await llm_service.health_check(model_type)
        if not health and model_type == "nvidia-nim":
            logger.error(f"Model service unhealthy for {model_type}")
            raise HTTPException(
                status_code=503, 
                detail=f"{model_type} service is not available. Please check if the service is running."
            )
        
        ai_response = await llm_service.generate_chat_response(
            messages=messages,
            model_name=model_name,
            model_type=model_type,
            temperature=request.temperature,
            max_tokens=request.max_length
        )
        logger.info(f"Generated response: {ai_response[:100]}...")
        
        # Save assistant message
        assistant_message = ChatMessageCreate(
            chat_id=chat_id,
            content=ai_response,
            is_user=False
        )
        assistant_msg_obj = chat_repository.create_message(db, obj_in=assistant_message)
        
        # Get model info for response
        model_info = {
            "model": model_name,
            "type": model_type,
            "health": health,
            "temperature": request.temperature,
            "max_length": request.max_length
        }
        
        return ChatGenerateResponse(
            response=ai_response,
            user_message_id=str(user_msg_obj.id),
            assistant_message_id=str(assistant_msg_obj.id),
            model_info=model_info
        )
        
    except Exception as e:
        logger.error(f"Chat generation failed with error: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate response: {str(e)}"
        )


@router.post("/{chat_id}/messages/generate", response_model=ChatMessage)
def generate_and_save_response(
    *,
    db: Session = Depends(get_db),
    chat_id: str,
    message_content: str = Query(..., description="The user message to respond to"),
    max_length: int = Query(150, description="Maximum response length"),
    temperature: float = Query(0.7, description="Sampling temperature")
) -> Any:
    """
    Simple endpoint to generate and save an AI response to a message.
    """
    # Verify chat exists
    chat = chat_repository.get(db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    try:
        # Get recent context
        recent_messages = chat_repository.get_chat_messages(
            db, chat_id=chat_id, skip=0, limit=5
        )
        
        # Format messages for NeMo
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(recent_messages)
        ]
        messages.append({"role": "user", "content": message_content})
        
        # Generate response
        ai_response = generate_chat_response(
            messages=messages,
            max_length=max_length,
            temperature=temperature
        )
        
        # Save assistant message
        assistant_message = ChatMessageCreate(
            chat_id=chat_id,
            role="assistant",
            content=ai_response
        )
        
        return chat_repository.create_message(db, obj_in=assistant_message)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )