# scripts/check_system.py
import os
import sys
import requests
import time
from pathlib import Path
import logging

# Add parent directory to path to import project modules
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Import dotenv for environment variables
from dotenv import load_dotenv
env_path = project_root / "config" / ".env"
load_dotenv(env_path)

def check_ollama():
    """Check if Ollama is running and the required model is available"""
    print("Checking Ollama...")
    ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
    ollama_port = os.getenv('OLLAMA_PORT', '11434')
    ollama_url = f"http://{ollama_host}:{ollama_port}/api/tags"
    
    try:
        response = requests.get(ollama_url, timeout=5)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                print(f"✅ Ollama is running with {len(models)} models available:")
                for model in models:
                    print(f"  - {model['name']}")
                
                # Check for llama3:8b specifically
                if any(model['name'] == 'llama3:8b' for model in models):
                    print("✅ llama3:8b model is available")
                else:
                    print("❌ llama3:8b model is NOT available")
                    print("   To download the model, run: ollama pull llama3:8b")
                
                return True
            else:
                print("⚠️ Ollama is running but no models are available.")
                print("   To download the required model, run: ollama pull llama3:8b")
                return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running. Please start Ollama with 'ollama serve'")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def check_database():
    """Check database connection and schema"""
    print("Checking database connection...")
    
    try:
        # Import here to avoid circular imports
        from src.core.db_interface import check_connection, get_db_session
        
        if check_connection():
            print("✅ Database connection successful")
            
            # Check for document_embeddings table and its columns
            with get_db_session() as session:
                try:
                    result = session.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'document_embeddings'")
                    columns = [row[0] for row in result]
                    
                    print(f"ℹ️ document_embeddings table has these columns: {', '.join(columns)}")
                    
                    if 'chunk_index' not in columns or 'chunk_text' not in columns:
                        print("⚠️ WARNING: Expected columns missing from document_embeddings table")
                        print("   This may cause issues with document retrieval")
                        print("   Consider resetting the database schema")
                    else:
                        print("✅ Database schema looks good")
                        
                    return True
                except Exception as e:
                    print(f"❌ Error checking database schema: {e}")
                    return False
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Error importing database modules: {e}")
        return False

if __name__ == "__main__":
    print("AI Assistant System Health Check")
    print("===============================")
    
    db_ok = check_database()
    print("\n")
    ollama_ok = check_ollama()
    
    print("\n")
    if db_ok and ollama_ok:
        print("✅ System health check passed - All services are available")
        sys.exit(0)
    else:
        print("⚠️ System health check failed - Please address the issues above")
        sys.exit(1)