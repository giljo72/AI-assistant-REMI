# src/gradio/components/project_sidebar.py
import gradio as gr
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

def create_sidebar():
    """Create the project sidebar component with project management"""
    with gr.Column(scale=1, min_width=350, elem_id="sidebar") as sidebar:
        # Top Header
        with gr.Row(elem_id="projects-header"):
            gr.Markdown(
                """<h3 style='color: #FFC000; margin: 0;'>PROJECTS</h3>""",
                elem_id="projects-title"
            )
            add_project_btn = gr.Button("+", elem_id="add-project-btn")
        
        # Debug area (can be hidden in production)
        debug_text = gr.Textbox(
            label="Debug Output",
            elem_id="debug-output",
            value="",
            visible=True
        )
        
        # Project List using Accordion for collapsible functionality
        with gr.Accordion("Project 1", open=True, elem_id="project-1"):
            # Project Actions
            with gr.Row(elem_id="project-1-actions"):
                add_chat_btn_1 = gr.Button("+", elem_id="add-chat-btn-1", size="sm")
                doc_btn_1 = gr.Button("📄", elem_id="doc-btn-1", size="sm")
                settings_btn_1 = gr.Button("⚙️", elem_id="settings-btn-1", size="sm")
                trash_btn_1 = gr.Button("🗑️", elem_id="trash-btn-1", size="sm")
            
            # Project Chats
            with gr.Column(elem_id="project-1-chats"):
                # Chat 1
                with gr.Row(elem_id="chat-1-1-row"):
                    gr.Markdown("💬 Chat 1 in Project 1")
                    with gr.Column(scale=1, min_width=80):
                        with gr.Row():
                            chat1_settings_btn = gr.Button("⚙️", size="sm")
                            chat1_delete_btn = gr.Button("🗑️", size="sm")
                
                # Chat 2
                with gr.Row(elem_id="chat-1-2-row"):
                    gr.Markdown("💬 Chat 2 in Project 1")
                    with gr.Column(scale=1, min_width=80):
                        with gr.Row():
                            chat2_settings_btn = gr.Button("⚙️", size="sm")
                            chat2_delete_btn = gr.Button("🗑️", size="sm")
                
                # Chat 3
                with gr.Row(elem_id="chat-1-3-row"):
                    gr.Markdown("💬 Chat 3 in Project 1")
                    with gr.Column(scale=1, min_width=80):
                        with gr.Row():
                            chat3_settings_btn = gr.Button("⚙️", size="sm")
                            chat3_delete_btn = gr.Button("🗑️", size="sm")
        
        # Project 2
        with gr.Accordion("Project 2", open=True, elem_id="project-2"):
            # Project Actions
            with gr.Row(elem_id="project-2-actions"):
                add_chat_btn_2 = gr.Button("+", elem_id="add-chat-btn-2", size="sm")
                doc_btn_2 = gr.Button("📄", elem_id="doc-btn-2", size="sm")
                settings_btn_2 = gr.Button("⚙️", elem_id="settings-btn-2", size="sm")
                trash_btn_2 = gr.Button("🗑️", elem_id="trash-btn-2", size="sm")
            
            # Project Chats
            with gr.Column(elem_id="project-2-chats"):
                # Chat 1
                with gr.Row(elem_id="chat-2-1-row"):
                    gr.Markdown("💬 Chat 1 in Project 2")
                    with gr.Column(scale=1, min_width=80):
                        with gr.Row():
                            chat1_settings_btn_2 = gr.Button("⚙️", size="sm")
                            chat1_delete_btn_2 = gr.Button("🗑️", size="sm")
        
        # Search Section
        with gr.Column(elem_id="search-section"):
            gr.Markdown("<h4 style='color: #FFC000; margin-top: 20px;'>Search across all projects</h4>")
            with gr.Column(elem_id="search-options", elem_classes="search-box-dark"):
                global_chats_cb = gr.Checkbox(label="Global Chats")
                global_docs_cb = gr.Checkbox(label="Global Documents")
                all_cb = gr.Checkbox(label="All")
        
        # CSS for styling
        gr.HTML("""
        <style>
        /* Adjust the main layout to give more width to the sidebar */
        .gradio-container .main > div:first-child {
            width: 380px !important;
            min-width: 380px !important;
            max-width: 380px !important;
            flex-grow: 0 !important;
            flex-shrink: 0 !important;
        }
        
        /* Basic styling */
        #sidebar {
            background-color: #080d13;
            padding: 10px;
            height: 100%;
            width: 100% !important;
        }
        
        /* Header styling */
        #projects-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        #add-project-btn {
            background-color: #FFC000;
            color: #080d13;
            font-weight: bold;
            font-size: 18px;
            width: 30px;
            height: 30px;
            min-width: 30px;
            border-radius: 0;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Accordion styling for wider projects */
        #sidebar .accordion {
            border: none !important;
            border-radius: 5px !important;
            background-color: #080d13 !important;
            margin-bottom: 10px !important;
            width: 100% !important;
        }
        
        #sidebar .accordion-header {
            padding: 10px !important;
            background-color: #080d13 !important;
            color: #FFC000 !important;
            font-weight: bold !important;
            border: none !important;
            width: 100% !important;
        }
        
        #sidebar .accordion-content {
            background-color: #1e293b !important;
            border: none !important;
            padding: 0 10px 10px 10px !important;
            width: 100% !important;
        }
        
        /* Project actions */
        #project-1-actions, #project-2-actions {
            margin-bottom: 10px !important;
            display: flex !important;
            justify-content: flex-end !important;
            width: 100% !important;
        }
        
        /* Chat rows */
        #project-1-chats .gr-row, #project-2-chats .gr-row {
            margin: 5px 0 !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
        }
        
        /* Button styling */
        #sidebar button {
            background-color: transparent !important;
            border: none !important;
            color: #FFC000 !important;
            padding: 2px 8px !important;
            min-width: auto !important;
        }
        
        /* Add Chat button styling - larger and bolder */
        #add-chat-btn-1, #add-chat-btn-2 {
            font-weight: bold !important;
            font-size: 19px !important; /* 10% larger */
        }
        
        /* Search section */
        .search-box-dark {
            background-color: #1e293b !important;
            border-radius: 5px !important;
            padding: 10px !important;
            width: 100% !important;
        }
        
        /* Debug output */
        #debug-output {
            background-color: #1e293b !important;
            color: #FFC000 !important;
            font-family: monospace !important;
            margin: 10px 0 !important;
            height: 80px !important;
        }
        
        /* Remove extra box styling */
        #sidebar div {
            border: none !important;
            box-shadow: none !important;
        }
        
        /* Fix width issues in the column */
        #sidebar .gr-block.gr-box, 
        #sidebar .gr-container, 
        #sidebar .gr-form,
        #sidebar .gr-input {
            width: 100% !important;
            max-width: 100% !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
        }
        </style>
        """)
        
        # Button handlers
        
        # Add Project button handler
        def on_add_project_click():
            logger.info("Add Project button clicked")
            return "Add Project button clicked"
        
        # Project 1 handlers
        def on_add_chat_btn_1_click():
            logger.info("Add Chat to Project 1 clicked")
            return "Add Chat to Project 1 clicked"
            
        def on_doc_btn_1_click():
            logger.info("View Documents for Project 1 clicked")
            return "View Documents for Project 1 clicked"
            
        def on_settings_btn_1_click():
            logger.info("Settings for Project 1 clicked")
            return "Settings for Project 1 clicked"
            
        def on_trash_btn_1_click():
            logger.info("Delete Project 1 clicked")
            return "Delete Project 1 clicked"
        
        # Chat handlers for Project 1
        def on_chat1_settings_btn_click():
            logger.info("Settings for Chat 1 in Project 1 clicked")
            return "Settings for Chat 1 in Project 1 clicked"
            
        def on_chat1_delete_btn_click():
            logger.info("Delete Chat 1 in Project 1 clicked")
            return "Delete Chat 1 in Project 1 clicked"
            
        def on_chat2_settings_btn_click():
            logger.info("Settings for Chat 2 in Project 1 clicked")
            return "Settings for Chat 2 in Project 1 clicked"
            
        def on_chat2_delete_btn_click():
            logger.info("Delete Chat 2 in Project 1 clicked")
            return "Delete Chat 2 in Project 1 clicked"
            
        def on_chat3_settings_btn_click():
            logger.info("Settings for Chat 3 in Project 1 clicked")
            return "Settings for Chat 3 in Project 1 clicked"
            
        def on_chat3_delete_btn_click():
            logger.info("Delete Chat 3 in Project 1 clicked")
            return "Delete Chat 3 in Project 1 clicked"
        
        # Project 2 handlers
        def on_add_chat_btn_2_click():
            logger.info("Add Chat to Project 2 clicked")
            return "Add Chat to Project 2 clicked"
            
        def on_doc_btn_2_click():
            logger.info("View Documents for Project 2 clicked")
            return "View Documents for Project 2 clicked"
            
        def on_settings_btn_2_click():
            logger.info("Settings for Project 2 clicked")
            return "Settings for Project 2 clicked"
            
        def on_trash_btn_2_click():
            logger.info("Delete Project 2 clicked")
            return "Delete Project 2 clicked"
        
        # Chat handlers for Project 2
        def on_chat1_settings_btn_2_click():
            logger.info("Settings for Chat 1 in Project 2 clicked")
            return "Settings for Chat 1 in Project 2 clicked"
            
        def on_chat1_delete_btn_2_click():
            logger.info("Delete Chat 1 in Project 2 clicked")
            return "Delete Chat 1 in Project 2 clicked"
        
        # Connect button handlers
        add_project_btn.click(on_add_project_click, [], [debug_text])
        
        # Project 1 buttons
        add_chat_btn_1.click(on_add_chat_btn_1_click, [], [debug_text])
        doc_btn_1.click(on_doc_btn_1_click, [], [debug_text])
        settings_btn_1.click(on_settings_btn_1_click, [], [debug_text])
        trash_btn_1.click(on_trash_btn_1_click, [], [debug_text])
        
        # Chat buttons for Project 1
        chat1_settings_btn.click(on_chat1_settings_btn_click, [], [debug_text])
        chat1_delete_btn.click(on_chat1_delete_btn_click, [], [debug_text])
        chat2_settings_btn.click(on_chat2_settings_btn_click, [], [debug_text])
        chat2_delete_btn.click(on_chat2_delete_btn_click, [], [debug_text])
        chat3_settings_btn.click(on_chat3_settings_btn_click, [], [debug_text])
        chat3_delete_btn.click(on_chat3_delete_btn_click, [], [debug_text])
        
        # Project 2 buttons
        add_chat_btn_2.click(on_add_chat_btn_2_click, [], [debug_text])
        doc_btn_2.click(on_doc_btn_2_click, [], [debug_text])
        settings_btn_2.click(on_settings_btn_2_click, [], [debug_text])
        trash_btn_2.click(on_trash_btn_2_click, [], [debug_text])
        
        # Chat buttons for Project 2
        chat1_settings_btn_2.click(on_chat1_settings_btn_2_click, [], [debug_text])
        chat1_delete_btn_2.click(on_chat1_delete_btn_2_click, [], [debug_text])
    
    # Return sidebar and empty nav buttons for compatibility
    nav_buttons = (None, None, None, None)
    return sidebar, nav_buttons