#!/usr/bin/env python3
"""
Simple migration to create personal_profiles table using SQLAlchemy.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.database import engine, Base
from app.db.models.personal_profile import PersonalProfile
from sqlalchemy import text

def run_migration():
    """Create tables using SQLAlchemy's create_all."""
    try:
        # First ensure the enum type exists
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                conn.execute(text("CREATE TYPE visibility_level AS ENUM ('private', 'shared', 'global');"))
                trans.commit()
                print("✓ Created visibility_level enum")
            except Exception as e:
                trans.rollback()
                if "already exists" in str(e):
                    print("✓ visibility_level enum already exists")
                else:
                    print(f"⚠️  Enum creation failed: {str(e)}")
        
        # Create all tables (this will only create tables that don't exist)
        print("\nCreating tables...")
        Base.metadata.create_all(bind=engine, tables=[PersonalProfile.__table__])
        print("✓ Tables created successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    print("Running personal profiles migration (simple version)...")
    run_migration()