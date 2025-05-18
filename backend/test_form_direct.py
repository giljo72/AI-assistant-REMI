"""
This script tests file uploads by directly creating a Form request and
using the upload_file function from the files.py endpoint.
"""

import os
import io
import uuid
from typing import Dict, List, Optional, Any
import asyncio
from fastapi import UploadFile, BackgroundTasks, Form
from sqlalchemy.orm import Session

# Import necessary modules
from app.db.database import get_db, engine
from app.api.endpoints.files import upload_file

class MockUploadFile(UploadFile):
    """Mock UploadFile for testing."""
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.file = io.BytesIO(content)
        self.size = len(content)
        self.headers = {}
        
    async def read(self, size: int = -1) -> bytes:
        return self.file.read(size)
        
    async def seek(self, offset: int) -> None:
        self.file.seek(offset)
        
    async def close(self) -> None:
        self.file.close()

class MockBackgroundTasks(BackgroundTasks):
    """Mock BackgroundTasks for testing."""
    def __init__(self):
        self.tasks = []
        
    def add_task(self, func, *args, **kwargs):
        self.tasks.append((func, args, kwargs))

async def test_direct_form_upload():
    """Test file upload using the upload_file function directly."""
    print("Testing direct form upload...")
    
    # Create a simple test file
    test_content = b"This is a test file for direct form upload testing."
    test_filename = "test_form_upload.txt"
    
    # Create a mock UploadFile
    mock_file = MockUploadFile(filename=test_filename, content=test_content)
    
    # Create a mock BackgroundTasks
    mock_bg_tasks = MockBackgroundTasks()
    
    # Get a database session
    db = Session(engine)
    
    try:
        # Test with 'name' parameter
        print("\nTest #1: Using 'name' parameter:")
        try:
            result = await upload_file(
                background_tasks=mock_bg_tasks,
                db=db,
                file=mock_file,
                name="Test Name via Form",
                description="Test description",
                project_id=None,
                tags=None
            )
            print("✅ Upload successful with 'name' parameter!")
            print(f"Result: {result}")
        except Exception as e:
            print(f"❌ Upload failed with 'name' parameter: {e}")
            import traceback
            traceback.print_exc()
            
        # Test without 'name' parameter
        print("\nTest #2: Without 'name' parameter (using original filename):")
        try:
            mock_file.file.seek(0)  # Reset file pointer
            result = await upload_file(
                background_tasks=mock_bg_tasks,
                db=db,
                file=mock_file,
                name=None,
                description="Test description without name",
                project_id=None,
                tags=None
            )
            print("✅ Upload successful without 'name' parameter!")
            print(f"Result: {result}")
        except Exception as e:
            print(f"❌ Upload failed without 'name' parameter: {e}")
            import traceback
            traceback.print_exc()
            
        return True
    
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Close the database session
        db.close()
        
        # Close the mock file
        await mock_file.close()
        
        print("\nTest resources cleaned up")

if __name__ == "__main__":
    success = asyncio.run(test_direct_form_upload())
    print("\n" + "="*50)
    if success:
        print("✅ Direct form upload test completed!")
    else:
        print("❌ Direct form upload test failed!")
    print("="*50)