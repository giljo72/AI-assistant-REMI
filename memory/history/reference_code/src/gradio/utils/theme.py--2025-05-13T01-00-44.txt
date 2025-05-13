# src/gradio/utils/theme.py
import gradio as gr

def create_theme():
    """Create the application theme with proper colors"""
    return gr.themes.Default(
        primary_hue="orange",
        secondary_hue="indigo",
        neutral_hue="slate",
    ).set(
        # Background colors
        background_fill_primary="#080d13",
        background_fill_secondary="#121922",
        
        # Button colors
        button_primary_background_fill="#FFC000",
        button_primary_text_color="#080d13",
        button_secondary_background_fill="#1e293b",
        
        # Input elements
        input_background_fill="#1e293b",
        input_border_color="#2d3748",
        
        # Block elements
        block_background_fill="#121922",
        block_title_text_color="#FFC000",
        
        # Border
        border_color_primary="#2d3748"
    )