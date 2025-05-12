# src/services/rag_service.py
import logging
from typing import List, Dict, Any, Optional

from ..rag.retrieval import DocumentRetriever
from ..rag.generation import ResponseGenerator
from .service_factory import service_factory

logger = logging.getLogger(__name__)

class RAGService:
    """Service for RAG operations"""
    
    def __init__(self):
        """Initialize the RAG service"""
        self.document_retriever = service_factory.get_service('document_retriever')
        self.response_generator = service_factory.get_service('response_generator')
    
    # RAG service methods will be implemented as needed