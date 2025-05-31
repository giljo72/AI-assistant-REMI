"""
Configuration settings for the AI Assistant application
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # Base paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent
    BACKEND_ROOT: Path = Path(__file__).parent.parent.parent
    
    # Database
    DATABASE_URL: str = "postgresql://assistant_user:assistant_pass@localhost/assistant_db"
    
    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "AI Assistant"
    
    # File storage
    UPLOAD_DIR: Path = PROJECT_ROOT / "data" / "uploads"
    PROCESSED_DIR: Path = PROJECT_ROOT / "data" / "processed"
    UPLOAD_FOLDER: Optional[str] = None  # Legacy support
    PROCESSED_FOLDER: Optional[str] = None  # Legacy support
    
    # Model settings
    DEFAULT_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    DEFAULT_LLM_MODEL: str = "qwen2.5:32b-instruct-q4_K_M"  # Changed to QWEN as requested
    MODEL_NAME: Optional[str] = None  # Legacy support
    EMBEDDINGS_MODEL: Optional[str] = None  # Legacy support
    
    # NIM settings
    NGC_API_KEY: Optional[str] = None
    NIM_EMBEDDINGS_URL: str = "http://localhost:8002"
    NIM_GENERATION_URL: str = "http://localhost:8001"
    
    # Ollama settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Processing settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Features
    PGVECTOR_AVAILABLE: bool = True
    
    # Self-aware mode
    SELF_AWARE_PASSWORD: str = "dev-mode-2024"
    
    # Authentication settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    DEV_MODE: bool = True
    DEV_BYPASS_AUTH: bool = False  # Set to True to bypass auth in dev
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

def get_settings():
    """Get application settings"""
    return Settings()

# Create singleton instance
settings = get_settings()