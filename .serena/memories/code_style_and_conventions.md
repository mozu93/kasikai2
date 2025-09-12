# Code Style and Conventions

## Language
*   **Comments and Docstrings:** Primarily in Japanese, providing detailed explanations of logic, functions, and sections.
*   **Variable and Function Names:** Generally in English, using `snake_case` for readability.

## Formatting
*   **Indentation:** Consistent use of 4 spaces for indentation.
*   **Line Endings:** Windows-style line endings (CRLF) are expected given the `.bat` files and Windows environment.

## Modularity
*   The project is well-structured into distinct Python files, each responsible for a specific functionality:
    *   `app.py`: Flask web server and API.
    *   `host_app.py`: Main application orchestrator, manages background services and system tray icon.
    *   `upload_script.py`: Handles file system monitoring and CSV data processing.
    *   `config_editor.py`: Provides a GUI for configuration management.

## Error Handling
*   Extensive use of `try-except` blocks for robust error handling, particularly around file operations, JSON parsing, and external library calls.
*   User-friendly error messages are provided via `messagebox` in the GUI editor and `print` statements in console applications.

## Configuration
*   Configuration settings are stored in `config.json`.
*   Default configurations are provided within the code (e.g., in `config_editor.py` and `upload_script.py`) if `config.json` is not found or is invalid.

## File Paths
*   `os.path.join` is consistently used for constructing file paths, ensuring cross-platform compatibility.

## Data Handling
*   CSV files are read with `encoding='utf-8-sig'` to correctly handle Byte Order Mark (BOM) often present in CSVs generated on Windows.
*   `pandas` DataFrames are used for efficient data manipulation.

## Naming Conventions
*   **Constants/Global Variables:** Defined in `UPPERCASE_WITH_UNDERSCORES` (e.g., `DATA_DIR`, `CONFIG_FILE`).
*   **Functions and Methods:** `snake_case` (e.g., `load_config`, `run_web_server`).
*   **Classes:** `PascalCase` (e.g., `ConfigEditorApp`, `DebounceEventHandler`).

## Imports
*   Standard Python library imports typically come first, followed by third-party library imports.
*   Relative imports are handled using `sys.path.append` for modules within the project directory.
