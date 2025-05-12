# scripts/health_check.py
import os
import sys
from pathlib import Path
import logging
import requests

# Add parent directory to path to import project modules
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Set up basic logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def check_database():
    """Check database connection and models"""
    try:
        # Import necessary modules
        from src.core.db_interface import get_db_session
        from src.db.models import Document, DocumentEmbedding
        
        # Check database connection
        logger.info("Checking database connection...")
        with get_db_session() as session:
            # Try simple query
            doc_count = session.query(Document).count()
            logger.info(f"✅ Database connection successful, found {doc_count} documents")
            
            # Check if embedding model is working
            try:
                # Try to access chunk_index field to confirm it exists
                from sqlalchemy import select
                stmt = select(DocumentEmbedding.chunk_index).limit(1)
                session.execute(stmt).first()
                logger.info("✅ DocumentEmbedding model with chunk_index field is working")
                return True
            except Exception as e:
                logger.error(f"❌ Error with DocumentEmbedding model: {e}")
                return False
    except ImportError as e:
        logger.error(f"❌ Error importing database modules: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {e}")
        return False

def check_ollama():
    """Check if Ollama is running and has required models"""
    logger.info("Checking Ollama...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                logger.info(f"✅ Ollama is running with {len(models)} models available:")
                for model in models:
                    logger.info(f"  - {model['name']}")
                
                # Check for llama3:8b model
                model_names = [model['name'] for model in models]
                if 'llama3:8b' in model_names:
                    logger.info("✅ llama3:8b model is available")
                    return True
                else:
                    logger.error("❌ llama3:8b model is not available")
                    logger.info("Run: ollama pull llama3:8b")
                    return False
            else:
                logger.error("❌ Ollama has no models available")
                logger.info("Run: ollama pull llama3:8b")
                return False
        else:
            logger.error(f"❌ Ollama API returned error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ Ollama is not running")
        logger.info("Run: ollama serve")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking Ollama: {e}")
        return False

def main():
    """Run all health checks"""
    logger.info("AI Assistant System Health Check")
    logger.info("===============================")
    
    db_ok = check_database()
    ollama_ok = check_ollama()
    
    if db_ok and ollama_ok:
        logger.info("✅ All systems operational")
    else:
        logger.info("⚠️ System health check failed - Please address the issues above")

if __name__ == "__main__":
    main()