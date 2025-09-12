# Codebase Structure

The project directory `kasikai` has the following key files and directories:

```
C:\Users\taka\Documents\Gemini\kasikai\
├───.gitignore
├───app.py                  # Flask web server for displaying booking data and API endpoints.
├───config_editor.py        # GUI application for editing config.json.
├───config.json             # Configuration file for meeting rooms, CSV column mappings, and modal display fields.
├───host_app.py             # Main application, runs in background, manages web server and file watcher threads, provides system tray icon.
├───index.html              # Frontend HTML file for the web interface.
├───README.md               # Project overview, setup, and usage instructions (in Japanese).
├───requirements.txt        # Python dependencies required for the project.
├───run_config_editor.bat   # Batch script to launch config_editor.py.
├───run_host_services.bat   # Batch script to launch host_app.py (background service).
├───setup.bat               # Batch script for initial project setup (directory creation, dependency installation).
├───setup.py                # Python script executed by setup.bat for project initialization.
├───start_server.bat        # Batch script to launch app.py (web server) in foreground.
├───upload_script.py        # Monitors '申し込みデータ' folder, processes CSVs, and updates 'data/processed_bookings.csv'.
├───__pycache__\            # Python compiled bytecode cache.
├───.git\...                 # Git version control directory.
├───.serena\                # Serena-specific configuration and memories.
│   ├───.gitignore
│   ├───project.yml
│   ├───cache\...
│   └───memories\
├───data\                   # Contains processed booking data.
│   └───processed_bookings.csv # Consolidated and processed booking data.
├───処理済み\               # Directory where processed CSV files are moved after successful processing.
└───申し込みデータ\           # Directory where raw booking CSV files are placed for processing.
```

## Key Components and Their Roles:

*   **`app.py`**: The Flask application that serves the web interface (`index.html`) and provides API endpoints for booking data and configuration.
*   **`host_app.py`**: The central orchestrator. It runs as a background process, launches `app.py` and `upload_script.py` in separate threads, and manages a system tray icon for application control.
*   **`upload_script.py`**: A file system watcher that monitors the `申し込みデータ` directory. When new or updated CSV files are detected, it processes them (parsing, cleaning, de-duplicating) and updates `data/processed_bookings.csv`.
*   **`config_editor.py`**: A Tkinter-based GUI tool that allows users to easily modify the `config.json` file, which defines meeting room details, CSV column mappings, and fields to display in the booking pop-ups.
*   **`config.json`**: Stores all user-configurable settings for the application.
*   **`index.html`**: The frontend web page that displays the meeting room booking calendar.
*   **`data/processed_bookings.csv`**: The consolidated and cleaned booking data used by the web application.
*   **`申し込みデータ/`**: The input directory where users place raw CSV files containing booking information.
*   **`処理済み/`**: The output directory where CSV files are moved after they have been successfully processed by `upload_script.py`.
