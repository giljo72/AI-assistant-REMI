from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:4010@localhost/ai_assistant")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create sessionmaker for session creation
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()