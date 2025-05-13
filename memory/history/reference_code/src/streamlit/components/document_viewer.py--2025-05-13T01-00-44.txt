import streamlit as st
import os
from pathlib import Path
import sys
import base64
from typing import Dict, Any, Optional, List
import logging

# Add parent directory to path to import project modules
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.db.repositories.document_repo import DocumentRepository
from src.document_processing.text_processor import TextProcessor
from src.document_processing.pdf_processor import PDFProcessor
from src.document_processing.spreadsheet_processor import SpreadsheetProcessor

logger = logging.getLogger(__name__)

def get_file_extension(filename):
    """Get the file extension from a filename"""
    return os.path.splitext(filename)[1].lower()

def render_document_viewer(document_id, highlight_chunk: Optional[str] = None):
    """
    Render a document viewer for the given document ID
    
    Args:
        document_id: ID of the document to view
        highlight_chunk: Optional text chunk to highlight
    """
    if not document_id:
        st.info("No document selected. Please select a document to view.")
        return
    
    # Get document details
    document_repo = DocumentRepository()
    document = document_repo.get_document(document_id)
    
    if not document:
        st.error(f"Document with ID {document_id} not found.")
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
    
    # If we have a chunk to highlight, show it
    if highlight_chunk:
        st.markdown("---")
        st.markdown("### Highlighted Section")
        with st.container(border=True):
            st.markdown(highlight_chunk)
        
        # Add a button to view the document without highlighting
        if st.button(
            "View Full Document Without Highlighting", 
            key="doc_view_no_highlight_btn",
            use_container_width=True
        ):
            # Clear the query parameter for highlight_chunk
            params = st.query_params
            if "highlight_chunk" in params:
                del params["highlight_chunk"]
            st.rerun()
        
        st.markdown("---")
    
    # Display document content based on file type
    file_path = document['file_path']
    extension = get_file_extension(document['filename'])
    
    # Check if file exists
    if not os.path.exists(file_path):
        st.error(f"File not found at: {file_path}")
        return
    
    # Navigation buttons
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button(
            "← Back", 
            key="doc_back_btn",
            help="Return to documents list"
        ):
            # Go back to Files page
            st.query_params.update({"nav": "Files"})
            st.rerun()
    
    # Display file content based on type
    try:
        if extension in ['.txt', '.md', '.py', '.json', '.csv']:
            # For text files
            display_text_file(file_path, highlight_chunk)
        elif extension == '.pdf':
            # For PDF files
            display_pdf_file(file_path, highlight_chunk)
        elif extension in ['.xlsx', '.xls']:
            # For Excel files
            display_excel_file(file_path)
        elif extension in ['.docx', '.doc']:
            # For Word documents
            display_word_file(file_path, highlight_chunk)
        elif extension in ['.jpg', '.jpeg', '.png', '.gif']:
            # For images
            display_image_file(file_path)
        else:
            st.warning(f"Preview not available for {extension} files.")
            
    except Exception as e:
        logger.error(f"Error displaying file: {str(e)}")
        st.error(f"Error displaying file: {str(e)}")

def get_highlighted_chunk_from_session():
    """Get the highlighted chunk from session state"""
    if 'viewing_chunk' in st.session_state:
        chunk = st.session_state.viewing_chunk
        # Clear it from session state to prevent it from persisting
        del st.session_state.viewing_chunk
        return chunk
    return None

# Keep existing functions below (display_text_file, display_pdf_file, etc.)

