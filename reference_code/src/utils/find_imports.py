"""
Script to find files importing from src.utils.display

Run this from your project root directory (F:\Project_Files) with:
python find_imports.py
"""

import os
import re

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
    import_pattern = r'from\s+src\.utils\.display\s+import|import\s+src\.utils\.display'
    
    print("Searching for files importing from src.utils.display...")
    results = find_imports(search_dir, import_pattern)
    
    if results:
        print(f"\nFound {len(results)} files importing from src.utils.display:")
        for file_path in results:
            print(f"  - {file_path}")
    else:
        print("\nNo files found importing from src.utils.display")