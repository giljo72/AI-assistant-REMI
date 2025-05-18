"""
Script to verify and fix the database schema for the Document model.
"""
import os
from sqlalchemy import Column, String, Text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import traceback

# Make sure app modules can be imported 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the database configuration
from app.db.database import get_db, engine, Base
from app.db.models.document import Document

def check_document_schema():
    """Check the Document model schema in the database."""
    print("Checking Document model schema...")
    
    # Get database inspector
    inspector = inspect(engine)
    
    # Check if documents table exists
    if 'documents' not in inspector.get_table_names():
        print("❌ 'documents' table doesn't exist in the database!")
        return False
    
    # Get columns of documents table
    columns = inspector.get_columns('documents')
    column_names = [col['name'] for col in columns]
    
    print(f"Found {len(columns)} columns in 'documents' table:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
    
    # Check for important columns
    required_columns = [
        'id', 'filename', 'filepath', 'filetype', 'filesize', 
        'description', 'created_at', 'is_processed'
    ]
    
    for col_name in required_columns:
        if col_name not in column_names:
            print(f"❌ Required column '{col_name}' is missing!")
            return False
    
    print("✅ All required columns exist in the schema.")
    return True

def test_document_creation():
    """Test creating a Document object with different parameters."""
    print("\nTesting Document object creation...")
    
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Test with all valid fields
        doc1 = Document(
            id="test-doc-1",
            filename="test_doc_1.txt",
            filepath="/path/to/test_doc_1.txt",
            filetype="txt",
            filesize=123,
            description="Test document 1"
        )
        print("✅ Created Document with standard fields")
        
        # Test with additional field that might cause issues
        try:
            doc2 = Document(
                id="test-doc-2",
                filename="test_doc_2.txt",
                filepath="/path/to/test_doc_2.txt",
                filetype="txt",
                filesize=456,
                description="Test document 2",
                name="This should cause an error"  # This is the problematic field
            )
            print("❌ Creating Document with 'name' field did NOT raise an error!")
            print("   This suggests the error is elsewhere in the API code.")
        except TypeError as e:
            print(f"✅ Creating Document with 'name' field correctly raised: {e}")
            
        # Roll back changes to not affect the database
        session.rollback()
        print("✅ Session rolled back successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error during Document creation test: {e}")
        traceback.print_exc()
        session.rollback()
        return False
    finally:
        session.close()

def examine_document_class():
    """Examine the Document class definition."""
    print("\nExamining Document class definition...")
    
    # Print all attributes and their types
    attributes = inspect(Document).columns
    print(f"Document class has {len(attributes)} attributes:")
    for attr in attributes:
        print(f"  - {attr.name}: {attr.type}")
    
    # Print the __init__ signature
    import inspect as py_inspect
    print("\nDocument class __init__ signature:")
    print(py_inspect.signature(Document.__init__))
    
    # Check for any name-related attributes
    name_attrs = [attr for attr in dir(Document) if 'name' in attr.lower()]
    if name_attrs:
        print(f"\nFound name-related attributes: {name_attrs}")
    else:
        print("\nNo name-related attributes found")

if __name__ == "__main__":
    print("=" * 50)
    print("DOCUMENT MODEL DIAGNOSTICS")
    print("=" * 50)
    
    schema_ok = check_document_schema()
    creation_ok = test_document_creation()
    examine_document_class()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    if schema_ok and creation_ok:
        print("✅ Document model schema looks correct")
        print("✅ Document object creation works as expected")
        print("🔍 The issue is likely in the API layer that maps between 'name' and 'filename'")
        print("\nSuggested solutions:")
        print("1. Create a custom function to handle file uploads without using DocumentCreate")
        print("2. Modify how form data is processed in the API endpoint")
        print("3. Add a simple wrapper model that maps between 'name' and 'filename'")
    else:
        print("❌ Issues detected with the Document model or schema")
    print("=" * 50)