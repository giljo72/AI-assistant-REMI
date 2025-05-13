# src/gradio/components/project_forms.py
import gradio as gr
import logging
from typing import List, Dict, Any, Optional, Tuple

from src.services.project_service import ProjectService
from src.services.service_factory import service_factory

logger = logging.getLogger(__name__)

class ProjectForms:
    """Project management forms component with service layer integration"""
    
    def __init__(self):
        """Initialize the project forms"""
        self.create_project_form = None
        self.edit_project_form = None
        self.delete_project_form = None
        
        # Initialize project service
        self.project_service = service_factory.get_service('project_service')
        if not self.project_service:
            self.project_service = ProjectService()
    
    def render_create_form(self):
        """Render the create project form"""
        with gr.Group() as self.create_project_form:
            gr.Markdown("### Create New Project")
            
            project_name = gr.Textbox(
                label="Project Name", 
                placeholder="Enter project name...",
                value=""
            )
            
            project_description = gr.Textbox(
                label="Custom Prompt (Optional)", 
                placeholder="Enter custom AI instructions for this project...",
                lines=3,
                value=""
            )
            
            status_message = gr.Markdown("")
            
            with gr.Row():
                cancel_btn = gr.Button("Cancel", variant="secondary")
                create_btn = gr.Button("Create Project", variant="primary")
            
            # Connect event handlers
            create_btn.click(
                fn=self.create_project,
                inputs=[project_name, project_description],
                outputs=[project_name, project_description, status_message]
            )
        
        return self.create_project_form
    
    def render_edit_form(self):
        """Render the edit project form"""
        with gr.Group() as self.edit_project_form:
            gr.Markdown("### Edit Project")
            
            # Hidden field for project ID
            project_id = gr.Number(visible=False)
            
            # Dropdown for project selection
            project_selector = gr.Dropdown(
                label="Select Project",
                choices=self._get_project_choices(),
                value=None
            )
            
            project_name = gr.Textbox(
                label="Project Name", 
                placeholder="Enter new name...",
                value=""
            )
            
            project_prompt = gr.Textbox(
                label="Custom Prompt", 
                placeholder="Enter custom AI instructions for this project...",
                lines=3,
                value=""
            )
            
            status_message = gr.Markdown("")
            
            with gr.Row():
                cancel_btn = gr.Button("Cancel", variant="secondary")
                update_btn = gr.Button("Update Project", variant="primary")
            
            # Connect event handlers
            project_selector.change(
                fn=self.load_project,
                inputs=[project_selector],
                outputs=[project_id, project_name, project_prompt]
            )
            
            update_btn.click(
                fn=self.update_project,
                inputs=[project_id, project_name, project_prompt],
                outputs=[project_name, project_prompt, status_message]
            )
        
        return self.edit_project_form
    
    def render_delete_form(self):
        """Render the delete project form"""
        with gr.Group() as self.delete_project_form:
            gr.Markdown("### Delete Project")
            gr.Markdown("⚠️ **Warning**: This will permanently delete the project and all its chats. This action cannot be undone.")
            
            # Dropdown for project selection
            project_selector = gr.Dropdown(
                label="Select Project to Delete",
                choices=self._get_project_choices(),
                value=None
            )
            
            # Project info display
            project_info = gr.Markdown("")
            
            status_message = gr.Markdown("")
            
            with gr.Row():
                cancel_btn = gr.Button("Cancel", variant="secondary")
                delete_btn = gr.Button("Delete Project", variant="stop")
            
            # Connect event handlers
            project_selector.change(
                fn=self.get_project_info,
                inputs=[project_selector],
                outputs=[project_info]
            )
            
            delete_btn.click(
                fn=self.delete_project,
                inputs=[project_selector],
                outputs=[project_selector, project_info, status_message]
            )
        
        return self.delete_project_form
    
    def _get_project_choices(self) -> List[Tuple[str, int]]:
        """
        Get projects for dropdown selection
        
        Returns:
            List of tuples (project_name, project_id)
        """
        try:
            projects = self.project_service.get_all_projects()
            return [(p['name'], p['id']) for p in projects]
        except Exception as e:
            logger.error(f"Error getting project choices: {e}")
            return []
    
    def create_project(self, name: str, custom_prompt: str):
        """Create a new project"""
        if not name:
            return name, custom_prompt, "⚠️ Project name is required"
        
        try:
            # Create the project
            project = self.project_service.create_project(
                name=name, 
                custom_prompt=custom_prompt if custom_prompt else None
            )
            
            logger.info(f"Created project: {name} (ID: {project['id']})")
            
            # Clear the form and show success message
            return "", "", f"✅ Project '{name}' created successfully"
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return name, custom_prompt, f"❌ Error creating project: {str(e)}"
    
    def load_project(self, project_selector):
        """Load a project for editing"""
        if not project_selector:
            return None, "", ""
        
        try:
            # Get project ID from selector (project_name, project_id)
            project_id = project_selector
            
            # Get project details
            project = self.project_service.get_project(project_id)
            
            if not project:
                return None, "", ""
            
            return project['id'], project['name'], project.get('custom_prompt', "")
        except Exception as e:
            logger.error(f"Error loading project: {e}")
            return None, "", ""
    
    def update_project(self, project_id, name, custom_prompt):
        """Update an existing project"""
        if not project_id:
            return name, custom_prompt, "⚠️ No project selected"
        
        if not name:
            return name, custom_prompt, "⚠️ Project name is required"
        
        try:
            # Update the project
            project = self.project_service.update_project(
                project_id=project_id,
                name=name,
                custom_prompt=custom_prompt if custom_prompt else None
            )
            
            logger.info(f"Updated project ID {project_id}: {name}")
            
            # Show success message but keep the form filled
            return name, custom_prompt, f"✅ Project updated successfully"
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return name, custom_prompt, f"❌ Error updating project: {str(e)}"
    
    def get_project_info(self, project_selector):
        """Get project info for deletion confirmation"""
        if not project_selector:
            return ""
        
        try:
            # Get project ID from selector (project_name, project_id)
            project_id = project_selector
            
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
            logger.error(f"Error getting project info: {e}")
            return f"Error retrieving project information: {str(e)}"
    
    def delete_project(self, project_selector):
        """Delete a project"""
        if not project_selector:
            return project_selector, "", "⚠️ No project selected"
        
        try:
            # Get project ID from selector (project_name, project_id)
            project_id = project_selector
            
            # Get project name for the success message
            project = self.project_service.get_project(project_id)
            project_name = project['name'] if project else f"ID: {project_id}"
            
            # Delete the project
            success = self.project_service.delete_project(project_id)
            
            if success:
                logger.info(f"Deleted project ID {project_id}")
                # Clear the form and show success message
                return None, "", f"✅ Project '{project_name}' deleted successfully"
            else:
                logger.warning(f"Failed to delete project ID {project_id}")
                return project_selector, "", f"❌ Failed to delete project"
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return project_selector, "", f"❌ Error deleting project: {str(e)}"