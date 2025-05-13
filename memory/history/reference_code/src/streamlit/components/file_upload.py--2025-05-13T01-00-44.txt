# src/streamlit/components/file_upload.py
import streamlit as st
import time
from typing import List, Dict, Any, Optional, Tuple

from ...document_processing.file_manager import FileManager

def render_file_upload(file_manager: FileManager):
    """
    Render file upload component with support for multiple files
    and individual metadata for each file
    
    Args:
        file_manager: FileManager instance for handling uploads
    """
    # Initialize session state variables
    if 'upload_submitted' not in st.session_state:
        st.session_state.upload_submitted = False
    if 'file_metadata' not in st.session_state:
        st.session_state.file_metadata = []
    if 'processed_document_ids' not in st.session_state:
        st.session_state.processed_document_ids = []
    if 'upload_success' not in st.session_state:
        st.session_state.upload_success = 0
    if 'upload_failure' not in st.session_state:
        st.session_state.upload_failure = 0
    if 'duplicate_files' not in st.session_state:
        st.session_state.duplicate_files = []
    if 'confirm_duplicates' not in st.session_state:
        st.session_state.confirm_duplicates = False
    
    # Form for file upload
    with st.form("file_upload_form"):
        st.subheader("Upload New Documents")
        
        # Allow multiple file uploads
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["txt", "pdf", "docx", "xlsx", "csv", "rtf", "md", "pptx"],
            accept_multiple_files=True,
            help="Upload one or more documents to add to your AI Assistant"
        )
        
        # Only show the metadata inputs if files are uploaded
        file_metadata = []
        if uploaded_files:
            st.write("### File Metadata")
            st.caption("Please provide metadata for each file")
            
            # Create a container for each file's metadata
            for i, file in enumerate(uploaded_files):
                with st.expander(f"File {i+1}: {file.name}", expanded=True):
                    # Tag selection
                    tag_col, desc_col = st.columns([1, 3])
                    
                    with tag_col:
                        tag = st.selectbox(
                            "Tag",
                            options=["P", "B", "PB"],
                            format_func=lambda x: {
                                "P": "Private",
                                "B": "Business",
                                "PB": "Private & Business"
                            }.get(x, x),
                            help="Categorize your document",
                            key=f"file_upload_tag_{i}"
                        )
                    
                    with desc_col:
                        description = st.text_input(
                            "Description (required)",
                            help="Add a brief description of the document",
                            key=f"file_upload_desc_{i}"
                        )
                    
                    # Store metadata for this file
                    file_metadata.append({
                        "file": file,
                        "tag": tag,
                        "description": description
                    })
        
        # Submit button for the form
        submit_button = st.form_submit_button("Upload Files", use_container_width=True)
        
        # Store form submission status and metadata in session state
        if submit_button and uploaded_files:
            st.session_state.upload_submitted = True
            st.session_state.file_metadata = file_metadata
        else:
            st.session_state.upload_submitted = False
    
    # Process uploads outside the form based on session state
    if st.session_state.upload_submitted and st.session_state.file_metadata:
        # Reset counters and document IDs for this submission
        st.session_state.upload_success = 0
        st.session_state.upload_failure = 0
        st.session_state.processed_document_ids = []
        
        # Validate all descriptions are filled
        missing_descriptions = [
            meta["file"].name for meta in st.session_state.file_metadata 
            if not meta["description"].strip()
        ]
        
        if missing_descriptions:
            st.error(f"Please provide descriptions for all files: {', '.join(missing_descriptions)}")
            st.session_state.upload_submitted = False
        else:
            # Check for duplicate files
            if not st.session_state.confirm_duplicates:  # Only check if not already confirmed
                duplicate_files = []
                for meta in st.session_state.file_metadata:
                    if file_manager.check_if_filename_exists(meta["file"].name):
                        duplicate_files.append(meta["file"].name)
                
                if duplicate_files:
                    st.session_state.duplicate_files = duplicate_files
                    st.warning(f"The following files already exist in the database: {', '.join(duplicate_files)}")
                    st.info("If you proceed, these files will be uploaded with 'Duplicate_DDMMYY' added to their names.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Proceed with Upload", key="file_upload_proceed_btn", use_container_width=True):
                            st.session_state.confirm_duplicates = True
                            st.rerun()  # Rerun to continue the upload
                    
                    with col2:
                        if st.button("Cancel Upload", key="file_upload_cancel_btn", use_container_width=True):
                            st.session_state.upload_submitted = False
                            st.session_state.duplicate_files = []
                            st.rerun()  # Rerun to cancel the upload
                    
                    # Stop processing here until user confirms
                    return
            
            # Process the uploads (only reach here if no duplicates or duplicates confirmed)
            file_count = len(st.session_state.file_metadata)
            
            # Progress bar for uploads
            progress_bar = st.progress(0)
            
            for i, meta in enumerate(st.session_state.file_metadata):
                with st.spinner(f"Uploading {meta['file'].name}..."):
                    # Save uploaded file
                    document = file_manager.save_uploaded_file(
                        file=meta["file"],
                        tag=meta["tag"],
                        description=meta["description"]
                    )
                    
                    # Process the file
                    if document:
                        process_success = file_manager.process_file(document['id'])
                        
                        if process_success:
                            st.session_state.upload_success += 1
                            st.session_state.processed_document_ids.append(document['id'])
                        else:
                            st.session_state.upload_failure += 1
                            st.write(f"❌ Failed to process {meta['file'].name}. Check logs for details.")
                    else:
                        st.session_state.upload_failure += 1
                        st.write(f"❌ Failed to upload {meta['file'].name}. Check logs for details.")
                
                # Update progress bar
                progress_bar.progress((i + 1) / file_count)
            
            # Show results
            if st.session_state.upload_success > 0:
                st.success(f"Successfully uploaded and processed {st.session_state.upload_success} file(s)!")
            
            if st.session_state.upload_failure > 0:
                st.warning(f"Failed to upload or process {st.session_state.upload_failure} file(s). Check logs for details.")
            
            # Reset states
            st.session_state.upload_submitted = False
            st.session_state.confirm_duplicates = False
            st.session_state.duplicate_files = []
    
    # Project attachment section (completely outside the form)
    if (st.session_state.processed_document_ids and 
        'active_project' in st.session_state and 
        st.session_state.active_project):
        
        project_button = st.button(
            "Attach to Current Project", 
            key="file_upload_attach_project_btn", 
            use_container_width=True
        )
        
        if project_button:
            for doc_id in st.session_state.processed_document_ids:
                file_manager.attach_to_project(
                    document_id=doc_id,
                    project_id=st.session_state.active_project
                )
            st.success(f"All documents attached to current project!")
            # Clear the list after attaching
            st.session_state.processed_document_ids = []