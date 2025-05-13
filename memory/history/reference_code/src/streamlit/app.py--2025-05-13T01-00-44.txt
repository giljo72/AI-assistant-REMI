# src/streamlit/app.py
import streamlit as st
import logging
import os
from pathlib import Path
import sys

# Add parent directory to path to import project modules
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join('config', '.env'))

# Import core modules
from src.core.config import get_settings
from src.core.db_interface import initialize_engine
from src.core.llm_interface import OllamaInterface
from src.core.logger import Logger

# Import repositories
from src.db.repositories.document_repo import DocumentRepository
from src.db.repositories.project_repo import ProjectRepository
from src.db.repositories.chat_repo import ChatRepository
from src.db.repositories.vector_repo import VectorRepository

# Import document processing
from src.document_processing.file_manager import FileManager

# Import RAG components
from src.rag.embeddings import EmbeddingGenerator
from src.rag.retrieval import DocumentRetriever
from src.rag.generation import ResponseGenerator

# Import chat management
from src.chat.project_manager import ProjectManager
from src.chat.chat_manager import ChatManager

# Import pages
from src.streamlit.pages.chat import render_chat_page
from src.streamlit.pages.files import render_files_page
from src.streamlit.pages.view_document import render_view_document_page
from src.streamlit.pages.settings import render_settings_page

# Import components
from src.streamlit.components.project_sidebar import render_sidebar

# Initialize logger
custom_logger = Logger()

def main():
    """Main application entry point"""
    
    # Set page config
    st.set_page_config(
        page_title="AI Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Hide Streamlit's built-in multipage nav (those extra links)
    st.markdown("""
        <style>
        section[data-testid="stSidebarNav"] {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "active_project" not in st.session_state:
        st.session_state.active_project = None
    if "active_chat" not in st.session_state:
        st.session_state.active_chat = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Chat"
    if "response_metadata" not in st.session_state:
        st.session_state.response_metadata = {}
    if "show_new_project_form" not in st.session_state:
        st.session_state.show_new_project_form = False
    
    # Initialize database
    initialize_engine()
    
    # Load settings
    settings = get_settings()
    
    # Initialize repositories
    document_repo = DocumentRepository()
    project_repo = ProjectRepository()
    chat_repo = ChatRepository()
    vector_repo = VectorRepository()
    
    # Initialize file manager with custom logger
    file_manager = FileManager(document_repo, custom_logger)
    
    # Store file_manager in session state for access in components
    if 'file_manager' not in st.session_state:
        st.session_state.file_manager = file_manager
    
    # Initialize Ollama interface
    ollama_interface = OllamaInterface()
    
    # Initialize RAG components
    embedding_generator = EmbeddingGenerator(vector_repo)
    document_retriever = DocumentRetriever(vector_repo, project_repo, embedding_generator)
    response_generator = ResponseGenerator(ollama_interface, document_retriever, project_repo)
    
    # Initialize project and chat managers
    # Pass document_repo to ProjectManager to enable document detachment when projects are deleted
    project_manager = ProjectManager(project_repo, chat_repo, document_repo)
    chat_manager = ChatManager(chat_repo, response_generator)
    
    # Render sidebar
    render_sidebar(project_manager)
    
    # Define navigation
    pages = {
        "Chat": lambda: render_chat_page(chat_manager, document_repo),
        "Files": lambda: render_files_page(file_manager, project_repo),
        "Settings": lambda: render_settings_page(custom_logger, ollama_interface)
    }
    
    # Check for view_document query parameter
    query_params = st.query_params
    
    if "view_document" in query_params:
        doc_id = query_params.get("view_document")
        
        if doc_id and doc_id[0].isdigit():
            render_view_document_page(int(doc_id[0]))
            return
    
    # Also check for document_id parameter (for backward compatibility)
    if "document_id" in query_params:
        doc_id = query_params.get("document_id")
        
        if doc_id and doc_id[0].isdigit():
            render_view_document_page(int(doc_id[0]))
            return
    
    # Check if the URL path contains specific page identifiers
    url_path = str(st.query_params)
    
    # Handle direct navigation to /files, /settings, etc.
    if '/files' in url_path:
        st.session_state.active_page = "Files"
    elif '/settings' in url_path:
        st.session_state.active_page = "Settings"
    elif '/chat' in url_path:
        st.session_state.active_page = "Chat"
    
    # Also check the nav parameter
    nav_param = query_params.get("nav", None)
    if nav_param and nav_param[0] in ["Files", "Settings", "Chat"]:
        st.session_state.active_page = nav_param[0]
    
    # Get active page from session state or default to Chat
    active_page = st.session_state.get('active_page', 'Chat')
    
    # If active_page is not in pages, default to Chat
    if active_page not in pages:
        active_page = 'Chat'
    
    # Render the active page
    try:
        pages[active_page]()
    except Exception as e:
        st.error(f"Error rendering page: {e}")
        logging.error(f"Error rendering page {active_page}: {e}", exc_info=True)

if __name__ == "__main__":
    main()