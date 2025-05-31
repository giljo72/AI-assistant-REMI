from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, UserRole
from app.core.auth import get_current_user as get_user_from_token
from app.core.config import settings


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token in cookie."""
    # Development bypass
    if settings.DEV_MODE and settings.DEV_BYPASS_AUTH:
        # Return a mock admin user for development
        mock_user = User(
            id="dev-user",
            username="dev_admin",
            email="dev@example.com",
            role=UserRole.ADMIN,
            is_active=True,
            is_first_login=False
        )
        return mock_user
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = get_user_from_token(db, access_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure user is an admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_optional_current_user(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if not access_token:
        return None
    
    user = get_user_from_token(db, access_token)
    return user if user and user.is_active else None