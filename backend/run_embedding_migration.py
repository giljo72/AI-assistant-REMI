#!/usr/bin/env python3
"""
Run the embedding column migration to fix pgvector storage.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.migrations.fix_embedding_column import run_migration
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run the migration."""
    print("Starting embedding column migration...")
    print("This will convert the embedding column from Text to pgvector Vector type.")
    print()
    
    response = input("Do you want to continue? (y/n): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    db = SessionLocal()
    try:
        success = run_migration(db)
        if success:
            print("\nMigration completed successfully!")
            print("The embedding column has been converted to pgvector Vector type.")
            print("Document search should now work properly.")
        else:
            print("\nMigration failed. Please check the logs for details.")
            sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()