"""
Migration to add system_prompts table
"""
from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upgrade():
    """Create system_prompts table"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Create the system_prompts table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS system_prompts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL UNIQUE,
                content TEXT NOT NULL,
                description TEXT,
                category VARCHAR(100),
                is_active BOOLEAN DEFAULT FALSE,
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ
            );
        """))
        
        # Create an index on is_active for faster queries
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_system_prompts_active 
            ON system_prompts(is_active);
        """))
        
        # Create an index on category for filtering
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_system_prompts_category 
            ON system_prompts(category);
        """))
        
        # Add a trigger to ensure only one active system prompt
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION ensure_single_active_system_prompt()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.is_active = TRUE THEN
                    UPDATE system_prompts 
                    SET is_active = FALSE 
                    WHERE id != NEW.id AND is_active = TRUE;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        conn.execute(text("""
            DROP TRIGGER IF EXISTS trg_ensure_single_active_system_prompt ON system_prompts;
            CREATE TRIGGER trg_ensure_single_active_system_prompt
            BEFORE INSERT OR UPDATE ON system_prompts
            FOR EACH ROW
            EXECUTE FUNCTION ensure_single_active_system_prompt();
        """))
        
        # Add update trigger for updated_at
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        conn.execute(text("""
            DROP TRIGGER IF EXISTS update_system_prompts_updated_at ON system_prompts;
            CREATE TRIGGER update_system_prompts_updated_at
            BEFORE UPDATE ON system_prompts
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """))
        
        conn.commit()
        logger.info("Successfully created system_prompts table")

def downgrade():
    """Drop system_prompts table"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS system_prompts CASCADE;"))
        conn.execute(text("DROP FUNCTION IF EXISTS ensure_single_active_system_prompt() CASCADE;"))
        conn.commit()
        logger.info("Successfully dropped system_prompts table")

if __name__ == "__main__":
    upgrade()