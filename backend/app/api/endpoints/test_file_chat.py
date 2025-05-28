"""
Test endpoint for file reading in chat
"""
from fastapi import APIRouter
from pydantic import BaseModel
import logging

from ...services.file_reader_service import get_file_reader

logger = logging.getLogger(__name__)
router = APIRouter()

class TestRequest(BaseModel):
    message: str

@router.post("/test-file-chat")
async def test_file_chat(request: TestRequest):
    """Test endpoint that shows exactly what the AI should receive"""
    
    # Try to read a file mentioned in the message
    file_reader = get_file_reader()
    
    # Simple pattern to find file names
    import re
    file_pattern = r'\b(\w+\.py|test\.md)\b'
    matches = re.findall(file_pattern, request.message, re.IGNORECASE)
    
    response = {
        "message": request.message,
        "files_found": matches,
        "file_contents": {}
    }
    
    for file_name in matches:
        result = file_reader.read_file(file_name)
        if result["success"]:
            response["file_contents"][file_name] = {
                "success": True,
                "content_preview": result["content"][:500] + "...",
                "full_length": len(result["content"])
            }
        else:
            response["file_contents"][file_name] = {
                "success": False,
                "error": result.get("error", "Unknown error")
            }
    
    # What the AI should receive
    ai_context = f"""
FILE CONTENTS:
{'='*60}
"""
    
    for file_name, file_data in response["file_contents"].items():
        if file_data["success"]:
            full_content = file_reader.read_file(file_name)["content"]
            ai_context += f"\n=== {file_name} ===\n```python\n{full_content}\n```\n{'='*60}\n"
    
    response["ai_should_receive"] = ai_context if response["file_contents"] else "No files to display"
    
    return response