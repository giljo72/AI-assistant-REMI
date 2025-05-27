from typing import Any, List, Dict, Optional, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
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
from ...services.model_orchestrator import orchestrator

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
    context_messages: int = 10  # Number of previous messages to include in context
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
        
        # Use specified model or get from system state (moved up to get model info early)
        model_name = request.model_name
        model_type = request.model_type
        
        # If no model specified, check system for active model
        if not model_name or not model_type:
            from ...api.endpoints.system import service_states
            model_name = model_name or service_states.get('active_model', 'meta/llama-3.1-8b-instruct')
            model_type = model_type or service_states.get('active_model_type', 'nvidia-nim')
        
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

        if is_self_aware:
            # Self-aware mode - add project structure knowledge
            system_content += f"""

SELF-AWARE MODE ACTIVE:
You have access to knowledge about your own implementation at F:\\assistant. This is a FastAPI + React application with:
- Backend: FastAPI, SQLAlchemy, PostgreSQL with pgvector
- Frontend: React, TypeScript, Redux Toolkit, Tailwind CSS
- LLM Integration: Ollama, NVIDIA NIM, Transformers
- Key features: Project management, document processing, RAG, user prompts

You can help improve your own code, debug issues, and suggest enhancements. When asked about your implementation, reference specific files and provide accurate technical details."""
        
        # Add custom context if provided
        if request.context_mode == "custom" and request.custom_context:
            system_content += f"\n\nCustom Context Instructions:\n{request.custom_context}"
        
        # Add active user prompts to system message
        if active_prompts:
            system_content += "\n\nAdditional Instructions:"
            for prompt in active_prompts:
                system_content += f"\n- {prompt.content}"
        
        # Add personal profile context if provided in request
        if hasattr(request, 'personal_context') and request.personal_context:
            system_content += f"\n{request.personal_context}"
        
        system_message = {
            "role": "system",
            "content": system_content
        }
        messages.append(system_message)
        
        if request.include_context:
            recent_messages = chat_repository.get_chat_messages(
                db, chat_id=chat_id, skip=0, limit=10
            )
            # Convert to format expected by NIM (OpenAI-compatible)
            context_messages = [
                {"role": "user" if msg.is_user else "assistant", "content": msg.content}
                for msg in reversed(recent_messages)  # Reverse to get chronological order
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
        
        # Process file operations in self-aware mode
        if is_self_aware:
            from ...services.file_reader_service import get_file_reader
            file_reader = get_file_reader()
            
            # Check if the user is asking about files
            user_msg_lower = request.message.lower()
            file_context = ""
            
            # Auto-detect file-related queries
            if any(keyword in user_msg_lower for keyword in ['file', 'code', 'show', 'read', 'list', 'search', 'find', 'look at', 'check']):
                # Extract potential file paths from the message
                import re
                
                # Look for file paths (e.g., backend/app/main.py or app.py)
                file_patterns = [
                    r'[\'"`]([^\'"`]+\.[a-zA-Z]+)[\'"`]',  # Quoted filenames
                    r'\b(\w+/[\w/]+\.\w+)\b',  # Path-like patterns
                    r'\b(\w+\.\w+)\b',  # Simple filenames
                ]
                
                potential_files = []
                for pattern in file_patterns:
                    matches = re.findall(pattern, request.message)
                    potential_files.extend(matches)
                
                # Try to read mentioned files
                files_read = []
                for file_path in potential_files:
                    result = file_reader.read_file(file_path)
                    if result["success"]:
                        files_read.append({
                            "path": file_path,
                            "content": result["content"]  # Full file content, no truncation
                        })
                
                # If files were found and read, add them to context
                if files_read:
                    file_context = "\n\nFile Contents:\n"
                    for file_info in files_read:
                        file_context += f"\n=== {file_info['path']} ===\n{file_info['content']}\n"
                
                # If asking to list files in a directory
                if 'list' in user_msg_lower and ('file' in user_msg_lower or 'directory' in user_msg_lower):
                    # Extract directory from message
                    dir_match = re.search(r'(?:in|from)\s+[\'"`]?([^\'"`\s]+)[\'"`]?', request.message)
                    directory = dir_match.group(1) if dir_match else ""
                    
                    files = file_reader.list_files(directory)
                    if files:
                        file_context += f"\n\nFiles in {directory or 'root directory'}:\n"
                        for f in files[:20]:  # Limit to 20 files
                            file_context += f"- {f['type']}: {f['path']}\n"
                
                # If searching for something in files
                if 'search' in user_msg_lower or 'find' in user_msg_lower:
                    search_match = re.search(r'(?:search|find)\s+(?:for\s+)?[\'"`]([^\'"`]+)[\'"`]', request.message)
                    if search_match:
                        search_term = search_match.group(1)
                        results = file_reader.search_in_files(search_term, max_results=10)
                        if results:
                            file_context += f"\n\nSearch results for '{search_term}':\n"
                            for r in results:
                                file_context += f"- {r['file']}:{r['line']}: {r['content']}\n"
            
            # Add file context if any was gathered
            if file_context:
                file_message = {
                    "role": "system",
                    "content": file_context
                }
                messages.append(file_message)
                logger.info("Added file reading context to self-aware mode")
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})
        
        # Generate response using Unified LLM Service
        llm_service = get_llm_service()
        
        logger.info(f"Generating response using {model_name} ({model_type})...")
        
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


@router.post("/{chat_id}/generate-stream")
async def generate_chat_response_stream(
    *,
    db: Session = Depends(get_db),
    chat_id: str,
    request: ChatGenerateRequest,
    background_tasks: BackgroundTasks
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
    
    # Save user message first
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
            
            messages.append({"role": "system", "content": system_content})
            
            # Add context messages if requested
            if request.include_context:
                recent_messages = chat_repository.get_chat_messages(
                    db, chat_id=chat_id, skip=0, limit=request.context_messages
                )
                for msg in reversed(recent_messages[:-1]):  # Exclude the just-saved user message
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
            
            # Add current user message
            messages.append({"role": "user", "content": request.message})
            
            # Start streaming response
            llm_service = get_llm_service()
            
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
            
            # Save the complete assistant message
            assistant_message = ChatMessageCreate(
                chat_id=chat_id,
                content=full_response,
                is_user=False
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