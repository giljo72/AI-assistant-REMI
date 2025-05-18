"""
This script tests file uploads by directly interacting with the database and filesystem,
bypassing the API.
"""

import os
import uuid
import shutil
from sqlalchemy.orm import Session
from app.db.database import engine
from app.db.models.document import Document

# Define upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def test_direct_upload():
    """Test document creation by directly interacting with the database."""
    print("Testing direct document upload...")
    
    # Create a simple test file
    test_filepath = os.path.join(os.path.dirname(__file__), "test_direct_upload.txt")
    with open(test_filepath, "w") as f:
        f.write("This is a test file for direct upload testing.")
    
    try:
        # Generate a unique ID
        file_id = str(uuid.uuid4())
        original_filename = os.path.basename(test_filepath)
        filename = f"{file_id}_{original_filename}"
        
        # Copy file to upload directory
        dest_path = os.path.join(UPLOAD_DIR, filename)
        shutil.copy(test_filepath, dest_path)
        
        # Get file size and type
        filesize = os.path.getsize(dest_path)
        filetype = os.path.splitext(original_filename)[1].lstrip(".").lower() or "txt"
        
        print(f"Created file at {dest_path}")
        print(f"  - ID: {file_id}")
        print(f"  - Original filename: {original_filename}")
        print(f"  - Size: {filesize} bytes")
        print(f"  - Type: {filetype}")
        
        # Create document in database
        with Session(engine) as session:
            try:
                print("\nCreating document with these fields:")
                
                document = Document(
                    id=file_id,
                    filename=original_filename, 
                    filepath=dest_path,
                    filetype=filetype,
                    filesize=filesize,
                    description="Test direct upload"
                )
                
                print("Document object created successfully")
                
                # Print all document attributes
                print("\nDocument attributes:")
                for key, value in document.__dict__.items():
                    if not key.startswith('_'):
                        print(f"  - {key}: {value}")
                
                # Save to database
                session.add(document)
                print("\nAdded document to session")
                
                session.commit()
                print("Committed session - document saved to database!")
                
                # Verify document was saved
                saved_doc = session.get(Document, file_id)
                if saved_doc:
                    print(f"\nSuccessfully verified document with ID {file_id} in database")
                    print(f"Filename in DB: {saved_doc.filename}")
                else:
                    print("\nFailed to find document in database after commit!")
                
                return True
                
            except Exception as e:
                session.rollback()
                print(f"\n❌ Error creating document in database: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                raise
    
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
    
    finally:
        # Clean up
        if os.path.exists(test_filepath):
            os.remove(test_filepath)
        print("\nTest file cleaned up")

if __name__ == "__main__":
    success = test_direct_upload()
    print("\n" + "="*50)
    if success:
        print("✅ Direct upload test succeeded!")
    else:
        print("❌ Direct upload test failed!")
    print("="*50)