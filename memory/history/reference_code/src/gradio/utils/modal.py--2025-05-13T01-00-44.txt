# src/gradio/utils/modal.py
import gradio as gr
import logging

logger = logging.getLogger(__name__)

def create_modal(title, content_fn, footer_fn=None, visible=False, size="md"):
    """
    Create a modal-like component using gr.Group with visibility toggling
    
    Args:
        title: Modal title text
        content_fn: Function that renders the modal content (takes the modal group as argument)
        footer_fn: Optional function that renders the modal footer (takes the modal group as argument)
        visible: Whether the modal is initially visible
        size: Size of the modal ("sm", "md", "lg", "xl")
        
    Returns:
        Tuple of (modal_group, close_btn)
    """
    # Calculate width based on size
    if size == "sm":
        width = 400
    elif size == "md":
        width = 600
    elif size == "lg":
        width = 800
    elif size == "xl":
        width = 1000
    else:
        width = 600  # Default to medium
    
    # Create a wrapper with custom styling
    wrapper_style = f"""
    <style>
    .modal-wrapper {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }}
    
    .modal-content {{
        background-color: #121922;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        width: {width}px;
        max-width: 90%;
        max-height: 90vh;
        overflow: auto;
    }}
    
    .modal-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .modal-title {{
        color: #FFC000;
        font-weight: bold;
        font-size: 18px;
        margin: 0;
    }}
    
    .modal-close {{
        color: rgba(255, 255, 255, 0.6);
        cursor: pointer;
        font-size: 20px;
        line-height: 20px;
    }}
    
    .modal-body {{
        padding: 16px;
    }}
    
    .modal-footer {{
        padding: 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: flex-end;
        gap: 8px;
    }}
    </style>
    """
    
    # Create the modal group with visibility control
    with gr.Group(visible=visible) as modal_group:
        # Create the HTML content with proper f-string formatting
        modal_html = f"""
        <div class="modal-wrapper">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">{title}</h3>
                    <span class="modal-close" id="modal-close-btn">&times;</span>
                </div>
                <div class="modal-body" id="modal-body">
                    <!-- Content will be rendered here -->
                </div>
                <div class="modal-footer" id="modal-footer">
                    <!-- Footer will be rendered here -->
                </div>
            </div>
        </div>

        <script>
        function setupModalHandlers() {{
            var closeBtn = document.getElementById('modal-close-btn');
            if (closeBtn) {{
                closeBtn.addEventListener('click', function() {{
                    var hiddenCloseBtn = document.getElementById('modal-hidden-close-btn');
                    if (hiddenCloseBtn) hiddenCloseBtn.click();
                }});
            }}
            
            document.addEventListener('keydown', function(event) {{
                if (event.key === 'Escape') {{
                    var hiddenCloseBtn = document.getElementById('modal-hidden-close-btn');
                    if (hiddenCloseBtn) hiddenCloseBtn.click();
                }}
            }});
        }}

        setupModalHandlers();
        setTimeout(setupModalHandlers, 300);
        </script>
"""
        
        # Apply the styles and HTML content
        gr.HTML(wrapper_style + modal_html)
        
        # Hidden close button
        close_btn = gr.Button("Close", elem_id="modal-hidden-close-btn", visible=False)
        
        # Render content
        if content_fn:
            with gr.Group(elem_id="modal-content-container"):
                content_fn(modal_group)
        
        # Render footer
        if footer_fn:
            with gr.Group(elem_id="modal-footer-container"):
                footer_fn(modal_group)
        
        # Connect close button to hide modal
        close_btn.click(
            fn=lambda: gr.update(visible=False),
            outputs=[modal_group]
        )
    
    return modal_group, close_btn

def show_modal(modal_group):
    """
    Show a modal
    
    Args:
        modal_group: Modal group component to show
        
    Returns:
        Updated visibility for the modal
    """
    return gr.update(visible=True)

def hide_modal(modal_group):
    """
    Hide a modal
    
    Args:
        modal_group: Modal group component to hide
        
    Returns:
        Updated visibility for the modal
    """
    return gr.update(visible=False)

def create_confirm_modal(title, message, confirm_text="Yes", cancel_text="No", on_confirm=None, on_cancel=None, visible=False):
    """
    Create a confirmation modal with Yes/No buttons
    
    Args:
        title: Modal title
        message: Confirmation message
        confirm_text: Text for confirm button
        cancel_text: Text for cancel button
        on_confirm: Function to call when confirmed
        on_cancel: Function to call when canceled
        visible: Whether the modal is initially visible
        
    Returns:
        Tuple of (modal_group, show_fn, hide_fn)
    """
    def content_fn(modal):
        gr.Markdown(message)
    
    def footer_fn(modal):
        with gr.Row():
            cancel_btn = gr.Button(cancel_text, variant="secondary")
            confirm_btn = gr.Button(confirm_text, variant="primary")
            
            if on_confirm:
                confirm_btn.click(
                    fn=on_confirm,
                    outputs=[modal]
                )
            else:
                confirm_btn.click(
                    fn=lambda: gr.update(visible=False),
                    outputs=[modal]
                )
                
            if on_cancel:
                cancel_btn.click(
                    fn=on_cancel,
                    outputs=[modal]
                )
            else:
                cancel_btn.click(
                    fn=lambda: gr.update(visible=False),
                    outputs=[modal]
                )
    
    modal_group, close_btn = create_modal(title, content_fn, footer_fn, visible, "sm")
    
    return modal_group