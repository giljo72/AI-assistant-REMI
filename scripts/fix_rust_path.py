#!/usr/bin/env python
"""
Fix Rust/Cargo PATH for Windows environment.
This script checks for Rust installation and adds it to the PATH.
"""

import os
import sys
import subprocess
import winreg
import ctypes

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def add_to_system_path(path):
    """Add a directory to system PATH"""
    try:
        with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as root:
            with winreg.OpenKey(root, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                existing_path = winreg.QueryValueEx(key, "PATH")[0]
                
                # Check if path already exists in PATH
                if path.lower() not in existing_path.lower():
                    new_path = f"{existing_path};{path}"
                    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                    print(f"Added {path} to user PATH")
                    
                    # Notify the system about the change
                    subprocess.run(["setx", "PATH", new_path], check=True, capture_output=True)
                    return True
                else:
                    print(f"{path} is already in PATH")
                    return True
    except Exception as e:
        print(f"Error adding to PATH: {str(e)}")
        return False

def check_cargo_installation():
    """Check for Cargo/Rust installation"""
    # Common Rust installation paths
    rust_paths = [
        os.path.expanduser("~/.cargo/bin"),
        os.path.expanduser("~/.rustup/toolchains/stable-x86_64-pc-windows-msvc/bin"),
        "C:\\Users\\{}\\AppData\\Local\\puccinialin\\puccinialin\\Cache\\rustup\\stable-x86_64-pc-windows-msvc\\bin".format(os.getenv("USERNAME")),
        "C:\\Users\\{}\\AppData\\Local\\puccinialin\\puccinialin\\Cache\\bin".format(os.getenv("USERNAME")),
        "C:\\Users\\{}\\AppData\\Local\\Programs\\Rust\\bin".format(os.getenv("USERNAME")),
        "C:\\Users\\{}\\AppData\\Local\\Programs\\Rust\\cargo\\bin".format(os.getenv("USERNAME")),
        "C:\\Users\\{}\\AppData\\Local\\.cargo\\bin".format(os.getenv("USERNAME")),
        "C:\\Users\\{}\\AppData\\Local\\rustup\\toolchains\\stable-x86_64-pc-windows-msvc\\bin".format(os.getenv("USERNAME")),
        "C:\\Users\\{}\\AppData\\Local\\puccinialin\\puccinialin\\Cache\\cargo\\bin".format(os.getenv("USERNAME")),
        "C:\\Users\\{}\\AppData\\Local\\puccinialin\\puccinialin\\Cache\\rustup\\stable-x86_64-pc-windows-msvc\\bin".format(os.getenv("USERNAME")),
        "C:\\Program Files\\Rust\\bin",
        "C:\\Rust\\bin"
    ]
    
    # Check if Cargo exists in any of these paths
    for path in rust_paths:
        cargo_path = os.path.join(path, "cargo.exe")
        if os.path.exists(cargo_path):
            print(f"Found Cargo at {cargo_path}")
            return path
    
    # If not found in common paths, try to find using rustup
    try:
        rustup_path = subprocess.check_output(["where", "rustup.exe"], text=True).strip()
        if rustup_path:
            cargo_dir = os.path.dirname(rustup_path)
            print(f"Found Rustup at {rustup_path}, Cargo should be in the same directory")
            return cargo_dir
    except:
        pass
    
    # Check .rustup directory structure
    rustup_home = os.path.expanduser("~/.rustup")
    if os.path.exists(rustup_home):
        print(f"Found .rustup directory at {rustup_home}")
        toolchains_dir = os.path.join(rustup_home, "toolchains")
        if os.path.exists(toolchains_dir):
            for toolchain in os.listdir(toolchains_dir):
                bin_dir = os.path.join(toolchains_dir, toolchain, "bin")
                if os.path.exists(os.path.join(bin_dir, "cargo.exe")):
                    print(f"Found Cargo in toolchain {toolchain}")
                    return bin_dir
    
    # If we still haven't found it, try using rustup show command
    try:
        result = subprocess.check_output(["rustup", "show"], text=True)
        for line in result.splitlines():
            if "Default host:" in line:
                toolchain = line.split(":")[-1].strip()
                bin_dir = os.path.join(rustup_home, "toolchains", toolchain, "bin")
                if os.path.exists(bin_dir):
                    return bin_dir
    except:
        pass
        
    return None

def main():
    print("Checking for Rust/Cargo installation...")
    
    # Check for existing installation in PATH
    try:
        subprocess.run(["cargo", "--version"], check=True, capture_output=True)
        print("Cargo is already in PATH and working correctly.")
        print("Run setup_environment.py to continue installation.")
        return True
    except:
        print("Cargo is not in PATH or not installed properly.")
    
    # Find Cargo installation
    cargo_path = check_cargo_installation()
    
    if not cargo_path:
        print("Could not find Cargo installation. Installing Rust...")
        
        # Download and run rustup-init
        try:
            # Create temp directory
            temp_dir = os.path.expanduser("~/rustup_temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Download rustup-init
            rustup_init = os.path.join(temp_dir, "rustup-init.exe")
            print("Downloading rustup-init.exe...")
            
            # Use PowerShell to download file
            download_cmd = [
                "powershell", 
                "-Command", 
                f"(New-Object System.Net.WebClient).DownloadFile('https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe', '{rustup_init}')"
            ]
            subprocess.run(download_cmd, check=True)
            
            # Run rustup-init with default settings
            print("Installing Rust...")
            subprocess.run([rustup_init, "-y"], check=True)
            
            # Cargo should now be installed at ~/.cargo/bin
            cargo_path = os.path.expanduser("~/.cargo/bin")
            
        except Exception as e:
            print(f"Error installing Rust: {str(e)}")
            print("Please install Rust manually from https://rustup.rs/")
            return False
    
    if cargo_path:
        print(f"Found Cargo at {cargo_path}")
        
        # Check if we're running as admin
        if not is_admin():
            print("Not running as admin. Will add Cargo to user PATH.")
        
        # Add to PATH
        if add_to_system_path(cargo_path):
            print("\nCargo has been added to your PATH.")
            print("Important: You need to RESTART your command prompt for the PATH changes to take effect.")
            print("\nAfter restarting your command prompt, run:")
            print("python setup_environment.py")
            return True
    
    print("\nFailed to set up Cargo in PATH.")
    print("Please manually add the Rust bin directory to your PATH and restart your command prompt.")
    print("Alternatively, use the setup_environment_fixed.py script with Pydantic v1 which doesn't require Rust.")
    return False

if __name__ == "__main__":
    main()