import gradio as gr
import logging

logger = logging.getLogger(__name__)

class SettingsPage:
    """Settings page component"""
    
    def __init__(self):
        """Initialize the settings page"""
        pass
    
    def render(self):
        """Render the settings page"""
        gr.Markdown("## Settings")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### System")
                db_status = gr.Textbox(label="Database Status", value="Connected", interactive=False)
                llm_status = gr.Textbox(label="LLM Status", value="Ollama: Ready", interactive=False)
            
            with gr.Column():
                gr.Markdown("### Model Settings")
                temperature = gr.Slider(minimum=0.1, maximum=1.0, value=0.7, label="Temperature")
                context_window = gr.Slider(minimum=1024, maximum=8192, value=4096, step=1024, label="Context Window")