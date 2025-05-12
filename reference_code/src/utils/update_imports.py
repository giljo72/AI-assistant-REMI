"""
Script to update import statements from src.utils.display to src.utils.document_formatting

Run this from your project root directory (F:\Project_Files) with:
python update_imports.py
"""

import os
import re
import shutil

def update_imports(file_path):
    """Update imports in a file from src.utils.display to src.utils.document_formatting"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace "from src.utils.display import X" with "from src.utils.document_formatting import X"
    updated_content = re.sub(
        r'from\s+src\.utils\.display\s+import',
        'from src.utils.document_formatting import',
        content
    )
    
    # Replace "import src.utils.display" with "import src.utils.document_formatting"
    updated_content = re.sub(
        r'import\s+src\.utils\.display',
        'import src.utils.document_formatting',
        updated_content
    )
    
    # Replace "src.utils.display." with "src.utils.document_formatting."
    updated_content = re.sub(
        r'src\.utils\.display\.',
        'src.utils.document_formatting.',
        updated_content
    )
    
    # Create backup file
    backup_path = file_path + '.bak'
    shutil.copy2(file_path, backup_path)
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    return True

def find_imports(directory, pattern):
    """Find files that import the specified pattern"""
    matches = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Look for imports from src.utils.display
                        if re.search(pattern, content):
                            matches.append(file_path)
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
    
    return matches

if __name__ == "__main__":
    # Directory to search (project root)
    search_dir = "."
    
    # Pattern to search for
    import_pattern = r'from\s+src\.utils\.display\s+import|import\s+src\.utils\.display|src\.utils\.display\.'
    
    print("Searching for files using src.utils.display...")
    results = find_imports(search_dir, import_pattern)
    
    if not results:
        print("\nNo files found importing from src.utils.display")
        exit(0)
    
    print(f"\nFound {len(results)} files using src.utils.display:")
    for file_path in results:
        print(f"  - {file_path}")
    
    confirm = input("\nDo you want to update these files? (y/n): ")
    if confirm.lower() != 'y':
        print("Update cancelled.")
        exit(0)
    
    # Update imports
    updated_files = []
    for file_path in results:
        print(f"Updating {file_path}...")
        if update_imports(file_path):
            updated_files.append(file_path)
    
    print(f"\nSuccessfully updated {len(updated_files)} files.")
    print("Backup files with .bak extension have been created.")
    print("\nFiles updated:")
    for file_path in updated_files:
        print(f"  - {file_path}")