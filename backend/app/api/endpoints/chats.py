from typing import Any, List, Dict, Optional, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
import json
import time
from datetime import datetime

logger = logging.getLogger(__name__)

from ...db.database import get_db
from ...db.repositories.chat_repository import chat_repository
from ...schemas.chat import Chat, ChatCreate, ChatUpdate, ChatMessage, ChatMessageCreate
from ...services.nim_service import get_nim_service
from ...services.llm_service import get_llm_service
from ...services.model_orchestrator import orchestrator, ModelStatus
from ..deps import get_current_user, get_optional_current_user
from ...db.models import User, UserRole

router = APIRouter()


@router.get("/debug/documents/{project_id}")
def debug_project_documents(
    project_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Debug endpoint to check document processing status for a project.
    """
    from ...db.models.document import Document, ProjectDocument
    
    # Get all documents for the project
    docs = db.query(Document).join(ProjectDocument).filter(
        ProjectDocument.project_id == project_id
    ).all()
    
    result = {
        "project_id": project_id,
        "total_documents": len(docs),
        "processed_documents": sum(1 for d in docs if d.is_processed),
        "documents": []
    }
    
    for doc in docs:
        doc_info = {
            "id": doc.id,
            "filename": doc.filename,
            "is_processed": doc.is_processed,
            "is_active": doc.is_active,
            "chunk_count": doc.chunk_count,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        }
        
        # Check if chunks exist
        try:
            from ...db.models.document import DocumentChunk
            chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
            doc_info["actual_chunks"] = chunks
        except:
            doc_info["actual_chunks"] = 0
        
        result["documents"].append(doc_info)
    
    return result


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
    max_length: int = 4096  # Increased from 150 to allow full responses
    temperature: float = 0.7
    include_context: bool = True
    context_messages: int = 100  # Increased from 10 to maintain longer conversation context
    model_name: Optional[str] = None
    model_type: Optional[str] = None
    context_mode: Optional[str] = None  # standard, project-focus, deep-research, quick-response, self-aware, custom
    custom_context: Optional[str] = None  # Custom context instructions when mode is 'custom'
    personal_context: Optional[str] = None  # Personal profile context from frontend
    # Document context settings
    is_project_documents_enabled: bool = True
    is_global_data_enabled: bool = False
    is_user_prompt_enabled: bool = False
    active_user_prompt_id: Optional[str] = None


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
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate AI response for a chat message using NVIDIA NIM.
    """
    # Verify chat exists
    chat = chat_repository.get(db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    try:
        # Get recent messages for context if requested (BEFORE saving new message)
        messages = []
        
        # Fetch context messages BEFORE saving the new user message to avoid duplication
        context_messages_list = []
        if request.include_context:
            context_messages_list = chat_repository.get_chat_messages(
                db, chat_id=chat_id, skip=0, limit=10  # Get exactly what we need
            )
        
        # NOW save the user message
        user_message = ChatMessageCreate(
            chat_id=chat_id,
            content=request.message,
            is_user=True
        )
        user_msg_obj = chat_repository.create_message(db, obj_in=user_message)
        
        # Use specified model or get from system state (moved up to get model info early)
        model_name = request.model_name
        model_type = request.model_type
        
        # If no model specified, check system for active model
        if not model_name or not model_type:
            from ...api.endpoints.system import service_states
            # Use Qwen as default model instead of NIM
            model_name = model_name or service_states.get('active_model', 'qwen2.5:32b-instruct-q4_K_M')
            model_type = model_type or service_states.get('active_model_type', 'ollama')
        
        # Get list of available models for model awareness
        from ...api.endpoints.system import get_ai_models
        available_models = get_ai_models()
        active_models = [m for m in available_models if m.status in ['loaded', 'running']]
        model_list = ", ".join([f"{m.name} ({m.type})" for m in active_models])
        
        # Check for active user prompts
        from ...db.repositories.user_prompt_repository import user_prompt_repository
        project_id = chat.project_id
        active_prompts = user_prompt_repository.get_active_for_project(db, project_id=project_id)
        
        # Get active system prompt
        from ...db.repositories.system_prompt_repository import SystemPromptRepository
        system_prompt_repo = SystemPromptRepository()
        active_system_prompt = system_prompt_repo.get_active(db)
        
        # If no active system prompt, try to activate default
        if not active_system_prompt:
            from sqlalchemy import select
            from ...db.models.system_prompt import SystemPrompt
            default_prompt = db.execute(
                select(SystemPrompt).where(
                    SystemPrompt.name == "Default Assistant",
                    SystemPrompt.is_default == True
                )
            ).scalar_one_or_none()
            if default_prompt:
                active_system_prompt = system_prompt_repo.set_active(db, default_prompt.id)
        
        # Check if we're in self-aware mode (from context mode, not user prompts)
        is_self_aware = request.context_mode == "self-aware"
        logger.info(f"Context mode: {request.context_mode}, is_self_aware: {is_self_aware}")
        
        # Build comprehensive system message
        from datetime import datetime
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        
        # Start with active system prompt content or fallback
        if active_system_prompt:
            system_content = active_system_prompt.content
        else:
            # Fallback if no system prompt is active
            system_content = """You are a helpful AI assistant designed to provide accurate, thoughtful, and practical assistance.

Core behaviors:
- Answer questions directly and comprehensively
- Admit uncertainty rather than guessing
- Ask clarifying questions when requests are ambiguous
- Provide step-by-step reasoning for complex topics
- Cite sources or indicate when information may be dated
- Maintain a professional yet conversational tone"""
        
        # Add model and system information
        system_content += f"\n\nSystem Information:\n- Model: {model_name} ({model_type})\n- Date: {current_date}\n- Available models: {model_list}"

        if is_self_aware and request.context_mode == "self-aware":
            # Self-aware mode - add project structure knowledge
            from .code_formatter_prompt import get_code_display_prompt
            
            system_content += f"""

SELF-AWARE MODE ACTIVE:
You have full read access to your own source code at F:\\assistant. This is a FastAPI + React application.

FILE ACCESS CAPABILITIES:
- Read any file: "show backend/app/main.py" or "read frontend/src/App.tsx"
- List directories: "list backend/app" or "show files in frontend/src"
- Search files: "search for 'config'" or "find all .py files"
- View structure: "show project tree" or "display directory structure"

{get_code_display_prompt()}

Architecture:
- Backend: FastAPI, SQLAlchemy, PostgreSQL with pgvector
- Frontend: React, TypeScript, Redux Toolkit, Tailwind CSS
- LLM Integration: Ollama, NVIDIA NIM
- Key features: Project management, document processing, RAG, user prompts

You can analyze code, suggest improvements, debug issues, and help with development. Always show complete file contents when requested."""
        
        # Add custom context if provided
        if request.context_mode == "custom" and request.custom_context:
            system_content += f"\n\nCustom Context Instructions:\n{request.custom_context}"
        
        # Add active user prompts to system message
        if active_prompts:
            system_content += "\n\nAdditional Instructions:"
            for prompt in active_prompts:
                system_content += f"\n- {prompt.content}"
        
        # Add personal profile context
        # Check if personal profiles are enabled (default to True for now)
        include_personal_profiles = getattr(request, 'include_personal_profiles', True)
        if include_personal_profiles:
            from ...services.personal_profile_service import personal_profile_service
            profiles_context = personal_profile_service.get_profiles_context(
                db=db,
                user_id="default_user",  # Using default user for now
                project_id=project_id,
                include_global=True
            )
            if profiles_context:
                system_content += f"\n\n{profiles_context}"
        
        # Add personal profile context if provided in request (legacy support)
        if hasattr(request, 'personal_context') and request.personal_context:
            system_content += f"\n{request.personal_context}"
        
        system_message = {
            "role": "system",
            "content": system_content
        }
        messages.append(system_message)
        
        if request.include_context and context_messages_list:
            # Convert to format expected by NIM (OpenAI-compatible)
            # No need to filter - we fetched messages before saving the new one
            context_messages = [
                {"role": "user" if msg.is_user else "assistant", "content": msg.content}
                for msg in reversed(context_messages_list)  # Reverse to get chronological order
            ]
            messages.extend(context_messages)
        
        # Check if project documents are enabled in context mode
        include_project_docs = True  # Default to including documents
        if hasattr(request, 'context_mode') and request.context_mode:
            # Check if this is a mode that excludes documents
            if request.context_mode in ['quick-response', 'minimal']:
                include_project_docs = False
        
        # Add document context if not in self-aware mode and documents are enabled
        if not is_self_aware and request.include_context and project_id and include_project_docs:
            try:
                # Search for relevant documents in the project
                from ...services.embedding_service import get_embedding_service
                from ...rag.vector_store import get_vector_store
                
                # Get embedding service and vector store
                embedding_service = get_embedding_service()
                vector_store = get_vector_store(db, embedding_service)
                
                # Log project info
                logger.info(f"Searching for documents in project {project_id}")
                
                # Check if there are any processed documents in the project
                from ...db.models.document import Document
                from ...db.models.project import ProjectDocument
                project_docs = db.query(Document).join(ProjectDocument).filter(
                    ProjectDocument.project_id == project_id,
                    Document.is_processed == True
                ).count()
                logger.info(f"Found {project_docs} processed documents in project")
                
                # Generate embedding for the query
                query_embedding = await vector_store.generate_embedding(request.message)
                
                # Search for relevant chunks with lower threshold
                chunks = vector_store.similarity_search(
                    query_embedding=query_embedding,
                    project_id=project_id,
                    limit=5,  # Get top 5 most relevant chunks
                    similarity_threshold=0.01  # Very low threshold for NIM embeddings
                )
                
                if chunks:
                    # Add document context as a system message
                    doc_context = "\n\nRelevant Document Context:\n"
                    for idx, chunk in enumerate(chunks[:3]):  # Still use only top 3
                        doc_context += f"\n[{idx+1}] From '{chunk['filename']}' (similarity: {chunk['similarity']:.2f}):\n{chunk['content']}\n"
                    
                    doc_message = {
                        "role": "system",
                        "content": doc_context
                    }
                    messages.append(doc_message)
                    logger.info(f"Added {min(len(chunks), 3)} document chunks to context")
                else:
                    logger.info("No relevant document chunks found")
            except Exception as e:
                logger.error(f"Failed to add document context: {e}", exc_info=True)
        
        # Process file operations in self-aware mode - ADMIN ONLY
        if request.context_mode == "self-aware":
            # Check if user is admin
            if current_user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=403, 
                    detail="Self-aware mode requires admin privileges"
                )
            
            logger.info(f"Self-aware mode activated by admin user: {current_user.username}")
            
            try:
                # Use the proper self-aware service
                from ...services.self_aware_service import SelfAwareService
                self_aware_service = SelfAwareService()
                
                # Process file reading requests
                file_context = self_aware_service.process_file_reading(request.message)
                
                if file_context:
                    messages.append({
                        "role": "system", 
                        "content": file_context
                    })
                    logger.info(f"Added self-aware file context: {len(file_context)} chars")
                    
                # Note: File writing will be handled after response generation
                # via the action approval system
                
            except Exception as e:
                logger.error(f"Failed to process self-aware context: {e}", exc_info=True)
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})
        
        # Generate response using Unified LLM Service
        llm_service = get_llm_service()
        
        logger.info(f"Generating response using {model_name} ({model_type})...")
        
        # Switch to the requested model if using orchestrator and it's an Ollama model
        if orchestrator and model_type == "ollama":
            from ...services.model_orchestrator import ModelStatus
            model_status = orchestrator.models.get(model_name)
            if model_status and model_status.status != ModelStatus.LOADED:
                logger.info(f"Switching to model: {model_name}")
                try:
                    switch_success = await orchestrator.switch_to_model(model_name)
                    if not switch_success:
                        logger.warning(f"Failed to switch to model {model_name}")
                except Exception as e:
                    logger.error(f"Error switching model: {e}")
        
        # Check service health for the model type
        health = await llm_service.health_check(model_type)
        if not health and model_type == "nvidia-nim":
            logger.error(f"Model service unhealthy for {model_type}")
            raise HTTPException(
                status_code=503, 
                detail=f"{model_type} service is not available. Please check if the service is running."
            )
        
        # Collect the full response from the async generator
        ai_response = ""
        async for chunk in llm_service.generate_chat_response(
            messages=messages,
            model_name=model_name,
            model_type=model_type,
            temperature=request.temperature,
            max_tokens=request.max_length,
            context_mode=request.context_mode
        ):
            ai_response += chunk
        logger.info(f"Generated response: {ai_response[:100]}...")
        
        # Check for self-aware mode actions (admin only)
        pending_actions = []
        if request.context_mode == "self-aware" and current_user.role == UserRole.ADMIN:
            # Admin users can perform self-aware actions
            session_token = f"admin_{current_user.id}"  # Use admin user ID as session token
            
            try:
                from .self_aware_integration import response_parser
                from .action_approval import approval_queue
                
                # Parse response for actions
                actions = response_parser.parse_response(ai_response, session_token)
                
                # Submit actions for approval
                for action in actions:
                    if action['type'] == 'file_write':
                        action_id = await approval_queue.request_approval(
                            action_type='file_write',
                            details={
                                'filepath': action['filepath'],
                                'content_preview': action['content'][:500] + '...' if len(action['content']) > 500 else action['content'],
                                'content_length': len(action['content']),
                                'reason': action['reason']
                            },
                            session_token=session_token
                        )
                        pending_actions.append({'id': action_id, 'type': 'file_write'})
                    
                    elif action['type'] == 'command':
                        action_id = await approval_queue.request_approval(
                            action_type='command',
                            details={
                                'command': action['command_str'],
                                'command_list': action['command'],
                                'working_directory': 'F:\\assistant',
                                'reason': action['reason']
                            },
                            session_token=session_token
                        )
                        pending_actions.append({'id': action_id, 'type': 'command'})
                
                # Inject approval status into response
                if pending_actions:
                    ai_response = response_parser.inject_approval_status(ai_response, actions)
                    
            except Exception as e:
                logger.error(f"Failed to process self-aware actions: {e}")
        
        # Get model info for response and storage
        # Match the expected frontend structure
        model_info = {
            "model_name": model_name,
            "device": "gpu" if model_type == "nvidia-nim" or health == "healthy" else "cpu",
            "is_initialized": health == "healthy",
            "nemo_available": model_type == "nvidia-nim",
            "model_type": model_type
        }
        
        # Save assistant message with model info
        assistant_message = ChatMessageCreate(
            chat_id=chat_id,
            content=ai_response,
            is_user=False,
            model_info=model_info
        )
        assistant_msg_obj = chat_repository.create_message(db, obj_in=assistant_message)
        
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


