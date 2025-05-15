#!/usr/bin/env python3
"""
Database setup script for AI Assistant.
This script initializes the database with tables and sample data.
"""

import os
import sys
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to set up the database."""
    try:
        # Import and run the database initialization
        from backend.app.db.init_db import main as init_db_main
        
        logger.info("Setting up database...")
        init_db_main()
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()