# src/streamlit/components/doc_preview.py
import streamlit as st
from typing import Dict, Any, Optional
import os

def render_document_preview(document: Dict[str, Any], chunk_text: Optional[str] = None):
    """
    Render a preview of a document with optional highlighted chunk
    
    Args:
        document: Document data dictionary
        chunk_text: Optional text chunk to highlight
    """
    if not document:
        st.error("Document not found")
        return
    
    # Document header
    st.subheader(f"Document: {document['filename']}")
    
    # Document metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Type:** {document['content_type']}")
    with col2:
        tag_label = {
            "P": "Private",
            "B": "Business",
            "PB": "Private & Business"
        }.get(document['tag'], document['tag'])
        st.markdown(f"**Tag:** {tag_label}")
    with col3:
        st.markdown(f"**Status:** {document['status']}")
    
    # Description if available
    if document.get('description'):
        st.markdown(f"**Description:** {document['description']}")
    
    # If we have a specific chunk to highlight
    if chunk_text:
        st.markdown("---")
        st.markdown("### Relevant Section")
        with st.container(border=True):
            st.markdown(chunk_text)
        st.markdown("---")
    
    # Get file path
    file_path = document.get('file_path')
    if not file_path or not os.path.exists(file_path):
        st.warning("Original file not found")
        return
    
    # Determine file type and render appropriate preview
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Text files
    if file_ext in ['.txt', '.md', '.py', '.json', '.csv', '.log', '.yaml', '.yml']:
        try:
            with open(file_path, 'r', errors='replace') as f:
                content = f.read()
            
            st.markdown("### Document Content")
            st.text_area("", content, height=400)
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    
    # PDF files
    elif file_ext == '.pdf':
        st.markdown("### Document Preview")
        # Display PDF in iframe
        try:
            with open(file_path, "rb") as f:
                base64_pdf = f.read().hex()
            
            # Display PDF
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying PDF: {str(e)}")
    
    # Images
    elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
        try:
            st.markdown("### Document Preview")
            st.image(file_path, caption=document['filename'])
        except Exception as e:
            st.error(f"Error displaying image: {str(e)}")
    
    # Other file types
    else:
        st.warning(f"Preview not available for {file_ext} files")
        st.markdown(f"File can be found at: {file_path}")

def render_document_chunk_explorer(retrieved_chunks: list, doc_repo):
    """
    Render an explorer for document chunks used in RAG
    
    Args:
        retrieved_chunks: List of retrieved chunks from RAG
        doc_repo: Document repository to fetch document data
    """
    if not retrieved_chunks:
        st.info("No document chunks were used in this response")
        return
    
    st.markdown("### Document Sources")
    
    for i, chunk in enumerate(retrieved_chunks):
        relevance = chunk.get('similarity', 0) * 100
        doc_id = chunk.get('document_id')
        
        with st.expander(f"{chunk['filename']} (Relevance: {relevance:.1f}%)"):
            # Get full document data
            document = doc_repo.get_document(doc_id) if doc_id else None
            
            if document:
                # Display document metadata
                st.markdown(f"**Document:** {document['filename']}")
                st.markdown(f"**Type:** {document['content_type']} | **Size:** {document['file_size']} bytes")
                
                # Show chunk text
                st.markdown("**Relevant section:**")
                st.markdown(chunk['chunk_text'])
                
                # Option to view full document
                if st.button("View Full Document", key=f"view_doc_{doc_id}_{i}"):
                    # Set session state to view this document
                    st.session_state.viewing_document = document
                    st.session_state.viewing_chunk = chunk['chunk_text']
                    st.rerun()
    
    # Render full document preview if selected
    if 'viewing_document' in st.session_state and st.session_state.viewing_document:
        with st.container():
            st.markdown("---")
            render_document_preview(
                st.session_state.viewing_document,
                st.session_state.viewing_chunk
            )
            
            if st.button("Close Preview", key="close_preview"):
                del st.session_state.viewing_document
                del st.session_state.viewing_chunk
                st.rerun()