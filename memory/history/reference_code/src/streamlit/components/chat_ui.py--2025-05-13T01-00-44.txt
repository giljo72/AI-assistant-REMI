# src/streamlit/components/chat_ui.py
import streamlit as st
import time
from typing import Dict, Any, Optional, List, Callable
import logging

from ...chat.chat_manager import ChatManager
from ..utils.display import render_chat_messages

logger = logging.getLogger(__name__)

def render_chat_ui(chat_manager: ChatManager, 
                  chat_id: int,
                  temperature: float = 0.7):
    """
    Render chat interface
    
    Args:
        chat_manager: ChatManager instance
        chat_id: ID of current chat
        temperature: Temperature for response generation
    """
    # Get chat details
    chat = chat_manager.get_chat(chat_id)
    if not chat:
        st.error(f"Chat not found. Please select or create a chat.")
        return
    
    # Get messages
    messages = chat_manager.get_chat_messages(chat_id)
    
    # Initialize metadata in session state if not present
    if 'response_metadata' not in st.session_state:
        st.session_state.response_metadata = {}
    
    # Display chat header
    st.subheader(f"Chat: {chat['name']}")
    
    # Extract metadata information
    docs_applied = False
    prompt_applied = False
    retrieved_chunks = None
    manual_selection = False
    
    if st.session_state.response_metadata:
        docs_applied = st.session_state.response_metadata.get('docs_applied', False)
        prompt_applied = st.session_state.response_metadata.get('prompt_applied', False)
        retrieved_chunks = st.session_state.response_metadata.get('retrieved_chunks', None)
        manual_selection = st.session_state.response_metadata.get('manual_doc_selection', False)
    
    # Check if any documents are manually selected for this chat
    has_manual_selection = False
    if 'chat_document_selections' in st.session_state:
        current_selections = st.session_state.chat_document_selections.get(chat_id, [])
        has_manual_selection = len(current_selections) > 0
    
    # If documents are manually selected but not yet used in a response, show an indicator
    if has_manual_selection and not manual_selection and not st.session_state.response_metadata:
        st.info("✨ Custom document selection active. Ask a question to use your selected documents!")
    
    # Display messages with metadata
    render_chat_messages(
        messages, 
        docs_applied, 
        prompt_applied, 
        retrieved_chunks,
        manual_selection
    )
    
    # Display input area with voice option if available
    col1, col2 = st.columns([0.9, 0.1])
    
    with col1:
        user_input = st.chat_input("Type your message...")
    
    with col2:
        # Voice button (if configured)
        if st.session_state.get('whisper_enabled', False):
            if st.button("🎤", help="Record voice input", key="chat_voice_btn"):
                st.session_state['recording_voice'] = True
                st.rerun()
    
    # Handle voice recording if active
    if st.session_state.get('recording_voice', False):
        voice_processor = st.session_state.get('voice_processor')
        if voice_processor:
            with st.container(border=True):
                st.write("🎙️ Recording voice input...")
                
                # Add a stop button
                if st.button("Stop Recording", key="chat_stop_recording_btn", use_container_width=True):
                    # Process the recording and get the transcription
                    with st.spinner("Transcribing..."):
                        try:
                            transcription = voice_processor.record_and_transcribe()
                            if transcription:
                                # Allow editing before sending
                                user_input = st.text_area(
                                    "Edit transcription:", 
                                    transcription, 
                                    height=100,
                                    key="chat_transcription_edit"
                                )
                                
                                if st.button("Send", key="chat_send_transcription_btn", use_container_width=True):
                                    # Use the transcription as user input
                                    st.session_state['recording_voice'] = False
                                    st.rerun()
                        except Exception as e:
                            logger.error(f"Error recording voice: {e}")
                            st.error(f"Error recording voice: {str(e)}")
                            st.session_state['recording_voice'] = False
    
    # Process input
    if user_input:
        # Show user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Process message and get response
        with st.spinner("Thinking..."):
            try:
                # Process user message and get response
                assistant_message, metadata = chat_manager.process_user_message(
                    chat_id=chat_id,
                    content=user_input,
                    temperature=temperature
                )
                
                # Store metadata for next render
                st.session_state.response_metadata = metadata
                
                # Show assistant response
                with st.chat_message("assistant"):
                    st.write(assistant_message['content'])
                
                # Force rerun to update UI with new message
                st.rerun()
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                st.error(f"Error generating response: {str(e)}")
        
    # Add a chat tools expander
    with st.expander("Chat Tools"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Temperature slider
            new_temp = st.slider(
                "Response creativity", 
                min_value=0.1, 
                max_value=1.0, 
                value=temperature,
                step=0.1,
                help="Higher values make responses more creative but potentially less accurate",
                key="chat_temperature_slider"
            )
            if new_temp != temperature:
                # Update temperature in session state
                st.session_state['chat_temperature'] = new_temp
        
        with col2:
            # Export chat
            if st.button("Export Chat", key="chat_export_btn", use_container_width=True):
                try:
                    export_data = chat_manager.export_chat(chat_id)
                    
                    # Convert to downloadable format
                    import json
                    export_str = json.dumps(export_data, indent=2)
                    
                    # Create download button
                    st.download_button(
                        label="Download Chat Export",
                        data=export_str,
                        file_name=f"chat_export_{chat_id}.json",
                        mime="application/json",
                        key="chat_download_export_btn"
                    )
                except Exception as e:
                    logger.error(f"Error exporting chat: {e}")
                    st.error(f"Error exporting chat: {str(e)}")
        
        with col3:
            # Clear chat
            if st.button("Clear Chat History", key="chat_clear_history_btn", use_container_width=True):
                st.session_state['confirm_clear_chat'] = True
                st.rerun()
    
    # Handle clear chat confirmation
    if st.session_state.get('confirm_clear_chat', False):
        with st.popover("Confirm Clear Chat", use_container_width=True):
            st.warning("Are you sure you want to clear all messages in this chat? This action cannot be undone.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Cancel", key="chat_cancel_clear_btn", use_container_width=True):
                    st.session_state['confirm_clear_chat'] = False
                    st.rerun()
            
            with col2:
                if st.button("Clear Chat", key="chat_confirm_clear_btn", type="primary", use_container_width=True):
                    try:
                        chat_manager.clear_chat_messages(chat_id)
                        st.success("Chat history cleared successfully!")
                        st.session_state['confirm_clear_chat'] = False
                        # Clear response metadata
                        st.session_state.response_metadata = {}
                        time.sleep(1)  # Brief pause to show success message
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Error clearing chat: {e}")
                        st.error(f"Error clearing chat: {str(e)}")
                        st.session_state['confirm_clear_chat'] = False