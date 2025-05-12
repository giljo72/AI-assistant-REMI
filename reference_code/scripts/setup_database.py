# scripts/setup_database.py
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import time
from pathlib import Path

# Add parent directory to path to import project modules
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
env_path = project_root / "config" / ".env"
load_dotenv(env_path)

def setup_database():
    """Set up the PostgreSQL database and schema"""
    # Get connection parameters from environment
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', 5432)
    db_name = os.getenv('POSTGRES_DB', 'ai_assistant')
    
    if not password:
        password = input("Enter PostgreSQL password: ")
    
    try:
        print("Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=db_name
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if pgvector extension is installed
        print("Checking pgvector extension...")
        cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Installing pgvector extension...")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            print("pgvector extension installed successfully.")
        else:
            print("pgvector extension already installed.")

        print("Checking for existing tables and dropping them if needed...")
        # Drop tables in the correct order to respect foreign key constraints
        tables_to_drop = [
            "messages", 
            "chats", 
            "document_projects", 
            "document_embeddings", 
            "web_search_cache",
            "logs", 
            "documents", 
            "projects"
        ]

        for table in tables_to_drop:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            print(f"Dropped table {table} if it existed")    
        
        # Create schema
        print("Creating database schema...")
        
        # Document metadata
        print("Creating documents table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            content_type TEXT NOT NULL,
            tag TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            chunk_count INTEGER DEFAULT 0,
            processing_error TEXT,
            search_vector tsvector
        )
        ''')

        # Create a GIN index for full-text search
        print("Creating search index...")
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS documents_search_idx 
        ON documents USING gin(search_vector)
        ''')

        # Create a trigger to update search_vector automatically
        print("Creating search vector trigger...")
        cursor.execute('''
        CREATE OR REPLACE FUNCTION update_document_search_vector() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := 
                setweight(to_tsvector('english', COALESCE(NEW.filename, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(NEW.content_type, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(NEW.tag, '')), 'D');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER documents_search_vector_update
        BEFORE INSERT OR UPDATE ON documents
        FOR EACH ROW EXECUTE FUNCTION update_document_search_vector();
        ''')
        
        # Drop existing document_embeddings table if it exists
        print("Checking for existing document_embeddings table...")
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'document_embeddings')")
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("Dropping existing document_embeddings table...")
            cursor.execute("DROP TABLE document_embeddings")
            print("Table dropped successfully.")
        
        # Vector storage with all required columns
        print("Creating document_embeddings table with all required columns...")
        cursor.execute('''
        CREATE TABLE document_embeddings (
            id SERIAL PRIMARY KEY,
            content_hash TEXT UNIQUE NOT NULL,
            embedding vector(1536) NOT NULL,
            document_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            chunk_metadata JSONB
        )
        ''')
        
        # Add foreign key constraint
        print("Adding foreign key constraints...")
        try:
            cursor.execute('''
            ALTER TABLE document_embeddings
            ADD CONSTRAINT fk_document
            FOREIGN KEY (document_id)
            REFERENCES documents(id)
            ON DELETE CASCADE
            ''')
        except psycopg2.errors.DuplicateObject:
            print("Foreign key constraint already exists.")
        
        # Projects
        print("Creating projects table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            custom_prompt TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        ''')
        
        # Chats
        print("Creating chats table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            project_id INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
        ''')
        
        # Messages
        print("Creating messages table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
        )
        ''')
        
        # Document associations
        print("Creating document_projects table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_projects (
            id SERIAL PRIMARY KEY,
            document_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
        ''')
        
        # Logs
        print("Creating logs table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            log_type TEXT NOT NULL,
            message TEXT NOT NULL,
            details JSONB,
            entity_type TEXT,
            entity_id INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        ''')
        
        # Web search cache (optional)
        print("Creating web_search_cache table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS web_search_cache (
            id SERIAL PRIMARY KEY,
            query TEXT NOT NULL,
            results JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        ''')
        
        # Create indexes
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_tag ON documents (tag)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_status ON documents (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chats_project_id ON chats (project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages (chat_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_projects_project_id ON document_projects (project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_entity_type ON logs (entity_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_embeddings_document_id ON document_embeddings (document_id)")
        
        # Commit changes
        conn.commit()
        print("Database schema created successfully.")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

def create_process_log_file():
    """Create the process_log.txt file"""
    project_root = Path(__file__).parent.parent
    log_dir = project_root / "data" / "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = log_dir / "_process_log.txt"
    
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("# File Processing Log\n")
            f.write("# Format: TIMESTAMP | FILENAME | TAG | STATUS | [ERROR] | DESCRIPTION\n")
            f.write("# Created: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            
        print(f"Created process log file: {log_file}")
    else:
        print(f"Process log file already exists: {log_file}")

def check_ollama():
    """Check if Ollama is installed and running"""
    import requests
    
    print("Checking Ollama installation...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                print(f"Ollama is running with {len(models)} models available:")
                for model in models:
                    print(f"  - {model['name']}")
                
                # Check specifically for llama3:8b
                model_names = [model['name'] for model in models]
                if 'llama3:8b' in model_names:
                    print("✅ llama3:8b model is available")
                    return True
                else:
                    print("❌ llama3:8b model is not available. Please run: ollama pull llama3:8b")
                    return False
            else:
                print("Ollama is running but no models are available.")
                print("Please run: ollama pull llama3:8b")
                return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running. Please start Ollama with: ollama serve")
        print("If Ollama is not installed, download from: https://ollama.ai/download")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def create_default_project():
    """Create a default project if none exists"""
    try:
        import psycopg2
        
        user = os.getenv('POSTGRES_USER', 'postgres')
        password = os.getenv('POSTGRES_PASSWORD')
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', 5432)
        db_name = os.getenv('POSTGRES_DB', 'ai_assistant')
        
        if not password:
            password = input("Enter PostgreSQL password: ")
        
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=db_name
        )
        
        cursor = conn.cursor()
        
        # Check if any projects exist
        cursor.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]
        
        if project_count == 0:
            print("Creating default project...")
            cursor.execute('''
            INSERT INTO projects (name, custom_prompt)
            VALUES (%s, %s)
            RETURNING id
            ''', ("Main Project", "You are a helpful AI assistant. Provide detailed and accurate information."))
            
            project_id = cursor.fetchone()[0]
            
            # Create a default chat
            cursor.execute('''
            INSERT INTO chats (name, project_id)
            VALUES (%s, %s)
            ''', ("General Chat", project_id))
            
            conn.commit()
            print("Default project and chat created successfully.")
        else:
            print("Projects already exist, skipping default project creation.")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error creating default project: {e}")
        return False

if __name__ == "__main__":
    print("Setting up AI Assistant database and environment...")
    print("WARNING: This will reset your database and create new tables.")
    confirmation = input("Are you sure you want to continue? (y/n): ")
    
    if confirmation.lower() != 'y':
        print("Setup aborted.")
        sys.exit(0)
    
    # Create necessary directories
    project_root = Path(__file__).parent.parent
    data_dirs = [
        project_root / "data" / "uploads",
        project_root / "data" / "processed",
        project_root / "data" / "logs"
    ]
    
    for data_dir in data_dirs:
        os.makedirs(data_dir, exist_ok=True)
        print(f"Created directory: {data_dir}")
    
    # Check Ollama
    ollama_ok = check_ollama()
    if not ollama_ok:
        print("⚠️ Ollama is not properly configured. Some features may not work without it.")
        answer = input("Continue setup? (y/n): ")
        if answer.lower() != 'y':
            print("Setup aborted. Please install and start Ollama, then run this script again.")
            sys.exit(1)
    
    # Setup database
    db_success = setup_database()
    
    # Create process log file
    create_process_log_file()
    
    # Create default project
    if db_success:
        project_success = create_default_project()
    
    if db_success:
        print("\n✅ Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Make sure Ollama is installed and running with llama3:8b model")
        print("2. Start the assistant with: python -m scripts.run_assistant")
        print("   or use the launcher: AI_Assistant_Launcher.exe")
    else:
        print("\n❌ Database setup failed. Please check the error messages above.")