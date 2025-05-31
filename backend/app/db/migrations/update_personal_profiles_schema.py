"""
Migration to update personal_profiles table with new schema
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Update personal_profiles table schema"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.begin() as conn:
        try:
            # First, drop the old table if it exists
            logger.info("Dropping old personal_profiles table if exists...")
            conn.execute(text("DROP TABLE IF EXISTS personal_profiles CASCADE"))
            
            # Create the visibility enum type
            logger.info("Creating visibility enum type...")
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE visibility_level AS ENUM ('private', 'shared', 'global');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            # Create the new table with updated schema
            logger.info("Creating new personal_profiles table...")
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
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create indexes
            logger.info("Creating indexes...")
            conn.execute(text("CREATE INDEX idx_personal_profiles_name ON personal_profiles(name)"))
            conn.execute(text("CREATE INDEX idx_personal_profiles_user_id ON personal_profiles(user_id)"))
            conn.execute(text("CREATE INDEX idx_personal_profiles_visibility ON personal_profiles(visibility)"))
            
            # Add some sample data
            logger.info("Adding sample personal profiles...")
            conn.execute(text("""
                INSERT INTO personal_profiles (name, preferred_name, relationship, organization, role, notes, visibility, user_id)
                VALUES 
                ('Johan Paulsson', 'Johan', 'colleague', 'Axis Communications', 'CTO', 
                 'Prefers data-driven discussions. Skeptical of "cloud strategy" as a concept. Values honest, direct feedback.', 
                 'shared', 'default_user'),
                 
                ('Sarah Chen', 'Sarah', 'friend', NULL, NULL,
                 'Wine enthusiast (prefers reds). Has golden retriever named Max. Teaches at local elementary school.',
                 'private', 'default_user'),
                 
                ('Example CEO', NULL, 'colleague', 'Example Corp', 'CEO',
                 'General company leadership profile for reference.',
                 'global', 'default_user')
            """))
            
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise


if __name__ == "__main__":
    run_migration()