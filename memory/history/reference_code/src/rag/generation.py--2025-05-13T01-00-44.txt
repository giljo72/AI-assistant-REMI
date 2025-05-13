# src/rag/generation.py
from typing import List, Dict, Any, Optional, Tuple
import logging

from ..core.llm_interface import OllamaInterface
from ..core.config import get_settings
from ..db.repositories.project_repo import ProjectRepository
from .retrieval import DocumentRetriever

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generates responses using the LLM with retrieved context"""
    
    def __init__(self, 
                ollama_interface: OllamaInterface,
                document_retriever: DocumentRetriever,
                project_repo: ProjectRepository):
        """
        Initialize the response generator
        
        Args:
            ollama_interface: Interface for LLM API
            document_retriever: Retriever for document chunks
            project_repo: Repository for project operations
        """
        self.ollama = ollama_interface
        self.retriever = document_retriever
        self.project_repo = project_repo
        self.settings = get_settings()
        
        # Default system prompt
        self.default_system_prompt = """You are an AI assistant with access to specific documents provided by the user.
Base your answers primarily on the document context provided.
If the context doesn't contain the information needed, clearly state that you don't have that information.
Keep your responses concise and focused on the query.
Cite specific documents when drawing information from them."""
    
    def generate_response(self, 
                         query: str, 
                         project_id: Optional[int] = None,
                         chat_history: Optional[List[Dict[str, Any]]] = None,
                         temperature: float = 0.7,
                         document_ids: Optional[List[int]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a response for a query with optional project and chat history
        
        Args:
            query: Query text
            project_id: Optional project ID for context
            chat_history: Optional chat history for context
            temperature: Temperature for response generation
            document_ids: Optional list of document IDs to prioritize in retrieval
            
        Returns:
            Tuple of (response text, metadata)
        """
        metadata = {
            "docs_applied": False,
            "prompt_applied": False,
            "manual_doc_selection": False,
            "combined_retrieval": False,
            "retrieval_strategy": "auto"
        }
        
        # Get custom prompt from project if specified
        system_prompt = self.default_system_prompt
        if project_id:
            project = self.project_repo.get_project(project_id)
            if project and project.get('custom_prompt'):
                system_prompt = project['custom_prompt']
                metadata["prompt_applied"] = True
        
        # Determine retrieval strategy and get document chunks
        retrieved_chunks = []
        top_k = self.settings['rag'].get('top_k_retrieval', 5)
        
        if document_ids and len(document_ids) > 0:
            # Manual document selection - retrieve from specified documents
            logger.info(f"Using manual document selection with IDs: {document_ids}")
            retrieved_chunks = self.retriever.retrieve_from_documents(
                query=query,
                document_ids=document_ids,
                limit=top_k
            )
            metadata["manual_doc_selection"] = True
            metadata["retrieval_strategy"] = "manual"
            
            # If manual selection doesn't yield enough results, supplement with project retrieval
            if len(retrieved_chunks) < 3 and project_id:
                logger.info("Supplementing manual selection with project documents")
                # Exclude already retrieved document IDs
                retrieved_doc_ids = [chunk.get('document_id') for chunk in retrieved_chunks]
                project_docs = self.project_repo.get_project_documents(project_id)
                
                if project_docs:
                    # Filter out already retrieved docs
                    additional_doc_ids = [
                        doc['id'] for doc in project_docs 
                        if doc['id'] not in retrieved_doc_ids and doc['id'] not in document_ids
                    ]
                    
                    if additional_doc_ids:
                        # Get additional chunks from project documents
                        additional_chunks = self.retriever.retrieve_from_documents(
                            query=query,
                            document_ids=additional_doc_ids,
                            limit=top_k - len(retrieved_chunks)
                        )
                        
                        if additional_chunks:
                            # Mark as combined retrieval and add additional chunks
                            metadata["combined_retrieval"] = True
                            retrieved_chunks.extend(additional_chunks)
        else:
            # Automatic retrieval based on project
            logger.info(f"Using automatic document retrieval for project: {project_id}")
            retrieved_chunks = self.retriever.retrieve_for_query(
                query=query,
                project_id=project_id,
                limit=top_k
            )
            metadata["retrieval_strategy"] = "project" if project_id else "all"
        
        # Sort chunks by relevance
        retrieved_chunks = sorted(retrieved_chunks, key=lambda x: x.get('similarity', 0), reverse=True)
        
        # Format documents as context
        document_context = ""
        if retrieved_chunks:
            document_context = self.retriever.format_context(retrieved_chunks)
            metadata["docs_applied"] = True
        
        # Construct the final prompt
        final_prompt = query
        
        if document_context:
            final_prompt = f"""I need information based on the following documents:

{document_context}

My question is: {query}"""
        
        # Prepare chat history context if provided
        context = None
        if chat_history:
            # Format as list of tokens for Ollama context
            context = self._format_chat_history(chat_history)
        
        # Generate the response
        response = self.ollama.generate(
            prompt=final_prompt,
            system_prompt=system_prompt,
            context=context,
            temperature=temperature,
            max_tokens=self.settings['model'].get('max_tokens', 1000)
        )
        
        # Enhance retrieved chunks with additional metadata for visualization
        enhanced_chunks = []
        for i, chunk in enumerate(retrieved_chunks):
            # Calculate normalized relevance (percentage of highest relevance)
            max_similarity = retrieved_chunks[0].get('similarity', 1.0) if retrieved_chunks else 1.0
            normalized_relevance = chunk.get('similarity', 0) / max_similarity if max_similarity > 0 else 0
            
            # Enhance with additional metadata
            enhanced_chunk = chunk.copy()
            enhanced_chunk.update({
                "rank": i + 1,
                "normalized_relevance": normalized_relevance,
                "relevance_tier": self._get_relevance_tier(chunk.get('similarity', 0)),
                "selection_type": "manual" if chunk.get('document_id') in (document_ids or []) else "auto"
            })
            enhanced_chunks.append(enhanced_chunk)
        
        # Add enhanced chunks to metadata
        metadata["retrieved_chunks"] = enhanced_chunks
        metadata["chunk_count"] = len(enhanced_chunks)
        
        return response, metadata
    
    def _format_chat_history(self, chat_history: List[Dict[str, Any]]) -> List[str]:
        """
        Format chat history for Ollama context
        
        Args:
            chat_history: List of chat messages
            
        Returns:
            Formatted context tokens
        """
        # Simple formatting - this may need to be adapted based on LLM requirements
        formatted_messages = []
        
        for msg in chat_history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'user':
                formatted_messages.append(f"Human: {content}")
            else:
                formatted_messages.append(f"Assistant: {content}")
        
        return formatted_messages
    
    def _get_relevance_tier(self, similarity: float) -> str:
        """
        Categorize relevance score into tiers for visualization
        
        Args:
            similarity: Similarity score (0-1)
            
        Returns:
            Relevance tier (high, medium, low)
        """
        if similarity >= 0.8:
            return "high"
        elif similarity >= 0.6:
            return "medium"
        else:
            return "low"