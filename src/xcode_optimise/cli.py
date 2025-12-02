"""Command-line interface for Xcode project utilities."""

import argparse
import os
import sys

from xcode_optimise.detection import find_xcode_project_path, is_xcode_project
from xcode_optimise.localization import (
    get_development_region,
    list_localization_languages,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Xcode project utilities")
    parser.add_argument(
        "directory",
        nargs="?",
        default=os.getcwd(),
        help="Directory path to check (defaults to current working directory)",
    )
    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List all localization languages supported in the Xcode project",
    )

    args = parser.parse_args()

    if args.list_languages:
        project_path = find_xcode_project_path(args.directory)
        if project_path is None:
            print(
                f"Error: No .xcodeproj found in {args.directory}",
                file=sys.stderr,
            )
            sys.exit(1)

        try:
            # Get the default development region
            default_name, default_code = get_development_region(project_path)

            # Get all known regions
            languages = list_localization_languages(project_path)

            # Print the default language on the first line
            if default_code:
                if default_name:
                    print(f"\nDefault Language: {default_name} ({default_code})")
                else:
                    print(f"\nDefault Language: (unknown) ({default_code})")
            elif languages:
                # Fallback: use first known region as default if developmentRegion is missing
                fallback_name, fallback_code = languages[0]
                if fallback_name:
                    print(
                        f"\nDefault Language: {fallback_name} ({fallback_code})",
                    )
                else:
                    print(f"\nDefault Language: (unknown) ({fallback_code})")
            else:
                print("\nDefault Language: (unknown) ()")

            # Print all known regions on subsequent lines
            if languages:
                print("\nAvailable Languages:")
                for language_name, language_code in languages:
                    print(f"{language_name} ({language_code})")
            elif not default_code:
                print(
                    "No localization languages found in project",
                    file=sys.stderr,
                )
        except (OSError, FileNotFoundError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if is_xcode_project(args.directory):
            print("Xcode project detected")
        else:
            print("Not an Xcode project")


