#!/usr/bin/env python3
import os
import shutil
import datetime
import sys

def create_backup():
    """Create a timestamped backup of the assistant project to E:\root"""
    # Get current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Source and destination paths
    source_dir = r"F:\assistant"
    backup_dir = rf"E:\root\assistant_backup_{timestamp}"
    
    print(f"Creating backup from {source_dir} to {backup_dir}")
    
    # Directories to exclude from backup
    exclude_dirs = {
        '__pycache__',
        '.pytest_cache',
        'node_modules',
        'venv',
        'venv_nemo',
        '.git',
        'nemo-models',
        'nemo-workspace',
        'logs',
        'data/models'
    }
    
    def should_exclude(path):
        """Check if a path should be excluded from backup"""
        parts = path.split(os.sep)
        return any(part in exclude_dirs for part in parts)
    
    try:
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        
        # Walk through source directory
        for root, dirs, files in os.walk(source_dir):
            # Calculate relative path
            rel_path = os.path.relpath(root, source_dir)
            
            # Skip if this path should be excluded
            if should_exclude(rel_path):
                dirs[:] = []  # Don't descend into this directory
                continue
            
            # Create corresponding directory in backup
            dest_dir = os.path.join(backup_dir, rel_path)
            if rel_path != '.':
                os.makedirs(dest_dir, exist_ok=True)
            
            # Copy files
            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, file)
                
                try:
                    shutil.copy2(src_file, dest_file)
                except Exception as e:
                    print(f"Warning: Could not copy {src_file}: {e}")
        
        print(f"\nBackup completed successfully!")
        print(f"Backup location: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print(f"Error creating backup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    backup_path = create_backup()
    print(f"\nNext steps:")
    print("1. Verify backup is complete")
    print("2. Run database migration to change vector dimensions")
    print("3. Update code to use NIM embeddings")