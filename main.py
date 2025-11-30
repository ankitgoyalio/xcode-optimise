import argparse
import os
from pathlib import Path


def is_xcode_project(directory_path: str) -> bool:
    """
    Check if a directory corresponds to an Xcode project.
    
    First checks the immediate directory for .xcodeproj or .xcworkspace bundles.
    If not found, recursively searches subdirectories.
    
    Args:
        directory_path: Path to the directory to check
        
    Returns:
        True if .xcodeproj or .xcworkspace is found, False otherwise
    """
    path = Path(directory_path)
    
    if not path.exists() or not path.is_dir():
        return False
    
    # Check immediate directory first
    for item in path.iterdir():
        if item.is_dir():
            if item.suffix == '.xcodeproj' or item.suffix == '.xcworkspace':
                return True
    
    # If not found, search recursively
    for root, dirs, files in os.walk(directory_path):
        for dir_name in dirs:
            if dir_name.endswith('.xcodeproj') or dir_name.endswith('.xcworkspace'):
                dir_path = Path(root) / dir_name
                if dir_path.is_dir():
                    return True
    
    return False


def main():
    parser = argparse.ArgumentParser(
        description='Check if a directory is an Xcode project'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default=os.getcwd(),
        help='Directory path to check (defaults to current working directory)'
    )
    
    args = parser.parse_args()
    
    if is_xcode_project(args.directory):
        print("Xcode project detected")
    else:
        print("Not an Xcode project")


if __name__ == "__main__":
    main()
