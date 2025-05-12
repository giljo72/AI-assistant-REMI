# src/streamlit/components/document_chunks.py
import streamlit as st
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def render_document_chunk_list(
    chunks: List[Dict[str, Any]], 
    display_mode: str = 'compact',
    max_display: int = 3,
    show_view_button: bool = True,
    document_repo: Optional[object] = None
):
    """
    Render a list of document chunks with metadata and actions
    
    Args:
        chunks: List of document chunks with similarity scores
        display_mode: 'compact' for chat/simple view, 'detailed' for full explorer
        max_display: Number of chunks to display initially
        show_view_button: Whether to show the view button
        document_repo: Document repository for fetching additional metadata
    """
    if not chunks:
        st.info("No document chunks to display")
        return
    
    # Sort chunks by relevance
    sorted_chunks = sorted(chunks, key=lambda x: x.get('similarity', 0), reverse=True)
    
    # Group documents by document ID if in detailed mode
    if display_mode == 'detailed':
        document_groups = {}
        for chunk in sorted_chunks:
            doc_id = chunk.get('document_id')
            if doc_id not in document_groups:
                document_groups[doc_id] = []
            document_groups[doc_id].append(chunk)
        
        # Display documents grouped
        for doc_id, chunks_for_doc in document_groups.items():
            _render_document_group(chunks_for_doc, document_repo, doc_id)
    else:
        # Display compact view
        _render_compact_chunk_list(
            sorted_chunks, 
            max_display, 
            show_view_button
        )

def _render_compact_chunk_list(chunks: List[Dict[str, Any]], max_display: int, show_view_button: bool):
    """Render a compact list of chunks for chat/simple views"""
    # Show top chunks
    top_chunks = chunks[:max_display]
    
    for i, chunk in enumerate(top_chunks):
        doc_id = chunk.get('document_id')
        filename = chunk.get('filename', 'Unknown')
        relevance = chunk.get('similarity', 0) * 100  # Convert to percentage
        
        st.markdown(f"**{i+1}. {filename}** (Relevance: {relevance:.1f}%)")
        
        # Add a button to view the document
        if show_view_button and doc_id:
            if st.button(
                f"View Document", 
                key=f"chunk_view_doc_{doc_id}_{i}_btn", 
                use_container_width=True
            ):
                # Set session state for viewing document with specific chunk
                st.session_state.viewing_document = doc_id
                st.session_state.viewing_chunk = chunk.get('chunk_text', '')
                # Update URL to navigate to document view
                st.query_params.update({
                    "view_document": doc_id, 
                    "highlight_chunk": "true"
                })
                st.rerun()
    
    # Show note if there are more sources
    if len(chunks) > max_display:
        st.caption(f"+ {len(chunks) - max_display} more sources")

def _render_document_group(chunks: List[Dict[str, Any]], document_repo, doc_id: int):
    """Render a group of chunks from the same document"""
    # Get full document data
    document = document_repo.get_document(doc_id) if document_repo else None
    
    if not document:
        return
    
    # Get the highest relevance chunk for this document
    highest_relevance_chunk = max(chunks, key=lambda x: x.get('similarity', 0))
    relevance = highest_relevance_chunk.get('similarity', 0) * 100
    
    # Determine color based on relevance
    if relevance > 80:
        color = "green"
    elif relevance > 60:
        color = "orange"
    else:
        color = "gray"
    
    # Build document header with relevance bar
    document_header = f"""
    <div style="margin-bottom: 5px;">
        <div style="display: flex; align-items: center;">
            <div style="flex-grow: 1; margin-right: 10px;">
                <strong>{document['filename']}</strong>
            </div>
            <div style="width: 60px; text-align: right;">
                {relevance:.1f}%
            </div>
        </div>
        <div style="background-color: #f0f0f0; border-radius: 5px; height: 10px; width: 100%;">
            <div style="background-color: {color}; border-radius: 5px; height: 10px; width: {min(int(relevance), 100)}%;"></div>
        </div>
    </div>
    """
    
    # Create an expander for this document
    with st.expander(f"{document['filename']}", expanded=len(chunks) <= 3):
        # Display the header with relevance bar
        st.markdown(document_header, unsafe_allow_html=True)
        
        # Display document metadata
        cols = st.columns(3)
        with cols[0]:
            content_type = document['content_type'].split('/')[-1].upper() if '/' in document['content_type'] else document['content_type']
            st.markdown(f"**Type:** {content_type}")
        with cols[1]:
            tag_labels = {
                "P": "Private",
                "B": "Business",
                "PB": "Private & Business"
            }
            tag = tag_labels.get(document['tag'], document['tag'])
            st.markdown(f"**Tag:** {tag}")
        with cols[2]:
            chunk_count = len(chunks)
            st.markdown(f"**Chunks used:** {chunk_count}")
        
        # Display each chunk from this document
        for i, chunk in enumerate(sorted(chunks, key=lambda x: x.get('similarity', 0), reverse=True)):
            chunk_relevance = chunk.get('similarity', 0) * 100
            
            with st.container(border=True):
                # Show chunk metadata
                st.markdown(f"**Chunk {i+1}** (Relevance: {chunk_relevance:.1f}%)")
                
                # If page number is available, show it
                if chunk.get('page_num'):
                    st.markdown(f"**Page:** {chunk['page_num']}")
                
                # Show chunk text
                st.markdown("**Content:**")
                st.markdown(chunk.get('chunk_text', ''))
        
        # Option to view full document
        if st.button(
            "View Full Document", 
            key=f"chunk_explorer_view_{doc_id}_btn", 
            use_container_width=True
        ):
            # Set query parameters and rerun
            st.query_params.update({
                "page": "ViewDocument", 
                "doc_id": doc_id
            })
            st.rerun()

def render_relevance_help():
    """Render help text about relevance scores"""
    with st.expander("About Document Relevance"):
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