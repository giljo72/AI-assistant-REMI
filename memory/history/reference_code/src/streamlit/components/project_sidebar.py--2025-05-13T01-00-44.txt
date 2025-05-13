# src/streamlit/components/project_sidebar.py
import streamlit as st
import time
from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

from src.chat.project_manager import ProjectManager

def render_sidebar(project_manager: ProjectManager):
    """
    Render the sidebar with projects and their chats
    
    Args:
        project_manager: ProjectManager instance
    """
    with st.sidebar:
        st.title("AI Assistant")
        
        # Create new project button - using the standard styling
        if st.button("New Project", key="new_project_btn", use_container_width=True):
            # Show a form for creating a new project
            st.session_state.show_new_project_form = True
        
        # New project form
        if st.session_state.get("show_new_project_form", False):
            with st.form("new_project_form"):
                project_name = st.text_input("Project Name:")
                custom_prompt = st.text_area("Custom Prompt (Optional):")
                
                submit_col, cancel_col = st.columns(2)
                with submit_col:
                    if st.form_submit_button("Create"):
                        if project_name:
                            try:
                                new_project = project_manager.create_project(
                                    name=project_name,
                                    custom_prompt=custom_prompt if custom_prompt else None
                                )
                                
                                st.session_state.active_project = new_project['id']
                                st.session_state.show_new_project_form = False
                                st.success(f"Project '{project_name}' created!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error creating project: {str(e)}")
                
                with cancel_col:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_new_project_form = False
                        st.rerun()
        
        # Navigation
        st.subheader("Navigation")
        nav_cols = st.columns(4)  # 4 columns for navigation icons
        
        with nav_cols[0]:
            if st.button("💬", help="Chat", use_container_width=True, key="nav_chat_btn"):
                st.session_state.active_page = "Chat"
                # Update URL to reflect the page change
                st.query_params.update({"nav": "Chat"})
                st.rerun()
        
        with nav_cols[1]:
            if st.button("📄", help="Documents", use_container_width=True, key="nav_docs_btn"):
                st.session_state.active_page = "Files"
                # Update URL to reflect the page change
                st.query_params.update({"nav": "Files"})
                st.rerun()
        
        with nav_cols[2]:
            if st.button("⚙️", help="Settings", use_container_width=True, key="nav_settings_btn"):
                st.session_state.active_page = "Settings"
                # Update URL to reflect the page change
                st.query_params.update({"nav": "Settings"})
                st.rerun()
        
        with nav_cols[3]:
            if st.button("❓", help="Help", use_container_width=True, key="nav_help_btn"):
                # Set a session state variable to show help information
                st.session_state.show_help = True
                st.rerun()
        
        # Projects list
        st.subheader("Projects")
        
        # Get projects
        projects = project_manager.get_all_projects()
        
        if not projects:
            st.caption("No projects yet")
        else:
            # Only show max 15 projects before scrolling
            with st.container():
                for project in projects:
                    # Project container
                    with st.container():
                        # Updated layout for project rows - all buttons in same row
                        col1, col2, col3, col4 = st.columns([8, 1, 1, 1])
                        
                        with col1:
                            # Project name - bold if active
                            is_active = st.session_state.get('active_project') == project['id']
                            is_expanded = st.session_state.get(f"expand_project_{project['id']}", is_active)
                            
                            # Show expand/collapse indicator
                            indicator = "▼ " if is_expanded else "► "
                            
                            # Make bold if active
                            name_display = project['name']
                            if len(name_display) > 20:
                                name_display = name_display[:17] + "..."
                                
                            if is_active:
                                name_display = f"**{name_display}**"
                            
                            # Click to select and expand/collapse
                            if st.button(f"{indicator}{name_display}", key=f"project_{project['id']}_btn", use_container_width=True):
                                st.session_state.active_project = project['id']
                                # Toggle expanded state
                                is_expanded = not is_expanded
                                st.session_state[f"expand_project_{project['id']}"] = is_expanded
                                st.rerun()
                        
                        with col2:
                            # Document button (document icon) - smaller size
                            if st.button("📄", key=f"project_{project['id']}_docs_btn", help="Project Documents"):
                                st.session_state.viewing_project_docs = project['id']
                                # Switch to a document management view for this project
                                st.session_state.active_page = "Files"
                                # Add project filter to query params
                                st.query_params.update({"nav": "Files", "project": project['id']})
                                st.rerun()
                        
                        with col3:
                            # Edit button (gear icon) - smaller size
                            if st.button("⚙️", key=f"project_{project['id']}_edit_btn", help="Edit Project"):
                                st.session_state.editing_project = project['id']
                                st.rerun()
                        
                        with col4:
                            # Delete button (trash icon) - smaller size
                            if st.button("🗑️", key=f"project_{project['id']}_delete_btn", help="Delete Project"):
                                st.session_state.deleting_project = project['id']
                                st.rerun()
                        
                        # Show chats if project is expanded
                        if is_expanded:
                            # Get chats for this project
                            chats = project_manager.get_project_chats(project['id'])
                            
                            # Add new chat row with same structure as project row
                            add_col1, add_col2, add_col3, add_col4 = st.columns([8, 1, 1, 1])
                            
                            with add_col2:
                                # Yellow plus button aligned with other action buttons
                                if st.button("➕", key=f"project_{project['id']}_add_chat_btn", help="Add Chat"):
                                    st.session_state.adding_chat_to_project = project['id']
                                    st.rerun()
                            
                            # Show chats with indentation and thinner design
                            for chat in chats:
                                # Create a container for the whole chat line with same column structure
                                with st.container():
                                    # Use same column structure for consistency
                                    chat_col1, chat_col2, chat_col3, chat_col4 = st.columns([8, 1, 1, 1])
                                    
                                    with chat_col1:
                                        # Truncate chat names if needed
                                        chat_name = chat['name']
                                        if len(chat_name) > 25:
                                            chat_name = chat_name[:22] + "..."
                                        
                                        # Make active chat bold
                                        is_active_chat = st.session_state.get('active_chat') == chat['id']
                                        if is_active_chat:
                                            chat_name = f"**{chat_name}**"
                                        
                                        # Chat button with smaller appearance - use smaller font
                                        if st.button(f"💬 {chat_name}", key=f"chat_{chat['id']}_select_btn", use_container_width=True):
                                            st.session_state.active_project = project['id']
                                            st.session_state.active_chat = chat['id']
                                            st.session_state.active_page = "Chat"  # Switch to chat page
                                            st.rerun()
                                    
                                    # Skip the document column for chats
                                    with chat_col3:
                                        # Settings/rename button - small gear icon
                                        if st.button("⚙️", key=f"chat_{chat['id']}_settings_btn", help="Rename Chat"):
                                            st.session_state.renaming_chat = chat['id']
                                            st.rerun()
                                            
                                    with chat_col4:
                                        # Chat delete button - small trash icon
                                        if st.button("🗑️", key=f"chat_{chat['id']}_delete_btn", help="Delete Chat"):
                                            st.session_state.deleting_chat = chat['id']
                                            st.rerun()
        
        # Handle project editing
        if 'editing_project' in st.session_state and st.session_state.editing_project:
            project_id = st.session_state.editing_project
            project = project_manager.get_project(project_id)
            
            if project:
                with st.form(key=f"edit_project_{project_id}_form"):
                    st.subheader(f"Edit Project: {project['name']}")
                    new_name = st.text_input("Name:", value=project['name'])
                    custom_prompt = st.text_area("Custom Prompt:", value=project.get('custom_prompt', ''))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Save"):
                            try:
                                project_manager.update_project(
                                    project_id=project_id,
                                    name=new_name,
                                    custom_prompt=custom_prompt
                                )
                                st.session_state.editing_project = None
                                st.success("Project updated!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating project: {str(e)}")
                    
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.editing_project = None
                            st.rerun()
        
        # Handle project deletion confirmation
        if 'deleting_project' in st.session_state and st.session_state.deleting_project:
            project_id = st.session_state.deleting_project
            project = project_manager.get_project(project_id)
            
            if project:
                st.warning(f"Delete project '{project['name']}'? This will delete all chats in this project but preserve all documents.")
                
                col1, col2 = st.columns(2)
                with col1:
                    # Yes, Delete button - using style consistent with "New Project" button
                    if st.button("Yes, Delete", key="confirm_delete_project_btn", use_container_width=True):
                        if project_manager.delete_project(project_id):
                            # Clear active project if it was this one
                            if st.session_state.get('active_project') == project_id:
                                st.session_state.active_project = None
                                st.session_state.active_chat = None
                            
                            st.success(f"Project deleted!")
                        else:
                            st.error("Error deleting project")
                        
                        st.session_state.deleting_project = None
                        st.rerun()
                
                with col2:
                    # Cancel button - using style consistent with form buttons
                    if st.button("Cancel", key="cancel_delete_project_btn", use_container_width=True):
                        st.session_state.deleting_project = None
                        st.rerun()
        
        # Handle chat deletion confirmation
        if 'deleting_chat' in st.session_state and st.session_state.deleting_chat:
            chat_id = st.session_state.deleting_chat
            chat = project_manager.chat_repo.get_chat(chat_id)
            
            if chat:
                st.warning(f"Delete chat '{chat['name']}'? This will delete all messages in this chat.")
                
                col1, col2 = st.columns(2)
                with col1:
                    # Yes, Delete button - using style consistent with project delete button
                    if st.button("Yes, Delete", key="confirm_delete_chat_btn", use_container_width=True):
                        if project_manager.delete_chat(chat_id):
                            # Clear active chat if it was this one
                            if st.session_state.get('active_chat') == chat_id:
                                st.session_state.active_chat = None
                            
                            st.success(f"Chat deleted!")
                        else:
                            st.error("Error deleting chat")
                        
                        st.session_state.deleting_chat = None
                        st.rerun()
                
                with col2:
                    # Cancel button - using style consistent with project cancel button
                    if st.button("Cancel", key="cancel_delete_chat_btn", use_container_width=True):
                        st.session_state.deleting_chat = None
                        st.rerun()
        
        # Handle chat renaming
        if 'renaming_chat' in st.session_state and st.session_state.renaming_chat:
            chat_id = st.session_state.renaming_chat
            chat = project_manager.chat_repo.get_chat(chat_id)
            
            if chat:
                with st.form(key=f"rename_chat_{chat_id}_form"):
                    st.subheader(f"Rename Chat")
                    new_name = st.text_input("Name:", value=chat['name'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Save"):
                            try:
                                project_manager.chat_repo.update_chat(chat_id, new_name)
                                st.session_state.renaming_chat = None
                                st.success("Chat renamed!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error renaming chat: {str(e)}")
                    
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.renaming_chat = None
                            st.rerun()
        
        # Handle adding chat to project
        if 'adding_chat_to_project' in st.session_state and st.session_state.adding_chat_to_project:
            project_id = st.session_state.adding_chat_to_project
            
            with st.form(key=f"add_chat_form_{project_id}"):
                st.subheader("Add New Chat")
                chat_name = st.text_input("Chat Name:")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Create"):
                        if chat_name:
                            try:
                                new_chat = project_manager.create_chat(
                                    project_id=project_id,
                                    name=chat_name
                                )
                                
                                st.session_state.active_chat = new_chat['id']
                                st.session_state.adding_chat_to_project = None
                                st.session_state.active_page = "Chat"  # Switch to chat page
                                st.success(f"Chat '{chat_name}' created!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error creating chat: {str(e)}")
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.adding_chat_to_project = None
                        st.rerun()
                        
        # Show help information if requested
        if st.session_state.get('show_help', False):
            with st.container():
                st.subheader("Help & Information")
                st.markdown("""
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
                
                # Close Help button - using style consistent with other buttons
                if st.button("Close Help", key="close_help_btn", use_container_width=True):
                    st.session_state.show_help = False
                    st.rerun()