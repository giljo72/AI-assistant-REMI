#!/usr/bin/env python3
"""
Cleanup script for AI Assistant project
Removes old test files, diagnostics, and unused scripts
Keeps files modified within last 48 hours
"""

import os
import time
from datetime import datetime, timedelta
from pathlib import Path

# Files to always keep regardless of age
KEEP_FILES = {
    'start_assistant.py',
    'stop_assistant.py',
    'install_models.py',
    'test_system.py',  # Recent comprehensive test
    'test_model_switch.py',  # Recent model test
    'test_nim_integration.py',  # Recent NIM test
    'setup_nim.py',  # NIM setup helper
    'model_reconfiguration.py',  # Recent model config
    'check_model_status.py',  # Recent status checker
}

# Files to definitely remove
REMOVE_FILES = {
    'setup_environment.py',  # Old setup script - we use venv_nemo
    'setup_new_project.py',  # Not needed
    'docker-compose-old-nemo.yml.bak',  # Old backup
    'nemo-workspace/nemo_api_server.py.bak',  # Old backup
}

# Patterns for old test/diagnostic files
OLD_PATTERNS = [
    'test_*.py',
    'check_*.py', 
    'fix_*.py',
    'diag_*.py',
    'reset_*.py',
    'batch_*.py',
    'upload_*.py',
    'direct_*.py',
    'create_db_*.py',
    '*_old.*',
    '*.bak',
    'temp_*.py',
]

def get_file_age_hours(filepath):
    """Get file age in hours"""
    file_time = os.path.getmtime(filepath)
    current_time = time.time()
    age_seconds = current_time - file_time
    return age_seconds / 3600

def should_remove_file(filepath, cutoff_hours=48):
    """Determine if file should be removed"""
    filename = os.path.basename(filepath)
    
    # Always keep certain files
    if filename in KEEP_FILES:
        return False
    
    # Always remove certain files
    if any(filepath.endswith(f) for f in REMOVE_FILES):
        return True
    
    # Check if it's an old pattern and older than cutoff
    for pattern in OLD_PATTERNS:
        if pattern.startswith('*'):
            if filename.endswith(pattern[1:]):
                return get_file_age_hours(filepath) > cutoff_hours
        elif pattern.endswith('*'):
            if filename.startswith(pattern[:-1]):
                return get_file_age_hours(filepath) > cutoff_hours
        elif '*' in pattern:
            prefix, suffix = pattern.split('*')
            if filename.startswith(prefix) and filename.endswith(suffix):
                return get_file_age_hours(filepath) > cutoff_hours
    
    return False

def cleanup_directory(directory, cutoff_hours=48, dry_run=True):
    """Clean up old files in directory"""
    removed_files = []
    kept_files = []
    
    # Backend test files
    backend_dir = os.path.join(directory, 'backend')
    if os.path.exists(backend_dir):
        for file in os.listdir(backend_dir):
            if file.endswith('.py'):
                filepath = os.path.join(backend_dir, file)
                if should_remove_file(filepath, cutoff_hours):
                    removed_files.append(filepath)
                    if not dry_run:
                        os.remove(filepath)
    
    # Scripts directory
    scripts_dir = os.path.join(directory, 'scripts')
    if os.path.exists(scripts_dir):
        for file in os.listdir(scripts_dir):
            if file.endswith('.py'):
                filepath = os.path.join(scripts_dir, file)
                age_hours = get_file_age_hours(filepath)
                
                # Keep recent files and important scripts
                if age_hours < cutoff_hours or file in KEEP_FILES:
                    kept_files.append((filepath, age_hours))
                else:
                    removed_files.append(filepath)
                    if not dry_run:
                        os.remove(filepath)
    
    # Root directory files
    for file in os.listdir(directory):
        filepath = os.path.join(directory, file)
        if os.path.isfile(filepath) and should_remove_file(filepath, cutoff_hours):
            removed_files.append(filepath)
            if not dry_run:
                os.remove(filepath)
    
    # Remove specific files
    for remove_file in REMOVE_FILES:
        filepath = os.path.join(directory, remove_file)
        if os.path.exists(filepath):
            removed_files.append(filepath)
            if not dry_run:
                os.remove(filepath)
    
    return removed_files, kept_files

def main():
    """Main cleanup function"""
    print("AI Assistant Cleanup Script")
    print("=" * 60)
    
    base_dir = "/mnt/f/assistant"
    cutoff_hours = 48
    
    print(f"Directory: {base_dir}")
    print(f"Cutoff: {cutoff_hours} hours")
    print(f"Current time: {datetime.now()}")
    print()
    
    # First do a dry run
    removed_files, kept_files = cleanup_directory(base_dir, cutoff_hours, dry_run=True)
    
    print("Files to REMOVE:")
    print("-" * 60)
    for filepath in sorted(removed_files):
        age = get_file_age_hours(filepath)
        print(f"  {filepath} (age: {age:.1f} hours)")
    
    print(f"\nTotal files to remove: {len(removed_files)}")
    
    print("\nRecent files to KEEP:")
    print("-" * 60)
    for filepath, age in sorted(kept_files, key=lambda x: x[1]):
        if age < cutoff_hours:
            print(f"  {filepath} (age: {age:.1f} hours)")
    
    if removed_files:
        print("\nProceeding with deletion...")
        removed_files, _ = cleanup_directory(base_dir, cutoff_hours, dry_run=False)
        print(f"\nRemoved {len(removed_files)} files.")
    else:
        print("\nNo files to remove.")

if __name__ == "__main__":
    main()