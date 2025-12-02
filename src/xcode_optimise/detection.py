"""Xcode project detection utilities."""

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
        if item.is_dir() and item.suffix in [".xcodeproj", ".xcworkspace"]:
            return True

    # If not found, search recursively
    for _root, dirs, _files in os.walk(directory_path):
        for dir_name in dirs:
            if dir_name.endswith((".xcodeproj", ".xcworkspace")):
                return True

    return False


def find_xcode_project_path(directory_path: str) -> Path | None:
    """
    Find and return the path to the .xcodeproj bundle in the given directory.

    First checks the immediate directory for .xcodeproj bundles.
    If not found, recursively searches subdirectories.

    Args:
        directory_path: Path to the directory to search

    Returns:
        Path to the .xcodeproj bundle if found, None otherwise
    """
    path = Path(directory_path)

    if not path.exists() or not path.is_dir():
        return None

    # Check immediate directory first
    for item in path.iterdir():
        if item.is_dir() and item.suffix == ".xcodeproj":
            return item

    # If not found, search recursively
    for root, dirs, _files in os.walk(directory_path):
        for dir_name in dirs:
            if dir_name.endswith(".xcodeproj"):
                return Path(root) / dir_name

    return None


