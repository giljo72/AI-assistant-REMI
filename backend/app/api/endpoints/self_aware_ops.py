"""
Self-aware operations that require approval.
Integrates with the approval queue for all write operations.
"""
import os
import json
from typing import Optional, Dict
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import logging

from .action_approval import approval_queue
from .secure_file_ops import secure_file_ops
from .self_aware_auth import get_current_session

logger = logging.getLogger(__name__)

router = APIRouter()

class FileWriteRequest(BaseModel):
    filepath: str
    content: str
    reason: str

class CommandExecuteRequest(BaseModel):
    command: list[str]
    working_directory: Optional[str] = None
    reason: str

class FileReadRequest(BaseModel):
    filepath: str

@router.post("/write-file")
async def write_file_with_approval(
    request: FileWriteRequest,
    authorization: str = Header(...)
):
    """
    Request to write a file. Requires approval before execution.
    """
    # Extract token from header
    token = authorization.replace("Bearer ", "")
    session = get_current_session(token)
    
    if not session.get('write_permissions'):
        raise HTTPException(status_code=403, detail="No write permissions")
    
    # Create approval request
    action_id = await approval_queue.request_approval(
        action_type="file_write",
        details={
            "filepath": request.filepath,
            "content_preview": request.content[:500] + "..." if len(request.content) > 500 else request.content,
            "content_length": len(request.content),
            "reason": request.reason
        },
        session_token=token
    )
    
    # Wait for approval
    approved = await approval_queue.wait_for_approval(action_id)
    
    if not approved:
        return {
            "success": False,
            "action_id": action_id,
            "message": "File write denied by user"
        }
    
    # Execute the write
    result = await secure_file_ops.write_file(
        request.filepath,
        request.content,
        action_id
    )
    
    return {
        "success": True,
        "action_id": action_id,
        "result": result
    }

@router.post("/execute-command")
async def execute_command_with_approval(
    request: CommandExecuteRequest,
    authorization: str = Header(...)
):
    """
    Request to execute a command. Requires approval before execution.
    """
    # Extract token from header
    token = authorization.replace("Bearer ", "")
    session = get_current_session(token)
    
    if not session.get('write_permissions'):
        raise HTTPException(status_code=403, detail="No write permissions")
    
    # Create approval request
    action_id = await approval_queue.request_approval(
        action_type="command",
        details={
            "command": ' '.join(request.command),
            "command_list": request.command,
            "working_directory": request.working_directory or "F:\\assistant",
            "reason": request.reason
        },
        session_token=token
    )
    
    # Wait for approval
    approved = await approval_queue.wait_for_approval(action_id)
    
    if not approved:
        return {
            "success": False,
            "action_id": action_id,
            "message": "Command execution denied by user"
        }
    
    # Execute the command
    result = await secure_file_ops.execute_command(
        request.command,
        request.working_directory
    )
    
    return {
        "success": True,
        "action_id": action_id,
        "result": result
    }

@router.post("/read-file")
async def read_file_no_approval(
    request: FileReadRequest,
    authorization: str = Header(...)
):
    """
    Read a file. No approval needed for read operations.
    """
    # Extract token from header
    token = authorization.replace("Bearer ", "")
    session = get_current_session(token)
    
    # Read is allowed in self-aware mode
    content = await secure_file_ops.read_file(request.filepath)
    
    return {
        "success": True,
        "filepath": request.filepath,
        "content": content
    }

@router.get("/audit-log")
async def get_audit_log(
    limit: int = 50,
    authorization: str = Header(...)
):
    """
    Get the audit log of all approved/denied actions.
    """
    # Extract token from header
    token = authorization.replace("Bearer ", "")
    session = get_current_session(token)
    
    # Return action history
    history = await approval_queue.get_action_history(limit)
    
    return {
        "success": True,
        "count": len(history),
        "actions": history
    }