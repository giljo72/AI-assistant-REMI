# src/gradio/components/chat_modal.py
import gradio as gr
import logging
from typing import List, Dict, Any, Optional, Tuple, Callable

from src.services.project_service import ProjectService
from src.services.service_factory import service_factory

logger = logging.getLogger(__name__)

class ChatModal:
    """Chat modal component for creating and managing chats within projects"""
    
    def __init__(self):
        """Initialize the chat modal"""
        # UI components
        self.create_modal = None
        self.edit_modal = None
        self.delete_modal = None
        
        # Initialize services
        self.project_service = service_factory.get_service('project_service')
        if not self.project_service:
            self.project_service = ProjectService()
    
    def render_create_modal(self, refresh_callback: Optional[Callable] = None):
        """
        Render the create chat modal
        
        Args:
            refresh_callback: Optional callback to refresh the projects list after creation
            
        Returns:
            Modal component
        """
        with gr.Group(visible=False, elem_id="create-chat-modal") as self.create_modal:
            gr.Markdown("## Create New Chat")
            
            # Hidden project ID field
            project_id = gr.Number(visible=False)
            
            # Display project name
            project_name = gr.Markdown("")
            
            chat_name = gr.Textbox(
                label="Chat Name", 
                placeholder="Enter chat name...",
                value=""
            )
            
            status_message = gr.Markdown("")
            
            with gr.Row():
                cancel_btn = gr.Button("Cancel", variant="secondary")
                create_btn = gr.Button("Create Chat", variant="primary")
            
            # Connect event handlers
            create_btn.click(
                fn=self.create_chat,
                inputs=[project_id, chat_name],
                outputs=[chat_name, status_message, self.create_modal]
            )
            
            cancel_btn.click(
                fn=lambda: (gr.update(value=""), gr.update(value=""), gr.update(visible=False)),
                outputs=[chat_name, status_message, self.create_modal]
            )
        
        return self.create_modal, project_id, project_name
    
    def render_edit_modal(self, refresh_callback: Optional[Callable] = None):
        """
        Render the edit chat modal
        
        Args:
            refresh_callback: Optional callback to refresh the projects list after editing
            
        Returns:
            Modal component
        """
        with gr.Group(visible=False, elem_id="edit-chat-modal") as self.edit_modal:
            gr.Markdown("## Edit Chat")
            
            # Hidden fields
            chat_id = gr.Number(visible=False)
            project_id = gr.Number(visible=False)
            
            # Display project name
            project_name = gr.Markdown("")
            
            chat_name = gr.Textbox(
                label="Chat Name", 
                placeholder="Enter chat name...",
                value=""
            )
            
            status_message = gr.Markdown("")
            
            with gr.Row():
                cancel_btn = gr.Button("Cancel", variant="secondary")
                update_btn = gr.Button("Update Chat", variant="primary")
            
            # Connect event handlers
            update_btn.click(
                fn=self.rename_chat,
                inputs=[chat_id, chat_name],
                outputs=[chat_name, status_message, self.edit_modal]
            )
            
            cancel_btn.click(
                fn=lambda: (gr.update(value=""), gr.update(value=""), gr.update(visible=False)),
                outputs=[chat_name, status_message, self.edit_modal]
            )
        
        return self.edit_modal, chat_id, project_id, chat_name, project_name
    
    def render_delete_modal(self, refresh_callback: Optional[Callable] = None):
        """
        Render the delete chat modal
        
        Args:
            refresh_callback: Optional callback to refresh the projects list after deletion
            
        Returns:
            Modal component
        """
        with gr.Group(visible=False, elem_id="delete-chat-modal") as self.delete_modal:
            gr.Markdown("## Delete Chat")
            gr.Markdown("⚠️ **Warning**: This will permanently delete this chat and all its messages. This action cannot be undone.")
            
            # Hidden fields
            chat_id = gr.Number(visible=False)
            project_id = gr.Number(visible=False)
            
            # Chat info display
            chat_info = gr.Markdown("")
            
            status_message = gr.Markdown("")
            
            with gr.Row():
                cancel_btn = gr.Button("Cancel", variant="secondary")
                delete_btn = gr.Button("Delete Chat", variant="stop")
            
            # Connect event handlers
            delete_btn.click(
                fn=self.delete_chat,
                inputs=[chat_id],
                outputs=[status_message, self.delete_modal]
            )
            
            cancel_btn.click(
                fn=lambda: (gr.update(value=""), gr.update(visible=False)),
                outputs=[status_message, self.delete_modal]
            )
        
        return self.delete_modal, chat_id, project_id, chat_info
    
    def create_chat(self, project_id: int, name: str):
        """
        Create a new chat in a project
        
        Args:
            project_id: ID of project to create chat in
            name: Chat name
            
        Returns:
            Tuple of (cleared name, status message, modal visibility)
        """
        if not project_id:
            return name, "⚠️ No project selected", gr.update(visible=True)
        
        if not name or not name.strip():
            return name, "⚠️ Chat name is required", gr.update(visible=True)
        
        try:
            # Create the chat
            chat = self.project_service.create_chat(
                project_id=project_id,
                name=name
            )
            
            logger.info(f"Created chat: {name} in project {project_id} (ID: {chat['id']})")
            
            # Clear the form and close the modal
            return "", f"✅ Chat '{name}' created successfully", gr.update(visible=False)
        except Exception as e:
            logger.error(f"Error creating chat: {e}")
            return name, f"❌ Error creating chat: {str(e)}", gr.update(visible=True)
    
    def rename_chat(self, chat_id: int, name: str):
        """
        Rename a chat
        
        Args:
            chat_id: ID of chat to rename
            name: New chat name
            
        Returns:
            Tuple of (cleared name, status message, modal visibility)
        """
        if not chat_id:
            return name, "⚠️ No chat selected", gr.update(visible=True)
        
        if not name or not name.strip():
            return name, "⚠️ Chat name is required", gr.update(visible=True)
        
        try:
            # Rename the chat
            chat = self.project_service.rename_chat(
                chat_id=chat_id,
                name=name
            )
            
            logger.info(f"Renamed chat ID {chat_id} to '{name}'")
            
            # Clear the form and close the modal
            return "", f"✅ Chat renamed successfully", gr.update(visible=False)
        except Exception as e:
            logger.error(f"Error renaming chat: {e}")
            return name, f"❌ Error renaming chat: {str(e)}", gr.update(visible=True)
    
    def delete_chat(self, chat_id: int):
        """
        Delete a chat
        
        Args:
            chat_id: ID of chat to delete
            
        Returns:
            Tuple of (status message, modal visibility)
        """
        if not chat_id:
            return "⚠️ No chat selected", gr.update(visible=True)
        
        try:
            # Delete the chat
            success = self.project_service.delete_chat(chat_id)
            
            if success:
                logger.info(f"Deleted chat ID {chat_id}")
                # Clear the form and close the modal
                return f"✅ Chat deleted successfully", gr.update(visible=False)
            else:
                logger.warning(f"Failed to delete chat ID {chat_id}")
                return f"❌ Failed to delete chat", gr.update(visible=True)
        except Exception as e:
            logger.error(f"Error deleting chat: {e}")
            return f"❌ Error deleting chat: {str(e)}", gr.update(visible=True)
    
    def load_project_for_create_chat(self, project_id: int):
        """
        Load a project for creating a new chat
        
        Args:
            project_id: ID of project to load
            
        Returns:
            Tuple of (project ID, project name)
        """
        try:
            # Get project details
            project = self.project_service.get_project(project_id)
            
            if project:
                return project_id, f"Creating a new chat in project: **{project['name']}**"
            else:
                return None, "Project not found"
        except Exception as e:
            logger.error(f"Error loading project for create chat: {e}")
            return None, f"Error loading project: {str(e)}"