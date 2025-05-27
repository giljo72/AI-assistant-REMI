#!/usr/bin/env python
"""
Install missing PDF processing libraries
"""
import subprocess
import sys

print("Installing PDF processing libraries...")
print("This will install: PyPDF2, pandas, openpyxl")
print()

# Install the packages
packages = ["PyPDF2", "pandas", "openpyxl"]

for package in packages:
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
print("\nAll packages installed successfully!")
print("\nPlease restart your backend now to use PDF extraction.")