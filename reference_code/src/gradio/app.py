# src/gradio/app.py
import gradio as gr
import os
import sys
from pathlib import Path
import logging

# Add parent directory to path to import project modules
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
env_path = project_root / "config" / ".env"
if env_path.exists():
    logger.info(f"Loading environment from: {env_path}")
    load_dotenv(env_path)
else:
    logger.warning(f"Environment file not found at: {env_path}")

# Import database interface
from src.core.db_interface import initialize_engine, check_connection, check_vector_extension

# Import pages
from src.gradio.pages.chat import ChatPage
from src.gradio.pages.files import FilesPage
from src.gradio.pages.settings import SettingsPage
from src.gradio.pages.help import HelpPage

# Import components
from src.gradio.components.project_sidebar import create_sidebar
from src.gradio.utils.theme import create_theme

# Import custom CSS
from src.gradio.utils.custom_css import get_custom_css

def create_app():
    """Create and configure the Gradio application"""
    # Initialize database with proper error handling
    try:
        logger.info("Initializing database connection...")
        db_initialized = initialize_engine()
        
        if not db_initialized:
            logger.warning("Database initialization returned False. Some features may not work correctly.")
        else:
            logger.info("Database engine successfully initialized")
            
            # Verify database connection is working
            if check_connection():
                logger.info("Database connection verified")
            else:
                logger.warning("Database connection check failed. Some features may not work correctly.")
                
            # Verify pgvector extension is available
            if check_vector_extension():
                logger.info("pgvector extension verified")
            else:
                logger.warning("pgvector extension not found. Vector search functionality will not work.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        logger.warning("Application will start but database features may not be available")
    
    # Initialize pages
    chat_page = ChatPage()
    
    # Create theme
    theme = create_theme()
    
    # Get custom CSS
    custom_css = get_custom_css()
    
    # Create a Blocks application
    with gr.Blocks(title="AI Assistant", theme=theme, css=custom_css) as app:
        # Application state
        current_project_id = gr.State(None)
        current_chat_id = gr.State(None)
        
        # Create a two-column layout: sidebar and main content
        with gr.Row():
            # Left sidebar for project navigation
            sidebar_component, nav_buttons = create_sidebar()
            
            # Main content area
            with gr.Column(scale=4):
                # Render chat page
                chat_page.render()
        
    return app

if __name__ == "__main__":
    try:
        logger.info("Starting AI Assistant application...")
        app = create_app()
        app.launch(
            server_name="0.0.0.0",  # Makes app available on LAN
            share=False,            # Disables public sharing
            show_error=True         # Shows detailed errors for debugging
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)