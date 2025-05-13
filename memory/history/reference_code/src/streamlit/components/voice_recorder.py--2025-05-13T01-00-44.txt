# src/streamlit/components/voice_recorder.py
import streamlit as st
import time
from typing import Optional, Callable
import os
import tempfile
import whisper
import logging

logger = logging.getLogger(__name__)

def render_voice_recorder(on_transcription: Callable[[str], None]):
    """
    Render voice recording component with Whisper integration
    
    Args:
        on_transcription: Callback for when audio is transcribed
    """
    # Voice recording container
    st.subheader("Voice Input")
    
    # Initialize Whisper model
    if 'whisper_model' not in st.session_state:
        # Use a smaller model by default for faster loading
        # Options: "tiny", "base", "small", "medium", "large"
        model_size = "base"
        with st.spinner(f"Loading Whisper {model_size} model..."):
            try:
                st.session_state.whisper_model = whisper.load_model(model_size)
                st.success(f"Whisper {model_size} model loaded successfully!")
            except Exception as e:
                st.error(f"Failed to load Whisper model: {e}")
                logger.error(f"Failed to load Whisper model: {e}")
                return
    
    # Model settings expander
    with st.expander("Transcription Settings", expanded=False):
        model_options = ["tiny", "base", "small", "medium", "large"]
        current_model = model_size if 'whisper_model' not in st.session_state else "base"
        
        selected_model = st.selectbox(
            "Whisper Model Size", 
            options=model_options,
            index=model_options.index(current_model),
            help="Larger models are more accurate but slower to process",
            key="voice_model_size_select"
        )
        
        if selected_model != current_model and st.button(
            "Change Model", 
            key="voice_change_model_btn", 
            use_container_width=True
        ):
            with st.spinner(f"Loading Whisper {selected_model} model..."):
                try:
                    st.session_state.whisper_model = whisper.load_model(selected_model)
                    st.success(f"Whisper {selected_model} model loaded successfully!")
                except Exception as e:
                    st.error(f"Failed to load Whisper model: {e}")
                    logger.error(f"Failed to load Whisper model: {e}")
    
    # Use Streamlit's audio recorder
    audio_bytes = st.audio_recorder(
        text="Click to record audio",
        recording_color="#ffc300",
        neutral_color="#121922",
        key="voice_audio_recorder"
    )
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav", key="voice_playback")
        
        # Save to temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        with st.spinner("Transcribing audio with Whisper..."):
            try:
                # Transcribe audio using Whisper
                model = st.session_state.whisper_model
                result = model.transcribe(tmp_file_path)
                transcribed_text = result["text"]
                
                # Show the transcribed text
                st.success("Audio transcribed!")
                edited_text = st.text_area(
                    "Transcribed Text (edit if needed)", 
                    transcribed_text, 
                    height=100,
                    key="voice_transcription_edit"
                )
                
                # Buttons for actions
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(
                        "Discard", 
                        key="voice_discard_btn", 
                        use_container_width=True
                    ):
                        st.info("Transcription discarded")
                        # Clean up temp file
                        os.unlink(tmp_file_path)
                
                with col2:
                    if st.button(
                        "Use Text", 
                        key="voice_use_text_btn", 
                        use_container_width=True
                    ):
                        # Pass edited text to callback
                        on_transcription(edited_text)
                        # Clean up temp file
                        os.unlink(tmp_file_path)
                        st.info("Transcription used!")
            
            except Exception as e:
                st.error(f"Error transcribing audio: {e}")
                logger.error(f"Error transcribing audio: {e}")
                # Clean up temp file
                os.unlink(tmp_file_path)