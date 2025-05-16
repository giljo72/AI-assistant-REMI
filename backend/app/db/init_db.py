import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .database import Base, engine, SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """Initialize database with required tables and extensions."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Setup pgvector extension
    try:
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        db.commit()
        logger.info("pgvector extension created successfully")
    except SQLAlchemyError as e:
        logger.warning(f"pgvector setup error: {str(e)}")
        logger.warning("Vector search functionality may not be available")
        logger.warning("Please install pgvector manually: https://github.com/pgvector/pgvector")
    
    # Create directory structure if it doesn't exist
    import os
    for directory in ["uploads", "processed", "logs", "hierarchy"]:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", directory)
        os.makedirs(path, exist_ok=True)
    
    logger.info("Database initialized successfully")


def main() -> None:
    """Main function to initialize database."""
    logger.info("Creating initial data")
    db = SessionLocal()
    init_db(db)
    db.close()


if __name__ == "__main__":
    main()