def display_text_file(file_path, highlight_text=None):
    """
    Display the content of a text file
    
    Args:
        file_path: Path to the text file
        highlight_text: Optional text to highlight
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # If we have text to highlight, try to locate it
            if highlight_text and highlight_text in content:
                # Split content around the highlighted text
                before, after = content.split(highlight_text, 1)
                
                # Calculate context window (showing some text before and after)
                context_size = 300  # characters
                context_before = before[-context_size:] if len(before) > context_size else before
                context_after = after[:context_size] if len(after) > context_size else after
                
                # Display with highlighting
                st.markdown("### Context Window")
                st.text(context_before)
                st.markdown("**Highlighted text:**")
                st.markdown(f"<div style='background-color: #ffff0030; padding: 10px;'>{highlight_text}</div>", unsafe_allow_html=True)
                st.text(context_after)
                
                # Also display full content
                st.markdown("### Full Document")
            
            st.text_area("File Content", value=content, height=400, key="doc_text_content")
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
                st.text_area("File Content", value=content, height=400, key="doc_text_content_latin")
        except Exception as e:
            st.error(f"Could not decode file: {str(e)}")
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

def display_pdf_file(file_path, highlight_text=None):
    """
    Display a PDF file using an iframe
    
    Args:
        file_path: Path to the PDF file
        highlight_text: Optional text to highlight
    """
    # Create a PDF processor to extract text
    processor = PDFProcessor()
    try:
        # Extract text
        text = processor.extract_text(file_path)
        
        # If we have text to highlight, try to locate it
        if highlight_text and highlight_text in text:
            # Display the highlighted section
            st.subheader("Highlighted Text")
            st.markdown(f"<div style='background-color: #ffff0030; padding: 10px; margin-bottom: 20px;'>{highlight_text}</div>", unsafe_allow_html=True)
        else:
            # Show the first 1000 characters as a preview
            preview = text[:1000]
            st.subheader("Text Preview")
            st.text_area("PDF Content Preview", value=preview + ("..." if len(text) > 1000 else ""), height=200, key="doc_pdf_preview")
        
        # Display PDF in an iframe
        st.subheader("PDF Viewer")
        display_pdf_as_iframe(file_path)
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        st.error(f"Error processing PDF: {str(e)}")

def display_pdf_as_iframe(file_path):
    """Display a PDF file using an iframe"""
    # Read PDF file
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    
    # Display PDF in iframe
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def display_excel_file(file_path):
    """Display an Excel file as a table"""
    try:
        processor = SpreadsheetProcessor()
        sheets_data = processor.extract_tables(file_path)
        
        if not sheets_data:
            st.warning("No data found in the Excel file.")
            return
        
        # Create tabs for each sheet
        sheet_names = list(sheets_data.keys())
        if len(sheet_names) > 1:
            tabs = st.tabs(sheet_names)
            
            for i, sheet_name in enumerate(sheet_names):
                with tabs[i]:
                    st.dataframe(sheets_data[sheet_name], height=400)
        else:
            # Single sheet
            sheet_name = sheet_names[0]
            st.subheader(f"Sheet: {sheet_name}")
            st.dataframe(sheets_data[sheet_name], height=400)
    except Exception as e:
        logger.error(f"Error displaying Excel file: {str(e)}")
        st.error(f"Error displaying Excel file: {str(e)}")

def display_word_file(file_path, highlight_text=None):
    """
    Display a Word document as text
    
    Args:
        file_path: Path to the Word file
        highlight_text: Optional text to highlight
    """
    try:
        # Use text processor for Word documents
        processor = TextProcessor()
        text = processor.extract_text(file_path)
        
        # If we have text to highlight, try to locate it
        if highlight_text and highlight_text in text:
            # Split content around the highlighted text
            before, after = text.split(highlight_text, 1)
            
            # Calculate context window (showing some text before and after)
            context_size = 300  # characters
            context_before = before[-context_size:] if len(before) > context_size else before
            context_after = after[:context_size] if len(after) > context_size else after
            
            # Display with highlighting
            st.markdown("### Context Window")
            st.text(context_before)
            st.markdown("**Highlighted text:**")
            st.markdown(f"<div style='background-color: #ffff0030; padding: 10px;'>{highlight_text}</div>", unsafe_allow_html=True)
            st.text(context_after)
            
            # Also display full content
            st.markdown("### Full Document")
        
        st.text_area("Document Content", value=text, height=400, key="doc_word_content")
    except Exception as e:
        logger.error(f"Error displaying Word document: {str(e)}")
        st.error(f"Error displaying Word document: {str(e)}")

def display_image_file(file_path):
    """Display an image file"""
    try:
        st.image(file_path, caption=os.path.basename(file_path))
    except Exception as e:
        logger.error(f"Error displaying image: {str(e)}")
        st.error(f"Error displaying image: {str(e)}")

def render_document_chunk_explorer(retrieved_chunks: List[Dict[str, Any]], document_repo: DocumentRepository):
    """
    Render an explorer for document chunks used in RAG
    
    Args:
        retrieved_chunks: List of retrieved chunks from RAG
        document_repo: Document repository to fetch document data
    """
    # Import the shared component
    from src.streamlit.components.document_chunks import render_document_chunk_list, render_relevance_help
    
    if not retrieved_chunks:
        st.info("No document chunks were used in this response")
        return
    
    # Display document sources
    st.markdown("The following document sources were used to answer your question:")
    
    # Create a column for filtering options
    col1, col2 = st.columns([3, 1])
    with col2:
        filter_option = st.selectbox(
            "Order by", 
            ["Relevance", "Document Name", "Selection Type"],
            key="doc_explorer_sort_option"
        )
    
    # Render the document chunks in detailed mode
    render_document_chunk_list(
        chunks=retrieved_chunks,
        display_mode='detailed',
        document_repo=document_repo
    )
    
    # Add explanation about relevance scores
    render_relevance_help()
    
def get_highlighted_chunk_from_session():
    """Get the highlighted chunk from session state"""
    if 'viewing_chunk' in st.session_state:
        chunk = st.session_state.viewing_chunk
        # Clear it from session state to prevent it from persisting
        del st.session_state.viewing_chunk
        return chunk
    return None