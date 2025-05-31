from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import User, UserRole
from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password,
    get_password_hash,
    decode_access_token
)

router = APIRouter(prefix="/auth", tags=["authentication"])


class SetupStatus(BaseModel):
    needs_setup: bool
    has_admin: bool


class CreateAdminRequest(BaseModel):
    username: str
    email: str
    password: str
    recovery_pin: str


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserInfo(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    is_first_login: bool


@router.post("/login", response_model=LoginResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint that returns JWT token and sets HTTP-only cookie."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # Set HTTP-only cookie for security
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_first_login": user.is_first_login
        }
    }


@router.post("/logout")
async def logout(response: Response):
    """Logout endpoint that clears the auth cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Get current user information from JWT token."""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = get_current_user(db, access_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return UserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        is_first_login=user.is_first_login
    )


@router.post("/verify-recovery-pin")
async def verify_recovery_pin(
    username: str,
    pin: str,
    db: Session = Depends(get_db)
):
    """Verify admin recovery PIN for password reset."""
    user = db.query(User).filter(
        User.username == username,
        User.role == UserRole.ADMIN
    ).first()
    
    if not user or not user.recovery_pin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or not an admin"
        )
    
    if not verify_password(pin, user.recovery_pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid recovery PIN"
        )
    
    # Generate temporary token for password reset
    reset_token = create_access_token(
        data={"sub": user.username, "purpose": "reset"},
        expires_delta=timedelta(minutes=15)
    )
    
    return {"reset_token": reset_token}


@router.post("/reset-password")
async def reset_password(
    reset_token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """Reset password using recovery token."""
    payload = decode_access_token(reset_token)
    
    if not payload or payload.get("purpose") != "reset":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired reset token"
        )
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password reset successfully"}


@router.get("/setup-status", response_model=SetupStatus)
async def check_setup_status(db: Session = Depends(get_db)):
    """Check if initial setup is needed (no admin users exist)."""
    admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
    
    return SetupStatus(
        needs_setup=admin_count == 0,
        has_admin=admin_count > 0
    )


@router.post("/setup-admin")
async def create_initial_admin(
    admin_data: CreateAdminRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Create the initial admin account during first-time setup."""
    # Check if any admin already exists
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin account already exists"
        )
    
    # Check if username or email already taken
    existing_user = db.query(User).filter(
        (User.username == admin_data.username) | 
        (User.email == admin_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already taken"
        )
    
    # Create admin user
    admin_user = User(
        username=admin_data.username,
        email=admin_data.email,
        password_hash=get_password_hash(admin_data.password),
        recovery_pin=get_password_hash(admin_data.recovery_pin),
        role=UserRole.ADMIN,
        is_active=True,
        is_first_login=False
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    # Auto-login the new admin
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin_user.username, "role": admin_user.role.value},
        expires_delta=access_token_expires
    )
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax"
    )
    
    return {
        "message": "Admin account created successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": admin_user.id,
            "username": admin_user.username,
            "email": admin_user.email,
            "role": admin_user.role.value,
            "is_active": admin_user.is_active,
            "is_first_login": admin_user.is_first_login
        }
    }