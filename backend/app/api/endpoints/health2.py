"""
New health check endpoints to verify API routing is working correctly.
This is a clean implementation to bypass potential issues with the original health.py module.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/ping2")
async def ping():
    """Simple ping endpoint to verify routing."""
    return {"message": "pong from health2"}

@router.get("/status2")
async def status():
    """Status endpoint to check application health."""
    return {"status": "healthy", "source": "health2 module"}