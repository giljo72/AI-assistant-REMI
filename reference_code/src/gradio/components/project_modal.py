# src/gradio/components/project_modal.py
import gradio as gr
import logging
from typing import List, Dict, Any, Optional, Tuple, Callable

from src.services.project_service import ProjectService
from src.services.service_factory import service_factory

logger = logging.getLogger(__name__)

class ProjectModal:
    """Project modal component for creating and editing projects"""
    
    def __init__(self):
        """Initialize the project modal"""
        # UI components
        self.create_modal = None
        self.edit_modal = None
        self.delete_modal = None
        
        # Initialize project service
        self.project_service = service_factory.get_service('project_service')
        if not self.project_service:
            self.project_service = ProjectService()
    
    def render_create_modal(self, refresh_callback: Optional[Callable] = None):
        """
        Render the create project modal
        
        Args:
            refresh_callback: Optional callback to refresh the projects list after creation
            
        Returns:
            Modal component
        """
        with gr.Group(visible=False, elem_id="create-project-modal") as self.create_modal:
            gr.Markdown("## Create New Project")
            
            project_name = gr.Textbox(
                label="Project Name", 
                placeholder="Enter project name...",
                value=""
            )
            
            project_prompt = gr.TextArea(
                label="Custom Prompt (Optional)", 
                placeholder="Enter custom AI instructions for this project...",
                value="",
                lines=5
            )
            
            status_message = gr.Markdown("")
            
            with gr.Row():
                cancel_btn = gr.Button("Cancel", variant="secondary")
                create_btn = gr.Button("Create Project", variant="primary")
            
            # Connect event handlers
            create_btn.click(
                fn=self.create_project,
                inputs=[project_name, project_prompt],
                outputs=[project_name, project_prompt, status_message, self.create_modal]
            )
            
            cancel_btn.click(
                fn=lambda: (gr.update(value=""), gr.update(value=""), gr.update(value=""), gr.update(visible=False)),
                outputs=[project_name, project_prompt, status_message, self.create_modal]
            )
        
        return self.create_modal
    
    def render_edit_modal(self, refresh_callback: Optional[Callable] = None):
        """
        Render the edit project modal
        
        Args:
            refresh_callback: Optional callback to refresh the projects list after editing
            
        Returns:
            Modal component
        """
        with gr.Group(visible=False, elem_id="edit-project-modal") as self.edit_modal:
            gr.Markdown("## Edit Project")
            
            # Hidden field for project ID
            project_id = gr.Number(visible=False)
            
            project_name = gr.Textbox(
                label="Project Name", 
                placeholder="Enter project name...",
                value=""
            )
            
            project_prompt = gr.TextArea(
                label="Custom Prompt", 
                placeholder="Enter custom AI instructions for this project...",
                value="",
                lines=5
            )
            
            status_message = gr.Markdown("")
            
            with gr.Row():
                cancel_btn = gr.Button("Cancel", variant="secondary")
                update_btn = gr.Button("Update Project", variant="primary")
            
            # Connect event handlers
            update_btn.click(
                fn=self.update_project,
                inputs=[project_id, project_name, project_prompt],
                outputs=[project_name, project_prompt, status_message, self.edit_modal]
            )
            
            cancel_btn.click(
                fn=lambda: (gr.update(value=""), gr.update(value=""), gr.update(value=""), gr.update(visible=False)),
                outputs=[project_name, project_prompt, status_message, self.edit_modal]
            )
        
        return self.edit_modal, project_id, project_name, project_prompt
    
    def render_delete_modal(self, refresh_callback: Optional[Callable] = None):
        """
        Render the delete project modal
        
        Args:
            refresh_callback: Optional callback to refresh the projects list after deletion
            
        Returns:
            Modal component
        """
        with gr.Group(visible=False, elem_id="delete-project-modal") as self.delete_modal:
            gr.Markdown("## Delete Project")
            gr.Markdown("⚠️ **Warning**: This will permanently delete the project and all its chats. This action cannot be undone.")
            
            # Hidden field for project ID
            project_id = gr.Number(visible=False)
            
            # Project info display
            project_info = gr.Markdown("")
            
            status_message = gr.Markdown("")
            
            with gr.Row():
                cancel_btn = gr.Button("Cancel", variant="secondary")
                delete_btn = gr.Button("Delete Project", variant="stop")
            
            # Connect event handlers
            delete_btn.click(
                fn=self.delete_project,
                inputs=[project_id],
                outputs=[status_message, self.delete_modal]
            )
            
            cancel_btn.click(
                fn=lambda: (gr.update(value=""), gr.update(visible=False)),
                outputs=[status_message, self.delete_modal]
            )
        
        return self.delete_modal, project_id, project_info
    
    def create_project(self, name: str, custom_prompt: str):
        """
        Create a new project
        
        Args:
            name: Project name
            custom_prompt: Custom prompt for the project
            
        Returns:
            Tuple of (cleared name, cleared prompt, status message, modal visibility)
        """
        if not name or not name.strip():
            return name, custom_prompt, "⚠️ Project name is required", gr.update(visible=True)
        
        try:
            # Create the project
            project = self.project_service.create_project(
                name=name, 
                custom_prompt=custom_prompt if custom_prompt else None
            )
            
            logger.info(f"Created project: {name} (ID: {project['id']})")
            
            # Clear the form and close the modal
            return "", "", f"✅ Project '{name}' created successfully", gr.update(visible=False)
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return name, custom_prompt, f"❌ Error creating project: {str(e)}", gr.update(visible=True)
    
    def update_project(self, project_id: int, name: str, custom_prompt: str):
        """
        Update a project
        
        Args:
            project_id: ID of project to update
            name: New project name
            custom_prompt: New custom prompt
            
        Returns:
            Tuple of (cleared name, cleared prompt, status message, modal visibility)
        """
        if not project_id:
            return name, custom_prompt, "⚠️ No project selected", gr.update(visible=True)
        
        if not name or not name.strip():
            return name, custom_prompt, "⚠️ Project name is required", gr.update(visible=True)
        
        try:
            # Update the project
            project = self.project_service.update_project(
                project_id=project_id,
                name=name,
                custom_prompt=custom_prompt if custom_prompt else None
            )
            
            logger.info(f"Updated project ID {project_id}: {name}")
            
            # Clear the form and close the modal
            return "", "", f"✅ Project updated successfully", gr.update(visible=False)
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return name, custom_prompt, f"❌ Error updating project: {str(e)}", gr.update(visible=True)
    
    def delete_project(self, project_id: int):
        """
        Delete a project
        
        Args:
            project_id: ID of project to delete
            
        Returns:
            Tuple of (status message, modal visibility)
        """
        if not project_id:
            return "⚠️ No project selected", gr.update(visible=True)
        
        try:
            # Get project name for the message
            project = self.project_service.get_project(project_id)
            project_name = project['name'] if project else f"ID: {project_id}"
            
            # Delete the project
            success = self.project_service.delete_project(project_id)
            
            if success:
                logger.info(f"Deleted project ID {project_id}")
                # Clear the form and close the modal
                return f"✅ Project '{project_name}' deleted successfully", gr.update(visible=False)
            else:
                logger.warning(f"Failed to delete project ID {project_id}")
                return f"❌ Failed to delete project", gr.update(visible=True)
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return f"❌ Error deleting project: {str(e)}", gr.update(visible=True)
    
    def load_project_for_edit(self, project_id: int):
        """
        Load a project for editing
        
        Args:
            project_id: ID of project to load
            
        Returns:
            Tuple of (project ID, project name, project prompt)
        """
        try:
            # Get project details
            project = self.project_service.get_project(project_id)
            
            if project:
                return project['id'], project['name'], project.get('custom_prompt', "")
            else:
                return None, "", ""
        except Exception as e:
            logger.error(f"Error loading project: {e}")
            return None, "", ""
    
    def load_project_for_delete(self, project_id: int):
        """
        Load a project for deletion confirmation
        
        Args:
            project_id: ID of project to load
            
        Returns:
            Project info HTML
        """
        try:
            # Get project details
            project = self.project_service.get_project(project_id)
            
            if not project:
                return "Project not found"
            
            # Get chat count
            chat_count = len(project.get('chats', []))
            
            # Get document count
            doc_count = project.get('document_count', 0)
            
            # Format info
            info = f"""
            **Project Details**
            
            - **Name**: {project['name']}
            - **Chats**: {chat_count}
            - **Documents**: {doc_count}
            - **Created**: {project.get('created_at', 'Unknown')}
            
            This will delete the project and all its chats.
            """
            
            return info
        except Exception as e:
            logger.error(f"Error loading project for deletion: {e}")
            return f"Error retrieving project information: {str(e)}"