import sys
import os
from sqlalchemy import inspect, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from app.db.database import engine, Base
from app.db.models.document import Document
from app.document_processing.status_tracker import status_tracker

def print_separator():
    print("-" * 50)

def check_db_connection():
    """Check if we can connect to the database."""
    try:
        connection = engine.connect()
        print("✅ Successfully connected to the database!")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Failed to connect to the database: {str(e)}")
        return False

def print_document_model():
    """Print the Document model structure."""
    print_separator()
    print("Document Model Fields:")
    try:
        inspector = inspect(Document)
        for column in inspector.columns:
            print(f"  - {column.name}: {column.type}")
        return True
    except Exception as e:
        print(f"❌ Error inspecting Document model: {str(e)}")
        return False

def check_status_tracker():
    """Check if the status tracker is functioning."""
    print_separator()
    print("Status Tracker Status:")
    try:
        status = status_tracker.get_status()
        print(f"✅ Status tracker is working! Current status:")
        for key, value in status.items():
            print(f"  - {key}: {value}")
        return True
    except Exception as e:
        print(f"❌ Error with status tracker: {str(e)}")
        print(f"Tracker type: {type(status_tracker)}")
        return False

def check_tables():
    """Check what tables exist in the database."""
    print_separator()
    print("Database Tables:")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if not tables:
            print("❌ No tables found in the database!")
            return False
        
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
        return True
    except Exception as e:
        print(f"❌ Error checking tables: {str(e)}")
        return False

def create_test_document():
    """Try to create a test document directly."""
    print_separator()
    print("Creating Test Document:")
    from sqlalchemy.orm import Session
    
    try:
        # Create a document directly
        with Session(engine) as session:
            doc = Document(
                id="test-123",
                filename="test_doc.txt",
                filepath="/path/to/file.txt",
                filetype="txt",
                filesize=123,
                description="Test document"
            )
            
            # Print the document attributes
            print("Document attributes:")
            for column in inspect(Document).columns:
                attr_name = column.name
                value = getattr(doc, attr_name)
                print(f"  - {attr_name}: {value}")
            
            # Add to session but don't commit
            session.add(doc)
            print("✅ Test document created successfully!")
            
            # Rollback to avoid actually creating the document
            session.rollback()
        return True
    except Exception as e:
        print(f"❌ Error creating test document: {str(e)}")
        return False

def check_api_routes():
    """Check FastAPI routes for the processing status endpoint."""
    print_separator()
    print("Checking API Routes:")
    try:
        from app.main import app
        routes = [
            {"path": route.path, "methods": route.methods}
            for route in app.routes
        ]
        
        print(f"Found {len(routes)} API routes.")
        print("Looking for processing status routes...")
        
        status_routes = [route for route in routes if "processing" in route["path"]]
        if status_routes:
            print(f"✅ Found {len(status_routes)} processing routes:")
            for route in status_routes:
                print(f"  - {route['path']} [{', '.join(route['methods'])}]")
        else:
            print("❌ No processing status routes found!")
        
        return True
    except Exception as e:
        print(f"❌ Error checking API routes: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Running Database and API Check Script")
    print_separator()
    
    # Run all checks
    check_db_connection()
    check_tables() 
    print_document_model()
    create_test_document()
    check_status_tracker()
    check_api_routes()
    
    print_separator()
    print("✨ Check complete!")