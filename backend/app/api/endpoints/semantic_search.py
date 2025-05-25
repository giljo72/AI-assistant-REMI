from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...db.database import get_db
from ...rag.vector_store import get_vector_store

router = APIRouter()


class SemanticSearchRequest(BaseModel):
    """Schema for semantic search requests."""
    query: str
    project_id: Optional[str] = None
    limit: Optional[int] = 10
    similarity_threshold: Optional[float] = 0.7


class SearchResult(BaseModel):
    """Schema for semantic search results."""
    document_id: str
    chunk_id: str
    content: str
    similarity: float
    filename: str
    filetype: str
    chunk_index: int
    meta_data: Optional[dict] = None


@router.post("/", response_model=List[SearchResult])
async def semantic_search(
    search_request: SemanticSearchRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Perform a semantic search using vector embeddings.
    """
    try:
        # Get embedding service and vector store
        from ...services.embedding_service import get_embedding_service
        embedding_service = get_embedding_service()
        vector_store = get_vector_store(db, embedding_service)
        
        # Generate embedding for the query
        query_embedding = await vector_store.generate_embedding(search_request.query)
        
        # Perform similarity search
        results = vector_store.similarity_search(
            query_embedding=query_embedding,
            project_id=search_request.project_id,
            limit=search_request.limit,
            similarity_threshold=search_request.similarity_threshold
        )
        
        # Convert to response model
        search_results = []
        for result in results:
            search_results.append(
                SearchResult(
                    document_id=result["document_id"],
                    chunk_id=result["chunk_id"],
                    content=result["content"],
                    similarity=float(result["similarity"]),
                    filename=result["filename"],
                    filetype=result["filetype"],
                    chunk_index=result["chunk_index"],
                    meta_data=result.get("meta_data")
                )
            )
        
        return search_results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing semantic search: {str(e)}")


@router.post("/chat-context")
async def get_chat_context(
    query: str = Body(..., embed=True),
    project_id: Optional[str] = Body(None, embed=True),
    limit: Optional[int] = Body(5, embed=True),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get relevant document chunks as context for a chat message.
    """
    try:
        # Get embedding service and vector store
        from ...services.embedding_service import get_embedding_service
        embedding_service = get_embedding_service()
        vector_store = get_vector_store(db, embedding_service)
        
        # Generate embedding for the query
        query_embedding = await vector_store.generate_embedding(query)
        
        # Perform similarity search
        results = vector_store.similarity_search(
            query_embedding=query_embedding,
            project_id=project_id,
            limit=limit,
            similarity_threshold=0.7
        )
        
        # Format results for context
        context_chunks = []
        for result in results:
            # Format each chunk as a context snippet
            context_chunks.append({
                "content": result["content"],
                "source": result["filename"],
                "similarity": float(result["similarity"]),
                "document_id": result["document_id"],
                "chunk_id": result["chunk_id"],
            })
        
        return {
            "context_chunks": context_chunks,
            "context_token_count": sum(len(c["content"].split()) for c in context_chunks)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat context: {str(e)}")