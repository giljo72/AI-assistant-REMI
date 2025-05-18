"""
Simple script to check database connectivity
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def check_db_connection():
    """Check if we can connect to the database"""
    try:
        # Get database URL from environment or use default
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:4010@localhost/ai_assistant")
        
        print(f"Trying to connect to: {DATABASE_URL}")
        
        # Create SQLAlchemy engine
        engine = create_engine(DATABASE_URL)
        
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")
            
            # Try to get table names
            result = connection.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            ))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"Found {len(tables)} tables: {', '.join(tables)}")
            else:
                print("No tables found. Database might be empty.")
            
            return True
    
    except SQLAlchemyError as e:
        print(f"Database connection error: {e}")
        return False

if __name__ == "__main__":
    success = check_db_connection()
    sys.exit(0 if success else 1)