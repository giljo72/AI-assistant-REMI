# src/gradio/pages/help.py
import gradio as gr
import logging

logger = logging.getLogger(__name__)

class HelpPage:
    """Help page component"""
    
    def __init__(self):
        """Initialize the help page"""
        pass
    
    def render(self):
        """Render the help page"""
        gr.Markdown("## Help & Information")
        
        gr.Markdown("""
        **Welcome to AI Assistant!**
        
        This application helps you organize your documents and chat with an AI assistant that understands your files.
        
        **Navigation:**
        - 💬 **Chat**: Talk with the AI assistant
        - 📄 **Documents**: Manage your documents
        - ⚙️ **Settings**: Configure the application
        
        **Document Management:**
        - Upload documents in the Documents section
        - Tag documents as Private (P), Business (B), or Both (PB)
        - Attach documents to projects for better context
        
        **Projects:**
        - Create projects to organize related chats and documents
        - Add custom prompts to guide the AI assistant
        - Create multiple chats within each project
        
        **Need more help?**
        Refer to the documentation or contact support.
        """)