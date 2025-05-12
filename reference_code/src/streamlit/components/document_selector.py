# src/streamlit/components/document_selector.py

import streamlit as st
import random
import string
from typing import List, Dict, Any, Callable

def format_file_type(content_type: str) -> str:
    """Convert MIME type to user-friendly format."""
    type_mapping = {
        "application/pdf": "PDF",
        "text/plain": "TXT",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "XLSX",
        "text/csv": "CSV",
        "application/msword": "DOC",
        "image/jpeg": "JPEG",
        "image/png": "PNG",
        "image/gif": "GIF",
        "text/markdown": "MD",
        "application/vnd.ms-powerpoint": "PPT",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PPTX",
    }
    return type_mapping.get(content_type, content_type.split('/')[-1].upper())

def render_document_selector(
    documents: List[Dict[Any, Any]],
    on_selection_change: Callable[[List[int]], None],
    current_project_id: int = None,
    current_selections: List[int] = None,
) -> None:
    """
    Render a document selector interface for RAG context.
    
    Args:
        documents: List of document dictionaries
        on_selection_change: Callback function when selection changes
        current_project_id: ID of the current project (to highlight project documents)
        current_selections: List of document IDs currently selected
    """
    if current_selections is None:
        current_selections = []
    
    if not documents:
        st.info("No documents available. Upload documents in the Files section to include them in AI responses.")
        return
    
    # Initialize session state for selected documents if not exists
    if "selected_docs_for_rag" not in st.session_state:
        st.session_state.selected_docs_for_rag = current_selections.copy()
    
    # Initialize tab state if not exists
    if "doc_selector_active_tab" not in st.session_state:
        st.session_state.doc_selector_active_tab = 0
    
    # Create tabs for different document views
    tabs = st.tabs(["All Documents", "Project Documents", "Selected Documents"])
    
    # All Documents tab
    with tabs[0]:
        st.subheader("All Documents")
        _render_document_list(
            documents, 
            on_selection_change,
            filter_func=lambda doc: True,  # No filter for all documents
            current_project_id=current_project_id,
            current_selections=st.session_state.selected_docs_for_rag,
            tab_prefix="all"  # Add tab prefix to ensure unique keys
        )
    
    # Project Documents tab
    with tabs[1]:
        st.subheader("Project Documents")
        if current_project_id:
            _render_document_list(
                documents,
                on_selection_change,
                filter_func=lambda doc: any(assoc.get('project_id') == current_project_id 
                                         for assoc in doc.get('associations', [])),
                current_project_id=current_project_id,
                current_selections=st.session_state.selected_docs_for_rag,
                tab_prefix="project"  # Add tab prefix to ensure unique keys
            )
        else:
            st.info("No project selected. Create or select a project to see project-specific documents.")
    
    # Selected Documents tab
    with tabs[2]:
        st.subheader("Selected Documents")
        _render_document_list(
            documents,
            on_selection_change,
            filter_func=lambda doc: doc.get('id') in st.session_state.selected_docs_for_rag,
            current_project_id=current_project_id,
            current_selections=st.session_state.selected_docs_for_rag,
            tab_prefix="selected"  # Add tab prefix to ensure unique keys
        )
    
    # Add a button to clear all selections
    if st.button(
        "Clear All Selections", 
        key="doc_selector_clear_all_btn", 
        use_container_width=True
    ):
        st.session_state.selected_docs_for_rag = []
        on_selection_change([])
        st.success("Cleared all document selections")
        st.rerun()

def _render_document_list(
    documents: List[Dict[Any, Any]],
    on_selection_change: Callable[[List[int]], None],
    filter_func: Callable[[Dict[Any, Any]], bool],
    current_project_id: int = None,
    current_selections: List[int] = None,
    tab_prefix: str = ""  # Add tab prefix parameter for unique keys
) -> None:
    """
    Helper function to render a filtered list of documents with selection checkboxes.
    
    Args:
        documents: List of document dictionaries
        on_selection_change: Callback function when selection changes
        filter_func: Function to filter documents
        current_project_id: ID of the current project
        current_selections: List of document IDs currently selected
        tab_prefix: Prefix to add to keys to ensure uniqueness across tabs
    """
    if current_selections is None:
        current_selections = []
    
    # Filter documents
    filtered_docs = [doc for doc in documents if filter_func(doc)]
    
    if not filtered_docs:
        st.info("No documents match the current filter.")
        return
    
    # Create a search box with tab-specific key
    search_key = f"doc_selector_{tab_prefix}_search"
    search_term = st.text_input(
        "Search documents by filename or description", 
        key=search_key
    )
    
    # Apply search filter if search term is provided
    if search_term:
        search_term = search_term.lower()
        filtered_docs = [
            doc for doc in filtered_docs 
            if search_term in doc.get('filename', '').lower() 
            or search_term in doc.get('description', '').lower()
        ]
    
    # Show document count
    st.write(f"Showing {len(filtered_docs)} document(s)")
    
    # Create columns for layout
    for i, doc in enumerate(filtered_docs):
        col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
        
        doc_id = doc.get('id')
        filename = doc.get('filename', 'Unnamed Document')
        file_type = format_file_type(doc.get('content_type', 'Unknown'))
        description = doc.get('description', '')
        
        # Truncate description if too long
        if len(description) > 50:
            description = description[:47] + "..."
        
        # Create a unique key for the checkbox using tab prefix, position, and document ID
        checkbox_key = f"doc_selector_{tab_prefix}_checkbox_{doc_id}_{i}"
        
        # Check if this document is in the current project
        is_in_project = current_project_id and any(
            assoc.get('project_id') == current_project_id 
            for assoc in doc.get('associations', [])
        )
        
        # Define update function for this specific checkbox
        def update_selection(checkbox_key=checkbox_key, doc_id=doc_id):
            # Get the current state of the checkbox
            if st.session_state[checkbox_key]:
                # Checkbox is checked, add document to selection if not already there
                if doc_id not in st.session_state.selected_docs_for_rag:
                    st.session_state.selected_docs_for_rag.append(doc_id)
                    on_selection_change(st.session_state.selected_docs_for_rag)
            else:
                # Checkbox is unchecked, remove document from selection if it's there
                if doc_id in st.session_state.selected_docs_for_rag:
                    st.session_state.selected_docs_for_rag.remove(doc_id)
                    on_selection_change(st.session_state.selected_docs_for_rag)
        
        # Selection checkbox
        with col1:
            is_selected = doc_id in current_selections
            st.checkbox(
                "Select document",  
                value=is_selected, 
                key=checkbox_key,
                label_visibility="collapsed",
                on_change=update_selection
            )
        
        # Document info
        with col2:
            doc_info = f"**{filename}** ({file_type})"
            if is_in_project:
                doc_info += " 📎"  # Paper clip emoji to indicate attachment to current project
            
            st.markdown(doc_info)
            if description:
                st.caption(description)
        
        # Download button
        with col3:
            download_key = f"doc_selector_{tab_prefix}_download_btn_{doc_id}_{i}"
            if st.button("Download", key=download_key, use_container_width=True):
                # Set query parameters to download this document
                st.query_params.update({"document_id": doc_id})
                st.rerun()
        
        # Add a separator line
        st.markdown("---")