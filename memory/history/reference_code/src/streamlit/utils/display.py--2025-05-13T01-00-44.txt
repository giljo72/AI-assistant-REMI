# src/streamlit/utils/display.py
import streamlit as st
from typing import List, Dict, Any
import random
import string
import os
import logging

def handle_delete_click(document_id):
    """Handle the delete button click event"""
    print(f"Delete handler called for document ID: {document_id}")
    st.session_state.confirm_delete_doc_id = document_id
    print(f"Set confirm_delete_doc_id to: {document_id}")

# Set up logger
logger = logging.getLogger(__name__)

# Import formatting utilities
from src.utils.document_formatting import format_timestamp, format_file_size

def format_file_type(content_type: str) -> str:
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

def show_document_list(
    documents: List[Dict[str, Any]],
    include_view_button: bool = False,
    include_project_column: bool = False,
    include_linked_column: bool = False
):
    if not documents:
        st.info("No documents found.")
        return

    # More robust file_manager access
    file_manager = None
    if 'file_manager' in st.session_state:
        file_manager = st.session_state['file_manager']
    
    if file_manager is None:
        st.error("File manager not initialized. Please reload the page.")
        return
    
    # Add debug line here, right after the file_manager check
    st.write(f"Debug - confirm_delete_doc_id: {st.session_state.get('confirm_delete_doc_id')}")

    # Initialize session state for deletion confirmations
    if 'confirm_delete_doc_id' not in st.session_state:
        st.session_state.confirm_delete_doc_id = None
    if 'delete_with_embeddings' not in st.session_state:
        st.session_state.delete_with_embeddings = True

    project_id = st.session_state.get('active_project')
    random_prefix = ''.join(random.choices(string.ascii_lowercase, k=6))

    for i, doc in enumerate(documents):
        with st.container():
            cols = st.columns([3, 1, 1, 2])

            with cols[0]:
                st.write(f"**{doc['filename']}**")
                if doc.get('description'):
                    st.write(f"_{doc['description']}_")

            with cols[1]:
                tag_display = {"P": "Private", "B": "Business", "PB": "Private & Business"}.get(doc['tag'], doc['tag'])
                st.write(f"**Tag:** {tag_display}")
                st.write(f"**Status:** {doc['status']}")
                if include_project_column:
                    proj_names = doc.get('project_names', [])
                    st.write(f"**Project:** {', '.join(proj_names) if proj_names else ''}")
                if include_linked_column:
                    linked = "YES" if doc.get('project_names') else "NO"
                    color = "green" if linked == "YES" else "red"
                    st.markdown(f"**Linked:** <span style='color:{color}'>{linked}</span>", unsafe_allow_html=True)

            with cols[2]:
                st.write(f"**Size:** {format_file_size(doc['file_size'])}")
                st.write(f"**Added:** {format_timestamp(doc['created_at'])}")

            with cols[3]:
                document_id = doc['id']
                file_path = doc.get('file_path')
                key_base = f"{random_prefix}_doc_{i}_{document_id}"

                btn_cols = st.columns([1, 1])

                if file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, "rb") as f:
                            file_data = f.read()
                        with btn_cols[0]:
                            st.download_button(
                                label="🔽",
                                data=file_data,
                                file_name=doc['filename'],
                                mime=doc['content_type'],
                                key=f"{key_base}_download",
                                use_container_width=True
                            )
                    except Exception as e:
                        with btn_cols[0]:
                            st.error(":x:")
                        logger.error(f"Download error: {e}")
                else:
                    with btn_cols[0]:
                        st.error("!")

                with btn_cols[1]:
                    # If currently confirming this document's deletion
                    if st.session_state.confirm_delete_doc_id == document_id:
                        # Show deletion options directly without nested columns
                        st.warning(f"Delete '{doc['filename']}'?")
                        
                        # Option to delete with or without embeddings
                        st.checkbox("Delete file and vector embeddings", 
                                    value=True, 
                                    key=f"delete_embeddings_{document_id}",
                                    on_change=lambda: setattr(st.session_state, 'delete_with_embeddings', 
                                                            st.session_state[f"delete_embeddings_{document_id}"]))
                        
                        # Use buttons side by side without columns
                        delete_btn = st.button("Delete", key=f"confirm_delete_{document_id}", use_container_width=True)
                        cancel_btn = st.button("Cancel", key=f"cancel_delete_{document_id}", use_container_width=True)
                        
                        if delete_btn:
                            try:
                                # Implement deletion with or without embeddings
                                if st.session_state.delete_with_embeddings:
                                    success = file_manager.delete_document(document_id)
                                    message = "Document and embeddings deleted"
                                else:
                                    # Use the new method to keep embeddings
                                    success = file_manager.delete_document_keep_embeddings(document_id)
                                    message = "Document detached but embeddings preserved"
                                    
                                if success:
                                    st.success(message)
                                    st.session_state.confirm_delete_doc_id = None
                                    st.rerun()
                                else:
                                    st.error("Failed to delete document")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                                logger.error(f"Error deleting document {document_id}: {e}", exc_info=True)
                        
                        if cancel_btn:
                            st.session_state.confirm_delete_doc_id = None
                            st.rerun()
                    else:
                        # Simple delete button with callback
                        if st.button("🗑️", key=f"delete_btn_{random_prefix}_{document_id}_{i}", on_click=handle_delete_click, args=(document_id,), use_container_width=True):
                            pass  # The callback will handle the action

            st.markdown("---")

def render_chat_messages(messages, docs_applied=False, prompt_applied=False, retrieved_chunks=None, manual_selection=False):
    if not messages:
        st.info("No messages yet. Start a conversation!")
        return

    for msg in messages:
        role = msg.get('role', '')
        content = msg.get('content', '')

        with st.container():
            if role == 'user':
                st.markdown(f"**You:** {content}")
            elif role == 'assistant':
                st.markdown(f"**AI:** {content}")

                if docs_applied or prompt_applied:
                    cols = st.columns(2)
                    if docs_applied:
                        with cols[0]:
                            st.markdown("<div style='display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(0, 100, 255, 0.2); color: #0064ff;'>🔍 Docs Applied</div>", unsafe_allow_html=True)
                    if prompt_applied:
                        with cols[1]:
                            st.markdown("<div style='display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(255, 195, 0, 0.2); color: #ffc300;'>📝 Custom Prompt</div>", unsafe_allow_html=True)

                if manual_selection:
                    st.markdown("<div style='display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(0, 200, 100, 0.2); color: #00c864;'>🧩 Custom Doc Selection</div>", unsafe_allow_html=True)

                if retrieved_chunks and len(retrieved_chunks) > 0:
                    with st.expander("Document Sources", expanded=False):
                        st.markdown("**Sources used in this response:**")
                        sorted_chunks = sorted(retrieved_chunks, key=lambda x: x.get('similarity', 0), reverse=True)[:3]
                        for i, chunk in enumerate(sorted_chunks):
                            filename = chunk.get('filename', 'Unknown')
                            relevance = chunk.get('similarity', 0) * 100
                            st.markdown(f"**{i+1}. {filename}** (Relevance: {relevance:.1f}%)")
            st.markdown("---")