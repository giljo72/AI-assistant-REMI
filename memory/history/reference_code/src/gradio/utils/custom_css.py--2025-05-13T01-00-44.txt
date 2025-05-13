# src/gradio/utils/custom_css.py

def get_custom_css():
    """Get custom CSS for the application"""
    return """
    /* Main background colors */
    body, .gradio-container {
        background-color: #080d13 !important;
    }
    
    /* Sidebar styling */
    .gradio-container .main > div:first-child > div:first-child {
        background-color: #080d13 !important;
        border-right: 1px solid #2d3748 !important;
    }
    
    /* Clickable icons */
    .clickable-icon p {
        color: #FFC000 !important;
        cursor: pointer !important;
        margin: 0 5px !important;
        display: inline-block !important;
        padding: 5px !important;
    }
    
    .clickable-icon p:hover {
        color: #ffffff !important;
    }
    
    /* Header text */
    .header-text p {
        color: #FFC000 !important;
        font-size: 16px !important;
        font-weight: bold !important;
        margin-bottom: 5px !important;
    }
    
    /* Project titles */
    .project-title p {
        color: #FFC000 !important;
        font-size: 14px !important;
        font-weight: bold !important;
        margin: 5px 0 !important;
    }
    
    /* Chat items */
    .chat-item p {
        color: #ffffff !important;
        margin-left: 15px !important;
        cursor: pointer !important;
        font-size: 14px !important;
        margin-top: 5px !important;
        margin-bottom: 0 !important;
    }
    
    .chat-item p:hover {
        color: #FFC000 !important;
    }
    
    /* Add button */
    .gradio-container .main > div:first-child button:has(span:contains("+")) {
        background: #FFC000 !important;
        color: #080d13 !important;
        border-radius: 4px !important;
        width: 100% !important;
        margin-bottom: 10px !important;
    }
    
    /* Separators */
    .gradio-container .main > div:first-child hr {
        border-color: rgba(255, 255, 255, 0.2) !important;
        margin: 10px 0 !important;
    }
    
    /* Row alignment for chat controls */
    .gradio-container .main > div:first-child .chat-item + div {
        display: flex !important;
        justify-content: flex-end !important;
        margin-right: 20px !important;
    }
    
    /* Chat area title */
    .gradio-container .main > div:nth-child(2) p:first-of-type {
        color: #FFC000 !important;
        font-size: 18px !important;
        font-weight: bold !important;
        margin: 10px 0 !important;
    }
    
    /* Chatbot message styling */
    .message.user {
        background-color: #1e293b !important;
        border-radius: 8px !important;
        padding: 10px !important;
        margin-left: 30% !important;
        color: #ffffff !important;
    }
    
    .message:not(.user) {
        background-color: #121922 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        color: #FFC000 !important;
    }
    
    /* Context buttons */
    button.primary {
        background-color: #FFC000 !important;
        color: #080d13 !important;
    }
    
    /* Input area */
    textarea, input[type="text"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #2d3748 !important;
    }
    
    /* Search box styling in sidebar */
    .search-box-dark {
        background-color: #1e293b !important;
        border-radius: 8px !important;
        padding: 10px !important;
        margin-top: 5px !important;
        margin-bottom: 15px !important;
        border: 1px solid #2d3748 !important;
    }
    
    /* Checkbox styling */
    .search-box-dark label {
        color: #ffffff !important;
        font-size: 14px !important;
        margin-bottom: 5px !important;
    }
    
    .search-box-dark input[type="checkbox"] {
        margin-right: 8px !important;
    }
    
    /* Full-width chat input */
    #chat-input-box {
        width: 100% !important;
    }
    
    /* Action buttons */
    .action-buttons-container {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
    }
    
    .action-button {
        cursor: pointer !important;
        margin: 5px 0 !important;
        font-size: 18px !important;
    }
    
    .send-button {
        color: #FFC000 !important;
        font-size: 22px !important;
    }
    """