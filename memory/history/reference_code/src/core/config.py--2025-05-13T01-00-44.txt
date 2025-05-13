# src/core/config.py
import os
from pathlib import Path
import yaml
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Initialize configuration cache
_settings_cache: Optional[Dict[str, Any]] = None

def get_settings() -> Dict[str, Any]:
    """
    Load and return application settings from config files.
    Uses caching to avoid reloading on every call.
    """
    global _settings_cache
    
    # Return cached settings if available
    if _settings_cache is not None:
        return _settings_cache
    
    # Base paths
    base_dir = Path(__file__).parent.parent.parent
    config_dir = base_dir / "config"
    
    # Load environment variables from .env file
    env_file = config_dir / ".env"
    load_dotenv(env_file)
    
    # Load settings from YAML file
    settings_file = config_dir / "settings.yaml"
    
    if not settings_file.exists():
        raise FileNotFoundError(f"Settings file not found: {settings_file}")
    
    with open(settings_file, 'r') as f:
        settings = yaml.safe_load(f)
    
    # Convert relative paths to absolute
    if 'UPLOAD_PATH' in os.environ:
        upload_path = os.environ['UPLOAD_PATH']
        if not os.path.isabs(upload_path):
            upload_path = os.path.join(base_dir, upload_path)
        settings['upload_path'] = upload_path
    else:
        settings['upload_path'] = os.path.join(base_dir, "data/uploads")
    
    if 'PROCESSED_PATH' in os.environ:
        processed_path = os.environ['PROCESSED_PATH']
        if not os.path.isabs(processed_path):
            processed_path = os.path.join(base_dir, processed_path)
        settings['processed_path'] = processed_path
    else:
        settings['processed_path'] = os.path.join(base_dir, "data/processed")
    
    # Database settings from environment variables
    settings['database'] = {
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', ''),
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB', 'ai_assistant'),
        'schema': settings.get('database', {}).get('schema', 'public'),
        'vector_dimension': settings.get('database', {}).get('vector_dimension', 1536)
    }
    
    # Ollama settings from environment variables
    settings['ollama'] = {
        'host': os.getenv('OLLAMA_HOST', 'localhost'),
        'port': os.getenv('OLLAMA_PORT', '11434'),
        'model': os.getenv('DEFAULT_MODEL', 'llama3:8b')
    }
    
    # Cache the settings
    _settings_cache = settings
    
    return settings

def reset_settings_cache():
    """
    Reset the settings cache to force reloading on next call to get_settings()
    """
    global _settings_cache
    _settings_cache = None