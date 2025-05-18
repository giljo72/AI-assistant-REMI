#!/usr/bin/env python
"""
Migration script to switch from mock implementation to real backend API.

This script performs the following operations:
1. Renames the old fileService.ts to fileService.mock.ts
2. Renames fileService.new.ts to fileService.ts
3. Optionally makes the same changes to MainFileManager and ProjectFileManager
4. Updates the necessary imports

Note: This script should be run from the project root directory.
"""

import os
import re
import argparse
import shutil
from pathlib import Path
import sys

# Define file paths
FRONTEND_DIR = Path("./frontend")
SERVICES_DIR = FRONTEND_DIR / "src" / "services"
COMPONENTS_DIR = FRONTEND_DIR / "src" / "components"

def confirm(message):
    """Ask for confirmation before proceeding."""
    while True:
        choice = input(f"{message} (y/n): ").lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
        print("Please respond with 'y' or 'n'")

def backup_file(file_path):
    """Create a backup of a file."""
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def replace_fileservice_implementation():
    """Replace mock fileService with real implementation."""
    mock_path = SERVICES_DIR / "fileService.ts"
    new_path = SERVICES_DIR / "fileService.new.ts"
    backup_path = SERVICES_DIR / "fileService.mock.ts"
    
    # Check if files exist
    if not mock_path.exists():
        print(f"Error: {mock_path} not found")
        return False
    
    if not new_path.exists():
        print(f"Error: {new_path} not found")
        return False
    
    # Make backup
    shutil.copy2(mock_path, backup_path)
    print(f"Backed up mock implementation to {backup_path}")
    
    # Replace the file
    shutil.copy2(new_path, mock_path)
    print(f"Replaced {mock_path} with real implementation from {new_path}")
    
    # Remove the .new file
    os.remove(new_path)
    print(f"Removed {new_path}")
    
    return True

def update_mainfilemanager():
    """Update MainFileManager to use real backend integration."""
    file_path = COMPONENTS_DIR / "file" / "MainFileManager.tsx"
    if not file_path.exists():
        print(f"Error: {file_path} not found")
        return False
    
    # Create a backup
    backup_file(file_path)
    
    # Read file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace window.mockFiles references
    content = re.sub(r'window\.mockFiles', '/* REMOVED: window.mockFiles */', content)
    
    # Replace localStorage.getItem('mockFiles') references
    content = re.sub(r"localStorage\.getItem\('mockFiles'\)", "/* REMOVED: localStorage.getItem('mockFiles') */", content)
    
    # Replace mockFileAdded event listener patterns
    content = re.sub(
        r'window\.addEventListener\([\'"]mockFileAdded[\'"]',
        '/* REMOVED: window.addEventListener("mockFileAdded"',
        content
    )
    content = re.sub(
        r'window\.removeEventListener\([\'"]mockFileAdded[\'"]',
        '/* REMOVED: window.removeEventListener("mockFileAdded"',
        content
    )
    
    # Save modified content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {file_path} to use real backend integration")
    return True

def update_projectfilemanager():
    """Update ProjectFileManager to use real backend integration."""
    file_path = COMPONENTS_DIR / "file" / "ProjectFileManager.tsx"
    if not file_path.exists():
        print(f"Error: {file_path} not found")
        return False
    
    # Create a backup
    backup_file(file_path)
    
    # Read file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace window.mockFiles references
    content = re.sub(r'window\.mockFiles', '/* REMOVED: window.mockFiles */', content)
    
    # Replace localStorage.getItem('mockFiles') references
    content = re.sub(r"localStorage\.getItem\('mockFiles'\)", "/* REMOVED: localStorage.getItem('mockFiles') */", content)
    
    # Replace mockFileAdded event listener patterns
    content = re.sub(
        r'window\.addEventListener\([\'"]mockFileAdded[\'"]',
        '/* REMOVED: window.addEventListener("mockFileAdded"',
        content
    )
    content = re.sub(
        r'window\.removeEventListener\([\'"]mockFileAdded[\'"]',
        '/* REMOVED: window.removeEventListener("mockFileAdded"',
        content
    )
    
    # Save modified content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {file_path} to use real backend integration")
    return True

def add_processing_panel():
    """Add ProcessingStatusPanel to MainFileManager."""
    file_path = COMPONENTS_DIR / "file" / "MainFileManager.tsx"
    if not file_path.exists():
        print(f"Error: {file_path} not found")
        return False
    
    # Read file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add import for ProcessingStatusPanel if not already present
    if "import ProcessingStatusPanel" not in content:
        import_pattern = r"import React, \{ useState, useEffect \} from 'react';"
        import_replacement = "import React, { useState, useEffect } from 'react';\nimport ProcessingStatusPanel from './ProcessingStatusPanel';"
        content = re.sub(import_pattern, import_replacement, content)
    
    # Add the panel component if not already present
    # Look for a good insertion point - typically above the file listing
    if "<ProcessingStatusPanel" not in content:
        # This pattern looks for a common part in the HTML structure where we'd want to insert
        panel_pattern = r'<div className="flex-grow overflow-auto">'
        panel_replacement = '<div className="flex-grow overflow-auto">\n          <ProcessingStatusPanel />'
        content = re.sub(panel_pattern, panel_replacement, content)
    
    # Save modified content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Added ProcessingStatusPanel to {file_path}")
    return True

def main():
    """Main function to run the migration."""
    parser = argparse.ArgumentParser(description="Migrate to real backend API")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompts")
    parser.add_argument("--skip-managers", action="store_true", help="Skip updating file managers")
    args = parser.parse_args()
    
    # Check if we're in the project root
    if not FRONTEND_DIR.exists() or not SERVICES_DIR.exists():
        print("Error: This script must be run from the project root directory")
        return 1
    
    print("===== Backend Migration Tool =====")
    print("This script will migrate from mock implementation to real backend API.")
    print(f"Frontend directory: {FRONTEND_DIR}")
    print(f"Services directory: {SERVICES_DIR}")
    
    if not args.no_confirm:
        if not confirm("This will replace the current fileService implementation. Continue?"):
            print("Migration cancelled.")
            return 0
    
    # Replace fileService implementation
    if not replace_fileservice_implementation():
        print("Error replacing fileService implementation")
        return 1
    
    if not args.skip_managers:
        # Update MainFileManager
        if not update_mainfilemanager():
            print("Error updating MainFileManager")
        
        # Update ProjectFileManager
        if not update_projectfilemanager():
            print("Error updating ProjectFileManager")
        
        # Add ProcessingStatusPanel
        add_processing_panel()
    
    print("\n===== Migration Complete =====")
    print("You should now be using the real backend API implementation.")
    print("To revert changes, you can use the .bak files that were created.")
    print("\nNext steps:")
    print("1. Start the backend with: cd backend && python -m uvicorn app.main:app --reload --port 8000")
    print("2. Start the frontend with: cd frontend && npm run dev")
    print("3. Test file upload, linking, and processing in the UI")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())