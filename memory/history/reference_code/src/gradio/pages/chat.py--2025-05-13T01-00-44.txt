# src/gradio/pages/chat.py
import gradio as gr
import logging
from typing import List, Dict, Any, Optional

from src.services.chat_service import ChatService
from src.services.service_factory import service_factory

logger = logging.getLogger(__name__)

class ChatPage:
    """Enhanced chat page component"""
    
    def __init__(self):
        """Initialize the chat page"""
        self.chat_history = None
        self.chat_input = None
        self.send_btn = None
        self.mic_btn = None
        self.attachment_btn = None
        self.document_context_btn = None
        self.prompt_btn = None
        self.project_title = None
        
    def render(self):
        """Render the chat page"""
        # Project/Chat title bar
        with gr.Row():
            self.project_title = gr.Markdown("""
        <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;'>
            <span style='color: #FFC000; font-weight: bold; font-size: 24px;'>
                "Project_Name (if it Exists) \\ Chat_Name",
                elem_id="chat_title"</span>
            """)
        
        # Chat area
        with gr.Column():
            # Using modern message format with type="messages"
            self.chat_history = gr.Chatbot(
                value=[
                    {"role": "assistant", "content": "This text is where the LLM types back to my questions. Next is just junk text to fill the space as:ldkjf;alksdfjf;lj Alska;lsdkjlt;asjkfd / alskdjflaksjdf.. Alsdkjflaskdjflklasdlfkjasldf / asldfkjlaksdfjasdfj"},
                    {"role": "user", "content": "my text should be white and, on the right"}
                ],
                height="72vh",
                label="Conversation",
                type="messages",
                elem_id="conversation-box"
            )
            
            # Bottom section - Full width chat input
            with gr.Row(elem_id="chat-controls-row"):
                # Chat input column - taking full width
                with gr.Column(scale=1):
                    # User Chat label
                    gr.Markdown("<div style='color: #FFC000; font-weight: bold; font-size: 16px; margin-bottom: 5px;'>User Chat</div>")
                    
                    # Chat input controls with row for alignment
                    with gr.Row():
                        # Text input - using most of width
                        with gr.Column(scale=20):
                            self.chat_input = gr.Textbox(
                                placeholder="Type your message here...",
                                lines=3,
                                max_lines=10,
                                elem_id="chat-input-box"
                            )
                        
                        # Control buttons aligned to the right of input
                        with gr.Column(scale=1, min_width=50, elem_classes="action-buttons-column"):
                            gr.HTML("""
                            <div class="action-buttons-container">
                                <div class="action-button">📎</div>
                                <div class="action-button">✏️</div>
                                <div class="action-button send-button">▶️</div>
                            </div>
                            """)
                    
                    # Context buttons at the bottom with custom styling
                    with gr.Row():
                        self.document_context_btn = gr.Button(
                            "Document Context: Enabled", 
                            variant="primary",
                            elem_classes="toggle-button active",
                            elem_id="doc-context-toggle"
                        )
                        self.prompt_btn = gr.Button(
                            "Project prompt: Enabled", 
                            variant="primary",
                            elem_classes="toggle-button active",
                            elem_id="prompt-toggle"
                        )
            
            # Add JavaScript to handle toggle behavior
            gr.HTML("""
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                // For Document Context toggle
                const docContextBtn = document.getElementById('doc-context-toggle');
                if (docContextBtn) {
                    docContextBtn.addEventListener('click', function() {
                        const isActive = this.classList.contains('active');
                        if (isActive) {
                            this.classList.remove('active');
                            this.textContent = 'Document Context: Disabled';
                        } else {
                            this.classList.add('active');
                            this.textContent = 'Document Context: Enabled';
                        }
                    });
                }
                
                // For Project Prompt toggle
                const promptToggleBtn = document.getElementById('prompt-toggle');
                if (promptToggleBtn) {
                    promptToggleBtn.addEventListener('click', function() {
                        const isActive = this.classList.contains('active');
                        if (isActive) {
                            this.classList.remove('active');
                            this.textContent = 'Project prompt: Disabled';
                        } else {
                            this.classList.add('active');
                            this.textContent = 'Project prompt: Enabled';
                        }
                    });
                }
            });
            </script>
            """)
        
        # Connect event handlers for chat
        self.send_btn = gr.Button("", visible=False)  # Hidden button for event handling
        self.send_btn.click(
            fn=self.send_message,
            inputs=[self.chat_input],
            outputs=[self.chat_input, self.chat_history]
        )
        
        return self
    
    def send_message(self, message):
        """Send a message (placeholder implementation)"""
        if not message.strip():
            return "", self.chat_history

        # Update to use the proper message format with role and content
        self.chat_history.append({"role": "user", "content": message})
        
        # Placeholder for actual message processing
        assistant_response = "This is a placeholder response."
        self.chat_history.append({"role": "assistant", "content": assistant_response})
        
        return "", self.chat_history