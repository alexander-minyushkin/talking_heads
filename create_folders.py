#!/usr/bin/env python3
"""Script to create the required folder structure for the AI-Agent testing utility."""

import os
import sys

def create_folders():
    """Create the required folder structure."""
    folders = [
        "agent",
        "human-simulation",
        "data",
        "logs"
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")
    
    # Create __init__.py files to make them Python packages
    for folder in ["agent", "human-simulation"]:
        init_file = os.path.join(folder, "__init__.py")
        with open(init_file, "w") as f:
            f.write("# Package initialization\n")
        print(f"Created: {init_file}")
    
    return True

if __name__ == "__main__":
    try:
        create_folders()
        print("Folder structure created successfully!")
    except Exception as e:
        print(f"Error creating folders: {e}")
        sys.exit(1)