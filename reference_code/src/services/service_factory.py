# src/services/service_factory.py
import logging
from typing import Dict, Any

from ..core.logger import Logger
from ..core.llm_interface import OllamaInterface
from ..db.repositories.document_repo import DocumentRepository
from ..db.repositories.project_repo import ProjectRepository
from ..db.repositories.chat_repo import ChatRepository
from ..db.repositories.vector_repo import VectorRepository
from ..document_processing.file_manager import FileManager
from ..rag.embeddings import EmbeddingGenerator
from ..rag.retrieval import DocumentRetriever
from ..rag.generation import ResponseGenerator
from ..chat.project_manager import ProjectManager
from ..chat.chat_manager import ChatManager

logger = logging.getLogger(__name__)

class ServiceFactory:
    """Factory for creating service instances"""
    
    def __init__(self):
        """Initialize the service factory"""
        self.services = {}
        self.repos = {}
        self.initialized = False
    
    def initialize(self):
        """Initialize all services"""
        if self.initialized:
            return
        
        try:
            # Create custom logger
            custom_logger = Logger()
            
            # Create repositories
            doc_repo = DocumentRepository()
            project_repo = ProjectRepository()
            chat_repo = ChatRepository()
            vector_repo = VectorRepository()
            
            # Store repositories
            self.repos = {
                'document_repo': doc_repo,
                'project_repo': project_repo,
                'chat_repo': chat_repo,
                'vector_repo': vector_repo
            }
            
            # Create LLM interface
            ollama = OllamaInterface()
            
            # Create core components
            file_manager = FileManager(doc_repo, custom_logger)
            embedding_generator = EmbeddingGenerator(vector_repo)
            document_retriever = DocumentRetriever(vector_repo, project_repo, embedding_generator)
            response_generator = ResponseGenerator(ollama, document_retriever, project_repo)
            project_manager = ProjectManager(project_repo, chat_repo, doc_repo)
            chat_manager = ChatManager(chat_repo, response_generator)
            
            # Store services
            self.services = {
                'file_manager': file_manager,
                'project_manager': project_manager,
                'chat_manager': chat_manager,
                'document_retriever': document_retriever,
                'response_generator': response_generator,
                'embedding_generator': embedding_generator,
                'ollama': ollama,
                'logger': custom_logger
            }
            
            self.initialized = True
            logger.info("Service factory initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing service factory: {e}")
            self.initialized = False
    
    def get_service(self, service_name):
        """Get a service by name"""
        if not self.initialized:
            self.initialize()
        
        if service_name in self.services:
            return self.services[service_name]
        else:
            logger.error(f"Service {service_name} not found")
            return None
    
    def get_repository(self, repo_name):
        """Get a repository by name"""
        if not self.initialized:
            self.initialize()
        
        if repo_name in self.repos:
            return self.repos[repo_name]
        else:
            logger.error(f"Repository {repo_name} not found")
            return None

# Create a singleton instance
service_factory = ServiceFactory()