# src/streamlit/pages/files.py
import streamlit as st
import time
from typing import Dict, Any, Optional, List
import logging

# Absolute imports
from src.db.repositories.document_repo import DocumentRepository
from src.db.repositories.project_repo import ProjectRepository
from src.document_processing.file_manager import FileManager
from src.streamlit.components.file_upload import render_file_upload
from src.streamlit.utils.display import show_document_list

logger = logging.getLogger(__name__)

def render_files_page(file_manager: FileManager, project_repo: Optional[ProjectRepository] = None):
    """
    Render the files management page
    
    Args:
        file_manager: FileManager instance
        project_repo: ProjectRepository instance (optional)
    """
    # Ensure file_manager is set in session state for components to access
    st.session_state['file_manager'] = file_manager
    st.title("Document Management")

    query_params = st.query_params
    filter_project_id = query_params.get("project", None)

    if filter_project_id and filter_project_id[0].isdigit():
        project_id = int(filter_project_id[0])
        st.session_state.viewing_project_docs = project_id
        if 'active_project' not in st.session_state or not st.session_state.active_project:
            st.session_state.active_project = project_id

    project_name = None
    if 'viewing_project_docs' in st.session_state and st.session_state.viewing_project_docs and project_repo:
        try:
            project = project_repo.get_project(st.session_state.viewing_project_docs)
            if project:
                project_name = project['name']
        except Exception as e:
            logger.error(f"Error getting project: {e}", exc_info=True)

    st.markdown("""
    <style>
    .document-title {
        font-size: 24px;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 18px;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .info-box {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    default_tab = 0
    if 'viewing_project_docs' in st.session_state and st.session_state.viewing_project_docs:
        default_tab = 1

    tab_names = ["All Documents", "Project Documents", "Upload", "Search"]
    if project_name:
        tab_names[1] = f"Project: {project_name}"

    all_tab, project_tab, upload_tab, search_tab = st.tabs(tab_names)

    with all_tab:
        st.subheader("All Documents")

        # Document filtering and sorting
        filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)

        with filter_col1:
            sort_option = st.selectbox(
                "Sort By", 
                ["Name (A-Z)", "Name (Z-A)", "Date Uploaded", "File Type", "File Size"], 
                key="sort_option"
            )
        
        with filter_col2:
            tag_filter = st.selectbox(
                "Tag Filter", 
                options=["All", "P", "B", "PB"], 
                format_func=lambda x: {
                    "All": "All Tags", 
                    "P": "Private", 
                    "B": "Business", 
                    "PB": "Private & Business"
                }.get(x, x),
                key="files_tag_filter"
            )
        
        with filter_col3:
            status_filter = st.selectbox(
                "Status Filter", 
                options=["All", "Active", "Failed"], 
                key="files_status_filter"
            )
        
        with filter_col4:
            # Add project filter
            projects = []
            if project_repo:
                try:
                    projects = project_repo.get_all_projects()
                except Exception as e:
                    logger.error(f"Error getting projects: {e}", exc_info=True)
            
            project_options = ["All"] + [p['name'] for p in projects]
            project_filter = st.selectbox(
                "Project Filter",
                options=project_options,
                key="project_filter"
            )
        
        with filter_col5:
            page_size = st.selectbox(
                "Items per page", 
                options=[10, 25, 50, 100], 
                index=1, 
                key="files_page_size"
            )

        # Initialize pagination in session state
        if 'document_page' not in st.session_state:
            st.session_state.document_page = 1

        # Convert sort option to database field name and order
        sort_mapping = {
            "Name (A-Z)": ("filename", "asc"),
            "Name (Z-A)": ("filename", "desc"),
            "Date Uploaded": ("created_at", "desc"),
            "File Type": ("content_type", "asc"),
            "File Size": ("file_size", "desc")
        }
        sort_by, sort_order = sort_mapping.get(sort_option, ("created_at", "desc"))

        # Set up filters
        tag = None if tag_filter == "All" else tag_filter
        status = None if status_filter == "All" else status_filter
        project_id = None
        
        # If a project is selected in the filter, get its ID
        if project_filter != "All" and project_repo:
            for p in projects:
                if p['name'] == project_filter:
                    project_id = p['id']
                    break

        try:
            # Get documents with filters and pagination
            documents, total_count = file_manager.get_all_documents(
                tag=tag, 
                status=status, 
                project_id=project_id, 
                page=st.session_state.document_page, 
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            # Calculate total pages
            total_pages = (total_count + page_size - 1) // page_size

            # Show pagination controls if needed
            if total_pages > 1:
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    if st.button(
                        "Previous", 
                        disabled=st.session_state.document_page <= 1, 
                        key="files_prev_page_btn", 
                        use_container_width=True
                    ):
                        st.session_state.document_page -= 1
                        st.rerun()
                
                with col2:
                    st.write(f"Page {st.session_state.document_page} of {total_pages} ({total_count} documents)")
                
                with col3:
                    if st.button(
                        "Next", 
                        disabled=st.session_state.document_page >= total_pages, 
                        key="files_next_page_btn", 
                        use_container_width=True
                    ):
                        st.session_state.document_page += 1
                        st.rerun()

            # Show the document list with all required columns
            show_document_list(
                documents, 
                include_view_button=True, 
                include_project_column=True, 
                include_linked_column=True
            )
            
        except Exception as e:
            st.error(f"Error retrieving documents: {e}")
            logger.error(f"Error in render_files_page: {e}", exc_info=True)

    # Project tab implementation
    with project_tab:
        project_id = None
        if 'viewing_project_docs' in st.session_state and st.session_state.viewing_project_docs:
            project_id = st.session_state.viewing_project_docs
            st.session_state.viewing_project_docs = None
            st.query_params.update({"project": None})
        elif 'active_project' in st.session_state and st.session_state.active_project:
            project_id = st.session_state.active_project

        if not project_id:
            st.info("Please select a project from the sidebar first.")
        else:
            try:
                if project_repo and not project_name:
                    project = project_repo.get_project(project_id)
                    if project:
                        project_name = project['name']

                st.subheader(f"Documents for: {project_name or 'Unnamed Project'}")

                documents, total_count = file_manager.get_all_documents(
                    project_id=project_id,
                    status=None
                )

                if not documents:
                    st.info("No documents attached to this project.")
                else:
                    show_document_list(
                        documents,
                        include_view_button=True,
                        include_project_column=True,
                        include_linked_column=True
                    )
            except Exception as e:
                st.error(f"Error retrieving project documents: {e}")
                logger.error(f"Error in project tab: {e}", exc_info=True)
    
    # Upload tab
    with upload_tab:
        render_file_upload(file_manager)
    
    # Search tab
    with search_tab:
        st.subheader("Document Search")
        
        # Search input
        search_query = st.text_input("Search documents", key="doc_search_query")
        
        # Search filters
        search_col1, search_col2, search_col3 = st.columns(3)
        
        with search_col1:
            search_tag_filter = st.selectbox(
                "Tag Filter", 
                options=["All", "P", "B", "PB"],
                format_func=lambda x: {
                    "All": "All Tags", 
                    "P": "Private", 
                    "B": "Business", 
                    "PB": "Private & Business"
                }.get(x, x),
                key="search_tag_filter"
            )
        
        with search_col2:
            search_status_filter = st.selectbox(
                "Status Filter", 
                options=["All", "Active", "Failed"],
                key="search_status_filter"
            )
        
        with search_col3:
            # Project filter for search
            search_project_filter = st.selectbox(
                "Project Filter",
                options=project_options,
                key="search_project_filter"
            )
        
        # Search button
        if st.button("Search", key="doc_search_btn", use_container_width=True) or search_query:
            # Convert filters
            search_tag = None if search_tag_filter == "All" else search_tag_filter
            search_status = None if search_status_filter == "All" else search_status_filter
            search_project_id = None
            
            # If a project is selected in the filter, get its ID
            if search_project_filter != "All" and project_repo:
                for p in projects:
                    if p['name'] == search_project_filter:
                        search_project_id = p['id']
                        break
            
            if search_query:
                try:
                    # Search documents
                    search_results = file_manager.document_repo.search_documents(
                        query=search_query,
                        tag=search_tag,
                        status=search_status,
                        project_id=search_project_id
                    )
                    
                    if not search_results:
                        st.info(f"No documents found matching '{search_query}'")
                    else:
                        st.success(f"Found {len(search_results)} matching documents")
                        
                        # Enrich results with project names
                        for doc in search_results:
                            try:
                                projects = file_manager.document_repo.get_projects_for_document(doc['id'])
                                doc['project_names'] = [p['name'] for p in projects] if projects else []
                            except Exception as e:
                                logger.error(f"Failed to load project names for document {doc['id']}: {e}")
                                doc['project_names'] = []
                        
                        # Display results with relevance indicators
                        show_document_list(
                            search_results,
                            include_view_button=True,
                            include_project_column=True,
                            include_linked_column=True
                        )
                except Exception as e:
                    st.error(f"Error searching documents: {e}")
                    logger.error(f"Error searching documents: {e}", exc_info=True)
            else:
                st.info("Enter a search query to find documents.")
        