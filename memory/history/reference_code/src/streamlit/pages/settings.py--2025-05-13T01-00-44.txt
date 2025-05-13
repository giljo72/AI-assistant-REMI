# src/streamlit/pages/settings.py
import streamlit as st
import time
from typing import Dict, Any, Optional, List
import logging
import os
from pathlib import Path

# Change relative imports to absolute imports
from src.core.config import get_settings, reset_settings_cache
from src.core.logger import Logger
from src.core.llm_interface import OllamaInterface

logger = logging.getLogger(__name__)

def render_settings_page(custom_logger: Logger, ollama: OllamaInterface):
    """
    Render the settings page
    
    Args:
        custom_logger: Logger instance
        ollama: OllamaInterface instance
    """
    st.title("Settings")
    
    # Create tabs for different settings sections
    system_tab, logs_tab, model_tab = st.tabs(["System", "Logs", "LLM Model"])
    
    with system_tab:
        st.subheader("System Information")
        
        # Get settings
        settings = get_settings()
        
        # System information
        st.write("**Paths**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"Upload Path: `{settings['upload_path']}`")
            st.write(f"Processed Path: `{settings['processed_path']}`")
        
        with col2:
            # Check if paths exist
            upload_exists = os.path.exists(settings['upload_path'])
            processed_exists = os.path.exists(settings['processed_path'])
            
            st.write(f"Upload Path Exists: {'✅' if upload_exists else '❌'}")
            st.write(f"Processed Path Exists: {'✅' if processed_exists else '❌'}")
        
        st.write("**Database**")
        
        st.write(f"Database Host: `{settings['database']['host']}`")
        st.write(f"Database Name: `{settings['database']['database']}`")
        
        # Test database connection
        if st.button(
            "Test Database Connection", 
            key="settings_test_db_btn", 
            use_container_width=True
        ):
            from src.core.db_interface import check_connection, check_vector_extension
            
            conn_ok = check_connection()
            if conn_ok:
                st.success("Database connection successful!")
                
                # Check vector extension
                vec_ok = check_vector_extension()
                if vec_ok:
                    st.success("pgvector extension is installed and working!")
                else:
                    st.error("pgvector extension is not installed or not working!")
            else:
                st.error("Database connection failed! Check your settings and ensure PostgreSQL is running.")
    
    with logs_tab:
        st.subheader("System Logs")
        
        # Get recent logs
        recent_logs = custom_logger.get_recent_file_logs(count=50)
        error_logs = custom_logger.get_error_logs(count=50)
        
        # Create tabs for different log types
        all_logs_tab, error_logs_tab = st.tabs(["All Logs", "Error Logs"])
        
        with all_logs_tab:
            if not recent_logs:
                st.info("No logs found.")
            else:
                st.code("\n".join(recent_logs))
                
                # Download button
                log_content = "\n".join(recent_logs)
                st.download_button(
                    label="Download Logs",
                    data=log_content,
                    file_name="file_process_logs.txt",
                    mime="text/plain",
                    key="settings_download_logs_btn",
                    use_container_width=True
                )
        
        with error_logs_tab:
            if not error_logs:
                st.info("No error logs found.")
            else:
                st.code("\n".join(error_logs), language="plain")
                
                # Add download button for error logs
                error_log_content = "\n".join(error_logs)
                st.download_button(
                    label="Download Error Logs",
                    data=error_log_content,
                    file_name="error_logs.txt",
                    mime="text/plain",
                    key="settings_download_error_logs_btn",
                    use_container_width=True
                )
    
    with model_tab:
        st.subheader("LLM Model Settings")
        
        # Model information
        st.write(f"Current Model: **{ollama.model}**")
        
        # Check if model is available
        model_available = ollama.check_model()
        
        if model_available:
            st.success(f"Model '{ollama.model}' is available in Ollama!")
        else:
            st.error(f"Model '{ollama.model}' is not available in Ollama! Please check Ollama configuration.")
            
            # Show download button
            if st.button(
                f"Download {ollama.model}", 
                key="settings_download_model_btn", 
                use_container_width=True
            ):
                st.info(f"To download the model, open a terminal and run:\n\n`ollama pull {ollama.model}`")
        
        # Temperature setting
        st.write("### Generation Settings")
        
        if 'temperature' not in st.session_state:
            st.session_state.temperature = 0.7
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
            help="Higher values make output more random, lower values more deterministic",
            key="settings_temperature_slider"
        )
        
        if temperature != st.session_state.temperature:
            st.session_state.temperature = temperature
            st.info(f"Temperature set to {temperature}")
        
        # Test generation
        st.write("### Test Generation")
        
        test_prompt = st.text_area(
            "Enter a test prompt",
            value="What can you tell me about vector databases?",
            height=100,
            key="settings_test_prompt"
        )
        
        if st.button(
            "Generate Test Response", 
            key="settings_test_generate_btn", 
            use_container_width=True
        ):
            with st.spinner("Generating response..."):
                response = ollama.generate(
                    prompt=test_prompt,
                    temperature=temperature
                )
                
                st.write("### Response:")
                st.write(response)
                
                # Add option to save response
                if st.button(
                    "Save Response to File", 
                    key="settings_save_response_btn", 
                    use_container_width=True
                ):
                    st.download_button(
                        label="Download Response",
                        data=response,
                        file_name="ollama_response.txt",
                        mime="text/plain",
                        key="settings_download_response_btn",
                        use_container_width=True
                    )