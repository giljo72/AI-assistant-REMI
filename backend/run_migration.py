#!/usr/bin/env python
"""Run the system prompts migration"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.migrations.add_system_prompts_table import upgrade

if __name__ == "__main__":
    print("Running system prompts migration...")
    upgrade()
    print("Migration completed successfully!")