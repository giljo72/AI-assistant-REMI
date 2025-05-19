#!/usr/bin/env python
"""
Fix requirements.txt to use pre-built wheels instead of source packages
that require Rust compilation.
"""

import os
import sys

def fix_requirements(requirements_file):
    """Update requirements to use pre-built wheels."""
    with open(requirements_file, 'r') as f:
        lines = f.readlines()
    
    # Replace problematic dependencies with versions that have pre-built wheels
    updated_lines = []
    for line in lines:
        # Pydantic causes Rust compilation issues
        if line.strip().startswith('pydantic=='):
            # Use an older version that has pre-built wheels
            updated_lines.append('pydantic==1.10.8\n')
        else:
            updated_lines.append(line)
    
    # Write updated requirements
    with open(requirements_file, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"Updated {requirements_file} to use pre-built wheels")

def main():
    # Check if we're in the AIbot directory
    if os.path.exists('/mnt/f/AIbot'):
        requirements_file = '/mnt/f/AIbot/backend/requirements.txt'
    elif os.path.exists('F:\\AIbot'):
        requirements_file = 'F:\\AIbot\\backend\\requirements.txt'
    else:
        print("Could not find AIbot directory")
        sys.exit(1)
    
    if not os.path.exists(requirements_file):
        print(f"Could not find {requirements_file}")
        sys.exit(1)
    
    fix_requirements(requirements_file)
    print("Requirements fixed. Run setup_environment.py again.")

if __name__ == "__main__":
    main()