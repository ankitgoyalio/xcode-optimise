"""Language and localization utilities for Xcode projects."""

import re
from pathlib import Path

from babel import Locale


def _get_language_name(code: str) -> str | None:
    """
    Convert a language code to a human-readable language name using babel.Locale.

    Args:
        code: Language code (e.g., 'en', 'fr', 'en-US')

    Returns:
        Language name (e.g., 'English', 'French') or None if parsing fails
    """
    try:
        locale = Locale.parse(code, sep="-")
        return locale.get_display_name("en")
    except (ValueError, AttributeError):
        try:
            base_code = code.split("-")[0].split("_")[0]
            locale = Locale.parse(base_code)
            return locale.get_display_name("en")
        except (ValueError, AttributeError):
            return None


def get_development_region(project_path: Path) -> tuple[str | None, str]:
    """
    Extract the development region (default language) from an Xcode project's project.pbxproj file.

    Args:
        project_path: Path to the .xcodeproj bundle

    Returns:
        Tuple containing (language_name, language_code) for the development region
        (e.g., ('English', 'en')). If not found or parsing fails, returns (None, '') or (None, <code>).

    Raises:
        FileNotFoundError: If project.pbxproj file is not found
        OSError: If project.pbxproj file cannot be read
    """
    pbxproj_path = project_path / "project.pbxproj"

    if not pbxproj_path.exists():
        raise FileNotFoundError(f"project.pbxproj not found in {project_path}")

    try:
        with open(pbxproj_path, encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        raise OSError(f"Failed to read project.pbxproj: {e}") from e

    pattern = r"developmentRegion\s*=\s*([^;]+);"
    match = re.search(pattern, content)

    if not match:
        return (None, "")

    code = match.group(1).strip().strip("'\"")
    if not code:
        return (None, "")

    language_name = _get_language_name(code)
    return (language_name, code)


def list_localization_languages(project_path: Path) -> list[tuple[str | None, str]]:
    """
    Extract all localization languages from an Xcode project's project.pbxproj file.

    Args:
        project_path: Path to the .xcodeproj bundle

    Returns:
        List of tuples containing (language_name, language_code) pairs
        (e.g., [('English', 'en'), ('French', 'fr'), ('German', 'de')])

    Raises:
        FileNotFoundError: If project.pbxproj file is not found
        OSError: If project.pbxproj file cannot be read
    """
    pbxproj_path = project_path / "project.pbxproj"

    if not pbxproj_path.exists():
        raise FileNotFoundError(f"project.pbxproj not found in {project_path}")

    try:
        with open(pbxproj_path, encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        raise OSError(f"Failed to read project.pbxproj: {e}") from e

    pattern = r"knownRegions\s*=\s*\((.*?)\);"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return []

    regions_content = match.group(1)
    language_codes: list[str] = []
    for line in regions_content.split("\n"):
        line = line.strip().rstrip(",")
        if line and not line.startswith("//"):
            lang = line.strip("'\"")
            if lang:
                language_codes.append(lang)

    languages = []
    for code in language_codes:
        language_name = _get_language_name(code)
        languages.append((language_name, code))

    return languages
