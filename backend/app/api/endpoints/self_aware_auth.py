"""
Self-aware mode authentication endpoint.
Handles password verification for enabling write permissions.
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory session storage (in production, use Redis or database)
active_sessions: Dict[str, dict] = {}

# Get password from settings (which loads from .env)
from app.core.config import settings
SELF_AWARE_PASSWORD = settings.SELF_AWARE_PASSWORD

class AuthRequest(BaseModel):
    password: str

class AuthResponse(BaseModel):
    success: bool
    token: str
    expires_at: str

class SessionValidation(BaseModel):
    valid: bool
    mode: str

def generate_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)

def cleanup_expired_sessions():
    """Remove expired sessions from memory."""
    now = datetime.utcnow()
    expired = [token for token, session in active_sessions.items() 
               if session['expires_at'] < now]
    for token in expired:
        del active_sessions[token]

@router.post("/authenticate", response_model=AuthResponse)
async def authenticate_self_aware_mode(request: AuthRequest):
    """
    Authenticate for self-aware mode with write permissions.
    Returns a session token valid for 1 hour.
    """
    cleanup_expired_sessions()
    
    if request.password != SELF_AWARE_PASSWORD:
        logger.warning("Failed self-aware mode authentication attempt")
        raise HTTPException(status_code=403, detail="Invalid password")
    
    # Generate session token
    token = generate_session_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    # Store session
    active_sessions[token] = {
        'mode': 'self_aware',
        'created_at': datetime.utcnow(),
        'expires_at': expires_at,
        'write_permissions': True
    }
    
    logger.info("Self-aware mode authenticated successfully")
    
    return AuthResponse(
        success=True,
        token=token,
        expires_at=expires_at.isoformat()
    )

@router.post("/validate-session", response_model=SessionValidation)
async def validate_session(token: str):
    """Check if a session token is valid."""
    cleanup_expired_sessions()
    
    if token in active_sessions:
        session = active_sessions[token]
        if session['expires_at'] > datetime.utcnow():
            return SessionValidation(valid=True, mode=session['mode'])
    
    return SessionValidation(valid=False, mode="")

@router.post("/logout")
async def logout_self_aware_mode(token: str):
    """Logout and invalidate the session token."""
    if token in active_sessions:
        del active_sessions[token]
        logger.info("Self-aware mode session ended")
        return {"success": True}
    return {"success": False}

def get_current_session(token: str) -> dict:
    """Dependency to get current session if valid."""
    cleanup_expired_sessions()
    
    if token not in active_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    session = active_sessions[token]
    if session['expires_at'] < datetime.utcnow():
        del active_sessions[token]
        raise HTTPException(status_code=401, detail="Session expired")
    
    return session