# src/streamlit/pages/__init__.py
"""
Page-level components for Streamlit interface.
"""
from .settings import render_settings_page
from .view_document import render_view_document_page

__all__ = [
    'render_settings_page',
    'render_view_document_page'
]