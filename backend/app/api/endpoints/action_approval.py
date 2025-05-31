"""
Action approval system for self-aware mode.
Every command and file write requires individual user approval.
"""
import os
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Optional, List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()

class ActionRequest(BaseModel):
    type: str  # 'command' or 'file_write'
    details: dict
    
class ApprovalRequest(BaseModel):
    action_id: str
    approved: bool
    
class ActionStatus(BaseModel):
    action_id: str
    type: str
    details: dict
    status: str  # 'pending', 'approved', 'denied', 'executed'
    created_at: str
    resolved_at: Optional[str]

class ActionApprovalQueue:
    def __init__(self):
        self.pending_actions: Dict[str, dict] = {}
        self.action_history: List[dict] = []
        self.websocket_connections: List[WebSocket] = []
        self.approval_events: Dict[str, asyncio.Event] = {}
        self.approval_results: Dict[str, bool] = {}
    
    async def request_approval(self, action_type: str, details: dict, session_token: str) -> str:
        """Request approval for an action. Returns action_id."""
        action_id = str(uuid.uuid4())
        
        action = {
            "id": action_id,
            "type": action_type,
            "details": details,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "session_token": session_token,
            "resolved_at": None
        }
        
        self.pending_actions[action_id] = action
        self.approval_events[action_id] = asyncio.Event()
        
        # Notify all connected clients
        await self.broadcast_action_request(action)
        
        logger.info(f"Approval requested for {action_type}: {action_id}")
        return action_id
    
    async def wait_for_approval(self, action_id: str, timeout: int = 300) -> bool:
        """Wait for user approval. Returns True if approved, False if denied."""
        if action_id not in self.approval_events:
            return False
            
        try:
            # Wait for approval with timeout (default 5 minutes)
            await asyncio.wait_for(
                self.approval_events[action_id].wait(), 
                timeout=timeout
            )
            return self.approval_results.get(action_id, False)
        except asyncio.TimeoutError:
            logger.warning(f"Approval timeout for action {action_id}")
            self.pending_actions[action_id]["status"] = "timeout"
            return False
    
    async def approve_action(self, action_id: str, approved: bool) -> bool:
        """Approve or deny an action."""
        if action_id not in self.pending_actions:
            return False
        
        action = self.pending_actions[action_id]
        action["status"] = "approved" if approved else "denied"
        action["resolved_at"] = datetime.utcnow().isoformat()
        
        # Store result and trigger event
        self.approval_results[action_id] = approved
        self.approval_events[action_id].set()
        
        # Move to history
        self.action_history.append(action)
        del self.pending_actions[action_id]
        
        # Notify clients of resolution
        await self.broadcast_action_resolution(action)
        
        logger.info(f"Action {action_id} {'approved' if approved else 'denied'}")
        return True
    
    async def broadcast_action_request(self, action: dict):
        """Broadcast new action request to all connected WebSocket clients."""
        message = {
            "type": "action_request",
            "action": action
        }
        await self._broadcast(message)
    
    async def broadcast_action_resolution(self, action: dict):
        """Broadcast action resolution to all connected WebSocket clients."""
        message = {
            "type": "action_resolved",
            "action": action
        }
        await self._broadcast(message)
    
    async def _broadcast(self, message: dict):
        """Send message to all connected WebSocket clients."""
        disconnected = []
        for websocket in self.websocket_connections:
            try:
                await websocket.send_json(message)
            except:
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for ws in disconnected:
            self.websocket_connections.remove(ws)
    
    def add_websocket(self, websocket: WebSocket):
        """Add a new WebSocket connection."""
        self.websocket_connections.append(websocket)
    
    def remove_websocket(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.websocket_connections:
            self.websocket_connections.remove(websocket)

# Global approval queue instance
approval_queue = ActionApprovalQueue()

@router.post("/request-approval", response_model=ActionStatus)
async def request_action_approval(request: ActionRequest, session_token: str):
    """Request approval for a command or file write action."""
    from .self_aware_auth import get_current_session
    
    # Validate session
    session = get_current_session(session_token)
    if not session.get('write_permissions'):
        raise HTTPException(status_code=403, detail="No write permissions")
    
    # Create approval request
    action_id = await approval_queue.request_approval(
        request.type, 
        request.details,
        session_token
    )
    
    action = approval_queue.pending_actions[action_id]
    
    return ActionStatus(
        action_id=action_id,
        type=action["type"],
        details=action["details"],
        status=action["status"],
        created_at=action["created_at"],
        resolved_at=action["resolved_at"]
    )

@router.post("/approve/{action_id}")
async def approve_action(action_id: str, request: ApprovalRequest):
    """Approve or deny a pending action."""
    success = await approval_queue.approve_action(action_id, request.approved)
    if not success:
        raise HTTPException(status_code=404, detail="Action not found")
    
    return {"success": True, "approved": request.approved}

@router.get("/pending-actions", response_model=List[ActionStatus])
async def get_pending_actions():
    """Get all pending actions awaiting approval."""
    actions = []
    for action in approval_queue.pending_actions.values():
        actions.append(ActionStatus(
            action_id=action["id"],
            type=action["type"],
            details=action["details"],
            status=action["status"],
            created_at=action["created_at"],
            resolved_at=action["resolved_at"]
        ))
    return actions

@router.get("/action-history", response_model=List[ActionStatus])
async def get_action_history(limit: int = 50):
    """Get recent action history."""
    history = approval_queue.action_history[-limit:]
    actions = []
    for action in reversed(history):
        actions.append(ActionStatus(
            action_id=action["id"],
            type=action["type"],
            details=action["details"],
            status=action["status"],
            created_at=action["created_at"],
            resolved_at=action["resolved_at"]
        ))
    return actions

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time action approval notifications."""
    await websocket.accept()
    approval_queue.add_websocket(websocket)
    
    try:
        # Send current pending actions
        for action in approval_queue.pending_actions.values():
            await websocket.send_json({
                "type": "action_request",
                "action": action
            })
        
        # Keep connection alive
        while True:
            # Wait for any message (ping/pong)
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        approval_queue.remove_websocket(websocket)