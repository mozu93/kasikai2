# Tech Stack

This project is built using Python 3 and leverages several key libraries:

*   **Python 3**: The core programming language.
*   **Flask**: A micro web framework used for the web server (`app.py`) that serves the booking calendar and API endpoints.
*   **Flask-CORS**: A Flask extension for handling Cross-Origin Resource Sharing (CORS), enabling web browsers to make requests to the Flask application from different origins.
*   **Pandas**: A powerful data manipulation and analysis library. It is extensively used in `upload_script.py` for reading, processing (e.g., filtering cancellations, de-duplication), and writing CSV files.
*   **Watchdog**: A Python library to monitor file system events. It is used in `upload_script.py` to detect changes (new files, modifications) in the `申し込みデータ` directory, triggering automated data processing.
*   **Pystray**: A library for creating system tray icons. It is used in `host_app.py` to provide a background application with a system tray presence and menu options (e.g., to exit the application).
*   **Pillow (PIL Fork)**: A Python Imaging Library fork, used in `host_app.py` for creating the system tray icon image dynamically.
*   **Tkinter**: Python's standard GUI (Graphical User Interface) toolkit, used in `config_editor.py` to provide a user-friendly interface for editing the `config.json` file.
*   **JSON**: Used for configuration management (`config.json`).
