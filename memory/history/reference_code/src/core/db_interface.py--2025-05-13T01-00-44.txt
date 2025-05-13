# src/core/db_interface.py
import os
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from .config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
_session_factory = None

def get_connection_string() -> str:
    """Get the PostgreSQL connection string from settings"""
    settings = get_settings()
    db_settings = settings['database']
    
    # Get database connection parameters
    user = db_settings['user']
    password = db_settings['password']
    host = db_settings['host']
    port = db_settings['port']
    database = db_settings['database']
    
    # Build connection string
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

def initialize_engine():
    """Initialize the database engine"""
    global _engine, _session_factory
    
    try:
        connection_string = get_connection_string()
        _engine = create_engine(
            connection_string,
            pool_pre_ping=True,  # Check connection vitality on each checkout
            pool_recycle=3600,   # Recycle connections after 1 hour
            connect_args={"connect_timeout": 10}  # Timeout after 10 seconds
        )
        
        # Create a scoped session factory
        _session_factory = scoped_session(sessionmaker(bind=_engine))
        
        logger.info("Database engine initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database engine: {e}")
        return False

def get_engine():
    """Get the SQLAlchemy engine, initializing if necessary"""
    global _engine
    
    if _engine is None:
        initialize_engine()
    
    return _engine

def get_session_factory():
    """Get the SQLAlchemy session factory, initializing if necessary"""
    global _session_factory
    
    if _session_factory is None:
        initialize_engine()
    
    return _session_factory

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    session_factory = get_session_factory()
    session = session_factory()
    
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

def check_connection() -> bool:
    """Check if the database connection is working"""
    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection check failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database connection check: {e}")
        return False

def check_vector_extension() -> bool:
    """Check if pgvector extension is installed and working"""
    try:
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
            return result.scalar() == 'vector'
    except SQLAlchemyError as e:
        logger.error(f"Vector extension check failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during vector extension check: {e}")
        return False