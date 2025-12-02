import argparse
import os
import re
import sys
from pathlib import Path

try:
    from babel import Locale
except ImportError:
    Locale = None


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
        if item.is_dir() and item.suffix == '.xcodeproj':
            return item

    # If not found, search recursively
    for root, dirs, files in os.walk(directory_path):
        for dir_name in dirs:
            if dir_name.endswith('.xcodeproj'):
                return Path(root) / dir_name

    return None


def list_localization_languages(project_path: Path) -> list[tuple[str, str]]:
    """
    Extract all localization languages from an Xcode project's project.pbxproj file.

    Args:
        project_path: Path to the .xcodeproj bundle

    Returns:
        List of tuples containing (language_name, language_code) pairs
        (e.g., [('English', 'en'), ('French', 'fr'), ('German', 'de')])

    Raises:
        FileNotFoundError: If project.pbxproj file is not found
        IOError: If project.pbxproj file cannot be read
    """
    pbxproj_path = project_path / 'project.pbxproj'

    if not pbxproj_path.exists():
        raise FileNotFoundError(f"project.pbxproj not found in {project_path}")

    try:
        with open(pbxproj_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except IOError as e:
        raise IOError(f"Failed to read project.pbxproj: {e}")

    pattern = r'knownRegions\s*=\s*\((.*?)\);'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return []

    regions_content = match.group(1)
    language_codes = []
    for line in regions_content.split('\n'):
        line = line.strip().rstrip(',')
        if line and not line.startswith('//'):
            lang = line.strip("'\"")
            if lang:
                language_codes.append(lang)

    languages = []
    for code in language_codes:
        language_name = None
        if Locale is not None:
            try:
                try:
                    locale = Locale.parse(code, sep='-')
                except (ValueError, AttributeError):
                    locale = Locale.parse(code, sep='_')
                language_name = locale.get_display_name('en')
            except (ValueError, AttributeError):
                try:
                    base_code = code.split('-')[0].split('_')[0]
                    locale = Locale.parse(base_code)
                    language_name = locale.get_display_name('en')
                except (ValueError, AttributeError):
                    pass

        if language_name is None:
            language_name = code

        languages.append((language_name, code))

    return languages


def main():
    parser = argparse.ArgumentParser(
        description='Xcode project utilities'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default=os.getcwd(),
        help='Directory path to check (defaults to current working directory)'
    )
    parser.add_argument(
        '--list-languages',
        action='store_true',
        help='List all localization languages supported in the Xcode project'
    )

    args = parser.parse_args()

    if args.list_languages:
        project_path = find_xcode_project_path(args.directory)
        if project_path is None:
            print(
                f"Error: No .xcodeproj found in {args.directory}", file=sys.stderr)
            sys.exit(1)

        try:
            languages = list_localization_languages(project_path)
            if languages:
                for language_name, language_code in languages:
                    print(f"{language_name} ({language_code})")
            else:
                print("No localization languages found in project", file=sys.stderr)
        except (FileNotFoundError, IOError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if is_xcode_project(args.directory):
            print("Xcode project detected")
        else:
            print("Not an Xcode project")


if __name__ == "__main__":
    main()
