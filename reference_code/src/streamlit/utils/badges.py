# src/streamlit/utils/badges.py
import streamlit as st

def tag_badge(tag: str):
    """
    Display a document tag badge
    
    Args:
        tag: Document tag (P, B, or PB)
    """
    if tag == "P":
        st.markdown("""
        <div style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(0, 100, 255, 0.2); color: #0064ff;">
            Private
        </div>
        """, unsafe_allow_html=True)
    elif tag == "B":
        st.markdown("""
        <div style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(0, 200, 0, 0.2); color: #00c800;">
            Business
        </div>
        """, unsafe_allow_html=True)
    elif tag == "PB":
        st.markdown("""
        <div style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(255, 150, 0, 0.2); color: #ff9600;">
            Private & Business
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(150, 150, 150, 0.2); color: #969696;">
            {tag}
        </div>
        """, unsafe_allow_html=True)

def status_badge(status: str):
    """
    Display a document status badge
    
    Args:
        status: Document status (Active, Uploaded, Detached, Failed)
    """
    if status == "Active":
        st.markdown("""
        <div style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(0, 200, 0, 0.2); color: #00c800;">
            Active
        </div>
        """, unsafe_allow_html=True)
    elif status == "Uploaded":
        st.markdown("""
        <div style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(0, 100, 255, 0.2); color: #0064ff;">
            Uploaded
        </div>
        """, unsafe_allow_html=True)
    elif status == "Failed":
        st.markdown("""
        <div style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(255, 0, 0, 0.2); color: #ff0000;">
            Failed
        </div>
        """, unsafe_allow_html=True)
    elif status == "Detached":
        st.markdown("""
        <div style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(150, 150, 150, 0.2); color: #969696;">
            Detached
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(150, 150, 150, 0.2); color: #969696;">
            {status}
        </div>
        """, unsafe_allow_html=True)

def rag_indicators(docs_applied: bool = False, prompt_applied: bool = False):
    """
    Display RAG indicators for documents and prompt usage
    
    Args:
        docs_applied: Whether documents were used
        prompt_applied: Whether a custom prompt was used
    """
    if docs_applied or prompt_applied:
        cols = st.columns(2)
        
        if docs_applied:
            with cols[0]:
                st.markdown("""
                <div style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(0, 100, 255, 0.2); color: #0064ff;">
                    🔍 Docs Applied
                </div>
                """, unsafe_allow_html=True)
        
        if prompt_applied:
            with cols[1]:
                st.markdown("""
                <div style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: rgba(255, 195, 0, 0.2); color: #ffc300;">
                    📝 Custom Prompt
                </div>
                """, unsafe_allow_html=True)