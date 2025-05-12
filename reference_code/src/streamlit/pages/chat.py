# src/streamlit/pages/chat.py
import streamlit as st
import time
from typing import Dict, Any, Optional, List
import logging

# Change relative imports to absolute imports
from src.chat.chat_manager import ChatManager
from src.db.repositories.document_repo import DocumentRepository
from src.streamlit.components.chat_ui import render_chat_ui
from src.streamlit.components.document_viewer import render_document_chunk_explorer
from src.streamlit.components.document_selector import render_document_selector

logger = logging.getLogger(__name__)

def render_chat_page(chat_manager: ChatManager, document_repo: DocumentRepository):
    """
    Render the chat page
    
    Args:
        chat_manager: ChatManager instance
        document_repo: DocumentRepository instance
    """
    st.title("AI Assistant Chat")
    
    # Check if a project is selected
    if 'active_project' not in st.session_state or not st.session_state.active_project:
        st.info("Please select a project from the sidebar first.")
        return
    
    # Check if a chat is selected
    if 'active_chat' not in st.session_state or not st.session_state.active_chat:
        st.info("Please select a chat from the sidebar or create a new one.")
        return
    
    # Get current chat and project
    chat_id = st.session_state.active_chat
    project_id = st.session_state.active_project
    
    # Initialize tabs for main chat, document explorer, and document selector
    chat_tab, docs_tab, select_docs_tab = st.tabs(["Chat", "Document Sources", "Select Documents"])
    
    with chat_tab:
        # Render the chat UI
        render_chat_ui(chat_manager, chat_id)
    
    with docs_tab:
        st.subheader("Document Sources")
        
        # Only show document explorer if we have metadata with retrieved chunks
        if ('response_metadata' in st.session_state and 
            st.session_state.response_metadata.get('retrieved_chunks')):
            
            retrieved_chunks = st.session_state.response_metadata.get('retrieved_chunks', [])
            manual_selection = st.session_state.response_metadata.get('manual_doc_selection', False)
            
            # Display help text depending on whether documents were manually selected
            if manual_selection:
                st.info("These sources were manually selected by you for this conversation.")
            else:
                st.info("These sources were automatically retrieved based on relevance to your query.")
            
            # Render the document explorer
            render_document_chunk_explorer(retrieved_chunks, document_repo)
            
            # Add a section about relevance ranking
            with st.expander("Understanding Document Relevance"):
                st.markdown("""
                **How Documents Are Ranked**
                
                Documents are ranked based on semantic similarity between your query and document content:
                
                1. **Vector Similarity**: Each document chunk is converted to a numerical vector that captures its meaning
                2. **Query Matching**: Your question is converted to the same format and compared with all document vectors
                3. **Relevance Score**: The similarity score (0-100%) indicates how closely each chunk matches your query
                
                The system prioritizes documents with higher relevance scores, but may include lower-scoring documents 
                that contain potentially useful context.
                
                **Color Coding**:
                - **Green**: Highly relevant (80-100%)
                - **Orange**: Moderately relevant (60-80%)
                - **Gray**: Less relevant but still related (<60%)
                """)
        else:
            st.info("No document sources are available for the current conversation.")
            st.markdown("""
            Document sources will appear here when:
            1. You ask a question related to your documents
            2. The AI assistant uses your documents to answer
            
            Try asking a question about the content of your documents!
            """)
            
            # Add a tip about manual document selection
            st.markdown("---")
            st.markdown("💡 **Tip**: You can manually select specific documents to use in the conversation by using the **Select Documents** tab.")
    
    with select_docs_tab:
        st.subheader("Select Documents for AI Context")
        
        # Get all documents
        all_documents = document_repo.get_documents()
        
        if not all_documents:
            st.warning("No documents available. Upload documents in the Files section before using this feature.")
        else:
            # Add more detailed instructions
            st.markdown("""
            Select specific documents to include in the AI's context when generating responses.
            Documents you select here will be prioritized over other documents in your project.
            
            **How it works**:
            1. Check the boxes next to documents you want to include
            2. Use the tabs to filter by All Documents, Project Documents, or Selected Documents
            3. Search for specific documents using the search box
            4. The 📎 icon indicates documents already attached to this project
            """)
            
            # Initialize document selections in session state if not exists
            if 'chat_document_selections' not in st.session_state:
                st.session_state.chat_document_selections = {}
            
            # Get current document selections for this chat
            current_selections = st.session_state.chat_document_selections.get(chat_id, [])
            
            # Callback for selection changes
            def on_document_selection_change(selected_doc_ids):
                st.session_state.chat_document_selections[chat_id] = selected_doc_ids
                # Update the chat manager with the selected documents
                chat_manager.set_document_context(chat_id, selected_doc_ids)
                logger.info(f"Updated document context for chat {chat_id}: {selected_doc_ids}")
                
                # Show a success message when selection changes
                if len(selected_doc_ids) > 0:
                    st.success(f"Updated document context with {len(selected_doc_ids)} selected document(s)")
                else:
                    st.info("Document context cleared. The AI will now use all project documents.")
            
            # Render the document selector
            render_document_selector(
                all_documents,
                on_document_selection_change,
                current_project_id=project_id,
                current_selections=current_selections
            )
            
            # Display currently selected documents count
            if current_selections:
                st.markdown(f"**{len(current_selections)} document(s) currently selected**")
                
                # Add a note about usage
                st.markdown("---")
                st.markdown("""
                **Note**: When documents are manually selected, the AI will:
                1. Prioritize these documents in responses
                2. Show a "Custom Doc Selection" indicator in chat
                3. Still include other relevant documents if needed, but with lower priority
                """)
                
                # Clear Selection button
                if st.button(
                    "Clear All Selections", 
                    key="chat_clear_selections_btn", 
                    use_container_width=True
                ):
                    # Clear selections for this chat
                    st.session_state.chat_document_selections[chat_id] = []
                    chat_manager.set_document_context(chat_id, [])
                    st.success("Document selections cleared")
                    st.rerun()