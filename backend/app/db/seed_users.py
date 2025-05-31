"""
Seed script to create development/test users.

This script creates:
- Admin user: admin/admin123 (with recovery PIN: 1234)
- Test user: testuser/test123

Run this script for development/testing purposes only.
"""

import logging
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from app.db.database import SessionLocal
from app.db.models import User, UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_users():
    """Create test users for development."""
    db = SessionLocal()
    
    try:
        # Test users data
        test_users = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123",
                "role": UserRole.ADMIN,
                "recovery_pin": pwd_context.hash("1234")
            },
            {
                "username": "testuser",
                "email": "testuser@example.com", 
                "password": "test123",
                "role": UserRole.USER,
                "recovery_pin": None
            }
        ]
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = db.query(User).filter(
                User.username == user_data["username"]
            ).first()
            
            if existing_user:
                logger.info(f"User {user_data['username']} already exists")
                continue
            
            # Create new user
            password = user_data.pop("password")
            user = User(
                **user_data,
                password_hash=pwd_context.hash(password)
            )
            
            db.add(user)
            logger.info(f"Created user: {user.username} ({user.role.value})")
        
        db.commit()
        logger.info("User seeding completed successfully")
        
    except IntegrityError as e:
        logger.error(f"Integrity error during seeding: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()