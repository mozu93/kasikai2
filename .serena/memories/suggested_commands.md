# Suggested Commands for Project Development

This document outlines essential commands for setting up, running, and developing the 'kasikai' meeting room booking system.

## Setup and Installation
*   **Initial Setup:**
    ```bash
    setup.bat
    ```
    This command creates necessary directories (`申し込みデータ`, `処理済み`, `data`) and installs all required Python dependencies from `requirements.txt` using `pip`.

## Running the Application
*   **Start Host Services (Background):**
    ```bash
    run_host_services.bat
    ```
    Launches the main application (`host_app.py`) in the background, which manages the web server and file watcher. A system tray icon will appear.

*   **Run Configuration Editor (GUI):**
    ```bash
    run_config_editor.bat
    ```
    Opens a graphical user interface (`config_editor.py`) to easily modify `config.json` settings, such as meeting room names and display fields.

*   **Start Web Server (Foreground/Development):**
    ```bash
    start_server.bat
    ```
    Starts only the Flask web server (`app.py`) in the foreground. Useful for development and debugging the web interface. Access via `http://127.0.0.1:5000/`.

## Data Management
*   **Update Booking Data:** Place new or updated CSV files into the `申し込みデータ` folder. The system will automatically process them within approximately 5 seconds.

## Network Access
*   **Check Local IP Address:**
    ```bash
    ipconfig
    ```
    Use this command in Command Prompt to find your PC's IPv4 address, which can be used by other devices on the same network to access the web interface (e.g., `http://<your_ip_address>:5000/`).

*   **Firewall Configuration:** Manual configuration of Windows Firewall may be required to allow incoming connections on port `5000` for access from other PCs.

## Development Commands (Suggested)
While no explicit linting, formatting, or testing commands are provided in the project, the following standard Python tools are highly recommended for maintaining code quality and ensuring correctness:

*   **Linting (e.g., Flake8):**
    ```bash
    pip install flake8
    flake8 .
    ```
    Checks Python code against style conventions (PEP 8) and identifies potential errors.

*   **Formatting (e.g., Black):**
    ```bash
    pip install black
    black .
    ```
    Automatically formats Python code to adhere to a consistent style, reducing style-related conflicts.

*   **Testing (e.g., Pytest):**
    ```bash
    pip install pytest
    pytest
    ```
    If unit tests are implemented (currently none are provided), `pytest` is a popular framework for running them. You would typically create a `tests/` directory and write test files (e.g., `test_app.py`, `test_upload_script.py`).

## Git Commands
*   **Check Status:**
    ```bash
    git status
    ```
    Shows the status of your working tree.

*   **View Changes:**
    ```bash
    git diff
    ```
    Shows changes between commits, commit and working tree, etc.

*   **Add Changes for Commit:**
    ```bash
    git add <file_name>
    git add .
    ```
    Stages changes for the next commit.

*   **Commit Changes:**
    ```bash
    git commit -m "Your commit message"
    ```
    Records changes to the repository.
