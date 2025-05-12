# src/streamlit/pages/view_document.py
import streamlit as st
from typing import Optional
import os
import logging

# Change relative imports to absolute imports
from src.db.repositories.document_repo import DocumentRepository

logger = logging.getLogger(__name__)

def navigate_to_files():
    """Handle navigation back to Files page"""
    # Clear all query parameters
    for param in list(st.query_params.keys()):
        del st.query_params[param]
    
    # Set just the navigation parameter
    st.query_params["nav"] = "Files"
    
    # Clear any document-related session state
    for key in list(st.session_state.keys()):
        if "document" in key or "doc" in key:
            del st.session_state[key]
    
    # Set the active page explicitly
    st.session_state.active_page = "Files"

def render_view_document_page(document_id: Optional[int] = None):
    """
    Render the document download page
    
    Args:
        document_id: ID of document to download and view
    """
    # Emergency escape link
    st.markdown('<a href="/" target="_self">Emergency Return to Home</a>', unsafe_allow_html=True)

    st.title("Document Download")    
    # Add breadcrumb navigation
    if st.button("← Back to Files", 
           key="view_doc_back_btn", 
           help="Return to documents list",
           on_click=navigate_to_files):
        pass  # The callback will handle the action
    
    # Get document ID from query params if not provided
    if not document_id:
        query_params = st.query_params
        
        # Check for document_id parameter (older style)
        doc_id_param = query_params.get("document_id")
        if doc_id_param and doc_id_param[0].isdigit():
            document_id = int(doc_id_param[0])
        
        # Also check for view_document parameter (newer style)
        view_doc_param = query_params.get("view_document")
        if not document_id and view_doc_param and view_doc_param[0].isdigit():
            document_id = int(view_doc_param[0])
    
    # Render the document download interface
    if document_id:
        render_document_download(document_id)
    else:
        st.info("No document selected. Please select a document to download.")
        
        # Link back to files page
        if st.button("Go to Files Page", key="view_doc_goto_files_btn", use_container_width=True):
            st.query_params.update({"nav": "Files"})
            st.rerun()

def render_document_download(document_id):
    """
    Render a document download interface for the given document ID
    
    Args:
        document_id: ID of the document to download
    """
    # Get document details
    document_repo = DocumentRepository()
    
    try:
        document = document_repo.get_document(document_id)
        
        if not document:
            st.error(f"Document with ID {document_id} not found in the database.")
            return
        
        # Display document metadata
        st.subheader(f"Document: {document['filename']}")
        
        # Show file metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            content_type = document['content_type'].split('/')[-1].upper() if '/' in document['content_type'] else document['content_type']
            st.write(f"**Type:** {content_type}")
        with col2:
            tag_labels = {
                "P": "Private",
                "B": "Business",
                "PB": "Private & Business"
            }
            tag = tag_labels.get(document['tag'], document['tag'])
            st.write(f"**Tag:** {tag}")
        with col3:
            status_colors = {
                "Active": "green",
                "Uploaded": "blue",
                "Failed": "red",
                "Detached": "orange"
            }
            color = status_colors.get(document['status'], "gray")
            st.markdown(f"**Status:** <span style='color: {color};'>{document['status']}</span>", unsafe_allow_html=True)
        
        if document.get('description'):
            st.markdown(f"**Description:** {document['description']}")
        
        # Add instructions for the user
        st.markdown("""
        ### Download Instructions
        
        To view this document:
        1. Download it using the button below
        2. Open it with your preferred application
        """)
        
        # File path
        file_path = document['file_path']
        
        # Check if file exists
        if not os.path.exists(file_path):
            st.error(f"File not found at: {file_path}")
            st.write("This could be due to:")
            st.write("1. The file was moved or deleted from the storage location")
            st.write("2. The path in the database doesn't match the actual file location")
            return
        
        # Read file data
        try:
            with open(file_path, "rb") as file:
                file_data = file.read()
                
                # Create download button
                st.download_button(
                    label="Download Document",
                    data=file_data,
                    file_name=document['filename'],
                    mime=document['content_type'],
                    key="download_document_btn",
                    use_container_width=True
                )
                
                st.success(f"Document '{document['filename']}' is ready for download. Click the button above to download.")
                
                # File information
                st.write("**File Information:**")
                file_size = document.get('file_size', 0)
                if file_size:
                    st.write(f"- Size: {format_file_size(file_size)}")
                st.write(f"- Type: {document['content_type']}")
                if document.get('created_at'):
                    st.write(f"- Created: {document['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                
        except PermissionError:
            st.error(f"Permission denied when trying to read the file. Check file permissions.")
        except Exception as e:
            st.error(f"Error accessing file: {str(e)}")
    except Exception as e:
        st.error(f"Error retrieving document: {str(e)}")

def format_file_size(size_bytes):
    """Format file size for display"""
    if not size_bytes:
        return "0 B"
    
    # Simple formatter without external dependencies
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"