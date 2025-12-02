## xcode-optimise

**xcode-optimise** is a small command‑line tool that provides utilities for working with Xcode projects, with a focus on detecting projects and inspecting their localization settings.

It can:

-   **Detect** whether a directory contains an Xcode project or workspace
-   **Locate** the nearest `.xcodeproj` bundle
-   **Read** the project's `project.pbxproj`
-   **Report** the development region (default language)
-   **List** all known localization languages configured in the project

---

## Installation

This project is configured with a `pyproject.toml` and is intended to be installed as a Python package.

-   **Using uv (recommended during development)**:

```bash
cd /path/to/xcode-optimise
uv run xcode-optimise --help
```

`uv run` will create/manage an isolated environment, install the project and its dependencies (such as `babel`), and then run the CLI entry point.

-   **Editable install with pip** (if you prefer):

```bash
cd /path/to/xcode-optimise
python -m pip install -e .
```

After installation, the `xcode-optimise` command will be available in your environment.

---

## Command‑line usage

The main entry point is the `xcode-optimise` script, which is backed by `xcode_optimise.cli:main`.

### Basic help

```bash
xcode-optimise --help
```

Output (simplified):

-   **Positional argument**:
    -   `directory` (optional): directory path to check. Defaults to the current working directory.
-   **Options**:
    -   `--list-languages`: list localization languages for the Xcode project.

### Detect whether a directory contains an Xcode project

To check if the current directory (or any of its subdirectories) contains an Xcode project (`.xcodeproj`) or workspace (`.xcworkspace`):

```bash
xcode-optimise
```

You can also provide an explicit directory:

```bash
xcode-optimise /path/to/your/ios/project
```

The tool will print:

-   `Xcode project detected` if it finds a `.xcodeproj` or `.xcworkspace`
-   `Not an Xcode project` otherwise

Under the hood this uses `xcode_optimise.detection.is_xcode_project`, which:

-   Checks the immediate directory for `.xcodeproj` / `.xcworkspace` bundles
-   Falls back to recursively searching subdirectories with `os.walk`

### List localization languages for a project

To inspect localization settings for an Xcode project, use `--list-languages`:

```bash
xcode-optimise --list-languages
```

or for a specific directory:

```bash
xcode-optimise /path/to/your/ios/project --list-languages
```

The tool will:

-   Find the nearest `.xcodeproj` bundle under the given directory
-   Read its `project.pbxproj`
-   Determine the development region (default language)
-   Parse and list all `knownRegions`

Example output:

```text
Default Language: English (en)

Available Languages:
English (en)
French (fr)
German (de)
```

If the `developmentRegion` is missing but there are known regions, the tool falls back to using the first known region as the default. If there are no known regions and no development region, it will report an unknown default language.

In error cases (for example, when no `.xcodeproj` can be found, or the `project.pbxproj` file cannot be read), messages are written to stderr and the command exits with a non‑zero status.

---

## Python API

In addition to the CLI, you can import and use the underlying utilities directly from Python code.

### `xcode_optimise.detection`

-   **`is_xcode_project(directory_path: str) -> bool`**  
    Returns `True` if the directory (or any subdirectory) contains a `.xcodeproj` or `.xcworkspace`, otherwise `False`.

-   **`find_xcode_project_path(directory_path: str) -> pathlib.Path | None`**  
    Returns the `Path` to the first `.xcodeproj` bundle found in the directory or its subdirectories, or `None` if not found.

### `xcode_optimise.localization`

-   **`get_development_region(project_path: pathlib.Path) -> tuple[str | None, str]`**  
    Reads `project.pbxproj` from the given `.xcodeproj` path and returns `(language_name, language_code)` for the `developmentRegion`.

    -   On success, returns a language name (e.g. `"English"`) and code (e.g. `"en"`).
    -   If the code is missing or cannot be parsed, returns `(None, "")` or `(None, <raw_code>)`.

-   **`list_localization_languages(project_path: pathlib.Path) -> list[tuple[str | None, str]]`**  
    Parses the `knownRegions` from `project.pbxproj` and returns a list of `(language_name, language_code)` pairs.  
    Uses `babel.Locale` to convert language codes to human‑readable names, falling back to `None` when parsing fails.

---

## Development

### Requirements

-   Python `>= 3.14`
-   `uv` (for convenient dependency management), or a standard Python + `pip` setup

### Set up a dev environment with uv

```bash
cd /path/to/xcode-optimise
uv run python -m pip install -e .[dev]
```

You can then run the linters and type‑checker:

```bash
uv run ruff check .
uv run mypy main.py
```

### Project structure

-   `main.py` – thin wrapper to invoke `xcode_optimise.cli.main()` for backward compatibility.
-   `src/xcode_optimise/cli.py` – CLI implementation and argument parsing.
-   `src/xcode_optimise/detection.py` – utilities for detecting and locating Xcode projects.
-   `src/xcode_optimise/localization.py` – utilities for reading development region and localization languages from `project.pbxproj`.
-   `src/xcode_optimise/py.typed` – marker file indicating that the package is fully type‑checked.

---

## License

This repository is licensed under the [MIT License](LICENSE).
