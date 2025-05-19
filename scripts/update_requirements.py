#!/usr/bin/env python
"""
Update the requirements.txt file to use Pydantic v1 and other pre-built wheels.
"""

import os
import sys
import shutil

def update_requirements():
    """Update the requirements.txt file for easier installation."""
    # Determine AIbot directory
    if os.path.exists('F:\\AIbot'):
        aibot_dir = 'F:\\AIbot'
    elif os.path.exists('/mnt/f/AIbot'):
        aibot_dir = '/mnt/f/AIbot'
    else:
        print("Error: AIbot directory not found")
        return False
    
    # Path to requirements file
    req_path = os.path.join(aibot_dir, 'backend', 'requirements.txt')
    backup_path = os.path.join(aibot_dir, 'backend', 'requirements.txt.bak')
    
    # Create backup
    shutil.copy2(req_path, backup_path)
    print(f"Backed up original requirements to {backup_path}")
    
    # Read current requirements
    with open(req_path, 'r') as f:
        lines = f.readlines()
    
    # Update requirements to use pre-built versions
    updated_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('pydantic=='):
            updated_lines.append('pydantic==1.10.8')
        elif line.startswith('fastapi=='):
            # Keep FastAPI version but ensure it works with Pydantic v1
            updated_lines.append(line)
        elif line.startswith('sqlalchemy=='):
            # Keep SQLAlchemy version
            updated_lines.append(line)
        elif line.startswith('numpy=='):
            # Ensure numpy has pre-built wheels
            updated_lines.append('numpy==1.24.3')
        else:
            updated_lines.append(line)
    
    # Write updated requirements
    with open(req_path, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"Updated {req_path} with compatible dependencies")
    print("You can now run the setup_environment_fixed.py script")
    return True

if __name__ == "__main__":
    success = update_requirements()
    if success:
        print("\nRequirements updated successfully.")
        print("Next steps:")
        print("1. Run 'python setup_environment_fixed.py' to set up the environment")
        print("2. If needed, you can restore the original requirements using the backup")
    else:
        print("\nFailed to update requirements.")