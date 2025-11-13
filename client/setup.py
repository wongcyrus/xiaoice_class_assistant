#!/usr/bin/env python3
import subprocess
import sys
import os

def setup_environment():
    """Setup virtual environment and install dependencies"""
    
    # Create virtual environment
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Determine activation script path based on OS
    if os.name == 'nt':  # Windows
        activate_script = os.path.join("venv", "Scripts", "activate")
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:  # Unix/Linux/macOS
        activate_script = os.path.join("venv", "bin", "activate")
        pip_path = os.path.join("venv", "bin", "pip")
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    
    print(f"\nSetup complete!")
    print(f"To activate the environment:")
    if os.name == 'nt':
        print(f"  .\\venv\\Scripts\\activate")
    else:
        print(f"  source venv/bin/activate")
    print(f"To run the application:")
    print(f"  python window_monitor.py")

if __name__ == "__main__":
    setup_environment()
