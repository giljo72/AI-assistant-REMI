#!/usr/bin/env python3
"""
Create personal_profiles table for storing information about people.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from app.core.config import settings

def run_migration():
    """Create personal_profiles table and visibility enum."""
    engine = create_engine(settings.DATABASE_URL)
    
    # First, let's check if the table already exists
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'personal_profiles'
            );
        """))
        table_exists = result.scalar()
        
        if table_exists:
            print("✓ personal_profiles table already exists")
            return
    
    # Create enum type in separate transaction
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("Creating visibility_level enum...")
            conn.execute(text("""
                CREATE TYPE visibility_level AS ENUM ('private', 'shared', 'global');
            """))
            trans.commit()
            print("✓ Created visibility_level enum")
        except ProgrammingError as e:
            trans.rollback()
            if "already exists" in str(e):
                print("✓ visibility_level enum already exists")
            else:
                raise
    
    # Create table in new transaction
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("\nCreating personal_profiles table...")
            conn.execute(text("""
                CREATE TABLE personal_profiles (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR NOT NULL,
                    preferred_name VARCHAR,
                    relationship VARCHAR NOT NULL,
                    organization VARCHAR,
                    role VARCHAR,
                    birthday DATE,
                    first_met DATE,
                    preferred_contact VARCHAR,
                    timezone VARCHAR,
                    current_focus VARCHAR,
                    notes TEXT,
                    visibility visibility_level NOT NULL DEFAULT 'private',
                    user_id VARCHAR NOT NULL DEFAULT 'default_user',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                );
            """))
            trans.commit()
            print("✓ Created personal_profiles table")
        except Exception as e:
            trans.rollback()
            print(f"❌ Failed to create table: {str(e)}")
            raise
    
    # Create indexes in separate transaction
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("\nCreating indexes...")
            conn.execute(text("""
                CREATE INDEX idx_personal_profiles_name 
                ON personal_profiles(name);
            """))
            conn.execute(text("""
                CREATE INDEX idx_personal_profiles_user_id 
                ON personal_profiles(user_id);
            """))
            trans.commit()
            print("✓ Created indexes")
        except Exception as e:
            trans.rollback()
            print(f"⚠️  Failed to create indexes (not critical): {str(e)}")
    
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    print("Running personal profiles migration...")
    run_migration()