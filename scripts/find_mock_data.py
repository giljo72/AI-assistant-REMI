#!/usr/bin/env python3
"""
Script to find mock data in frontend files.
"""

import os
import sys
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Find files with mock data in the frontend."""
    try:
        # Change to the project root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        frontend_dir = os.path.join(root_dir, "frontend", "src")
        
        logger.info(f"Searching for mock data in {frontend_dir}...")
        
        # Patterns to look for
        patterns = [
            r'mock\w*\s*=',  # mockProjects =, mockData =, etc.
            r'const\s+mock',  # const mock...
            r'\/\/\s*Mock',   # // Mock...
            r'\/\*\s*Mock',   # /* Mock...
        ]
        
        # Track files with mock data
        mock_files = []
        
        # Walk through the frontend directory
        for root, _, files in os.walk(frontend_dir):
            for file in files:
                if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Check if any pattern matches
                        for pattern in patterns:
                            if re.search(pattern, content):
                                relative_path = os.path.relpath(file_path, root_dir)
                                mock_files.append(relative_path)
                                break
        
        # Print results
        logger.info(f"Found {len(mock_files)} files with mock data:")
        for file in sorted(mock_files):
            logger.info(f"- {file}")
        
        # Write results to a file
        output_path = os.path.join(root_dir, "mock_files_list.txt")
        with open(output_path, 'w') as f:
            f.write(f"Files with mock data ({len(mock_files)}):\n")
            for file in sorted(mock_files):
                f.write(f"{file}\n")
        
        logger.info(f"Results saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error finding mock data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()