@router.post("/{chat_id}/generate-stream")
async def generate_chat_response_stream(
    *,
    db: Session = Depends(get_db),
    chat_id: str,
    request: ChatGenerateRequest,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """
    Generate AI response for a chat message with streaming.
    Returns Server-Sent Events (SSE) stream.
    """
    # Verify chat exists
    chat = chat_repository.get(db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Capture project_id before entering the async generator (to avoid SQLAlchemy session issues)
    project_id_for_context = chat.project_id
    
    # Fetch context messages BEFORE saving the new user message to avoid duplication
    context_messages_list = []
    if request.include_context:
        context_messages_list = chat_repository.get_chat_messages(
            db, chat_id=chat_id, skip=0, limit=request.context_messages  # Get exactly what we need
        )
    
    # NOW save the user message
    user_message = ChatMessageCreate(
        chat_id=chat_id,
        content=request.message,
        is_user=True
    )
    user_msg_obj = chat_repository.create_message(db, obj_in=user_message)
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            # Build messages context (same as non-streaming endpoint)
            messages = []
            
            # Get model info
            model_name = request.model_name
            model_type = request.model_type
            
            if not model_name or not model_type:
                from ...api.endpoints.system import service_states
                model_name = model_name or service_states.get('active_model', 'mistral-nemo:latest')
                model_type = model_type or service_states.get('active_model_type', 'ollama')
            
            # Get available models for awareness
            from ...api.endpoints.system import get_ai_models
            available_models = get_ai_models()
            active_models = [m for m in available_models if m.status in ['loaded', 'running']]
            model_list = ", ".join([f"{m.name} ({m.type})" for m in active_models])
            
            # Build system message
            from datetime import datetime
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            
            system_content = f"""You are {model_name}, an AI assistant running via {model_type}. Today's date is {current_date}.

You are part of an AI Assistant system with the following capabilities:
- Multiple AI models available: {model_list}
- Currently active model: {model_name} ({model_type})
- Document processing and semantic search
- Project-based knowledge containment
- Custom user prompts for behavior modification

You are a helpful, friendly, and knowledgeable assistant. Be concise but thorough in your responses."""

            # Add self-aware mode if enabled
            if request.context_mode == "self-aware":
                system_content += """

SELF-AWARE MODE ACTIVE:
You have access to knowledge about your own implementation at F:\\assistant. This is a FastAPI + React application with:
- Backend: FastAPI, SQLAlchemy, PostgreSQL with pgvector
- Frontend: React, TypeScript, Redux Toolkit, Tailwind CSS
- LLM Integration: Ollama, NVIDIA NIM, Transformers
- Key features: Project management, document processing, RAG, user prompts

You can help improve your own code, debug issues, and suggest enhancements."""

            # Add custom context if provided
            if request.context_mode == "custom" and request.custom_context:
                system_content += f"\n\nCustom Context Instructions:\n{request.custom_context}"
            
            # Add personal profile context
            include_personal_profiles = getattr(request, 'include_personal_profiles', True)
            if include_personal_profiles:
                from ...services.personal_profile_service import personal_profile_service
                profiles_context = personal_profile_service.get_profiles_context(
                    db=db,
                    user_id="default_user",  # Using default user for now
                    project_id=project_id_for_context,
                    include_global=True
                )
                if profiles_context:
                    system_content += f"\n\n{profiles_context}"
            
            messages.append({"role": "system", "content": system_content})
            
            # Add context messages if requested
            if request.include_context and context_messages_list:
                # No need to filter - we fetched messages before saving the new one
                for msg in reversed(context_messages_list):
                    role = "user" if msg.is_user else "assistant"
                    messages.append({"role": role, "content": msg.content})
            
            # Add document context if enabled
            if request.is_project_documents_enabled or request.is_global_data_enabled:
                try:
                    # Import necessary modules
                    from ...rag.vector_store import get_vector_store
                    from ...services.embedding_service import get_embedding_service
                    
                    # Initialize services
                    embedding_service = get_embedding_service()
                    # NIM doesn't need initialization
                    vector_store = get_vector_store(db, embedding_service)
                    
                    # Generate embedding for the user's message
                    if hasattr(embedding_service, 'embed_text'):
                        query_embedding = await embedding_service.embed_text(request.message)
                    elif hasattr(embedding_service, 'embed_query'):
                        # NIM uses embed_query for search queries
                        query_embedding = await embedding_service.embed_query(request.message)
                    else:
                        raise Exception("Embedding service has no compatible embed method")
                    
                    # Determine project scope
                    project_id = project_id_for_context if request.is_project_documents_enabled and not request.is_global_data_enabled else None
                    
                    # Perform semantic search
                    relevant_chunks = vector_store.similarity_search(
                        query_embedding=query_embedding,
                        project_id=project_id,
                        limit=5,  # Get top 5 most relevant chunks
                        similarity_threshold=0.01  # Very low threshold for NIM embeddings
                    )
                    
                    # If we found relevant documents, add them to context
                    if relevant_chunks:
                        document_context = "\n\nRelevant information from documents:\n"
                        for i, chunk in enumerate(relevant_chunks, 1):
                            document_context += f"\n[Document {i}: {chunk['filename']} (similarity: {chunk['similarity']:.2f})]\n"
                            document_context += f"{chunk['content']}\n"
                        
                        # Add document context as a system message
                        messages.append({
                            "role": "system",
                            "content": f"Use the following document excerpts to help answer the user's question. These are the most relevant sections found:{document_context}"
                        })
                        
                        logger.info(f"Added {len(relevant_chunks)} document chunks to context")
                    else:
                        logger.info("No relevant document chunks found for the query")
                        
                except Exception as e:
                    logger.error(f"Failed to retrieve document context: {str(e)}")
                    # Continue without document context rather than failing the request
            
            # Process file operations in self-aware mode - ADMIN ONLY
            if request.context_mode == "self-aware":
                # Check if user is admin
                if current_user.role != UserRole.ADMIN:
                    raise HTTPException(
                        status_code=403, 
                        detail="Self-aware mode requires admin privileges"
                    )
                
                logger.info(f"[STREAMING] Self-aware mode activated by admin user: {current_user.username}")
                
                try:
                    # Use the proper self-aware service
                    from ...services.self_aware_service import SelfAwareService
                    self_aware_service = SelfAwareService()
                    
                    # Process file reading requests
                    file_context = self_aware_service.process_file_reading(request.message)
                    
                    if file_context:
                        messages.append({
                            "role": "system", 
                            "content": file_context
                        })
                        logger.info(f"[STREAMING] Added self-aware file context: {len(file_context)} chars")
                        
                except Exception as e:
                    logger.error(f"[STREAMING] Failed to process self-aware context: {e}", exc_info=True)
            
            # Add current user message
            messages.append({"role": "user", "content": request.message})
            
            # Switch to the requested model if using orchestrator and it's an Ollama model
            if orchestrator and model_type == "ollama":
                model_status = orchestrator.models.get(model_name)
                if model_status and model_status.status != ModelStatus.LOADED:
                    logger.info(f"Switching to model: {model_name}")
                    try:
                        switch_success = await orchestrator.switch_to_model(model_name)
                        if not switch_success:
                            logger.warning(f"Failed to switch to model {model_name}")
                    except Exception as e:
                        logger.error(f"Error switching model: {e}")
            
            # Start streaming response
            llm_service = get_llm_service()
            
            # Check service health for the model type
            health = await llm_service.health_check(model_type)
            if not health and model_type == "nvidia-nim":
                logger.error(f"Model service unhealthy for {model_type}")
                raise HTTPException(
                    status_code=503, 
                    detail=f"{model_type} service is not available. Please check if the service is running."
                )
            
            # Send initial SSE event
            yield f"data: {json.dumps({'type': 'start', 'model': model_name})}\n\n"
            
            # Collect response for saving
            full_response = ""
            
            # Stream the response
            async for chunk in llm_service.generate_chat_response(
                messages=messages,
                model_name=model_name,
                model_type=model_type,
                temperature=request.temperature,
                max_tokens=request.max_length,
                context_mode=request.context_mode
            ):
                full_response += chunk
                # Send chunk as SSE event
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            
            # Get model info for storage
            # Match the expected frontend structure
            model_info = {
                "model_name": model_name,
                "device": "gpu" if model_type == "nvidia-nim" or health == "healthy" else "cpu",
                "is_initialized": health == "healthy",
                "nemo_available": model_type == "nvidia-nim",
                "model_type": model_type
            }
            
            # Save the complete assistant message with model info
            assistant_message = ChatMessageCreate(
                chat_id=chat_id,
                content=full_response,
                is_user=False,
                model_info=model_info
            )
            assistant_msg_obj = chat_repository.create_message(db, obj_in=assistant_message)
            
            # Send completion event with message IDs
            yield f"data: {json.dumps({'type': 'complete', 'user_message_id': str(user_msg_obj.id), 'assistant_message_id': str(assistant_msg_obj.id)})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming generation failed: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable Nginx buffering
        }
    )