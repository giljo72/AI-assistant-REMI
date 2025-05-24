#!/usr/bin/env python3
"""
Add system prompts to the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.seed_system_prompts import seed_system_prompts

if __name__ == "__main__":
    print("Adding system prompts to database...")
    seed_system_prompts()
    print("Done!")