# Task Completion Guidelines

When a task is completed, the following steps should be taken to ensure code quality, functionality, and proper integration:

1.  **Code Review:** Ensure the changes adhere to the established `code_style_and_conventions.md` (e.g., naming, formatting, commenting).

2.  **Local Testing:**
    *   **Unit/Integration Tests:** If new tests were added or existing ones modified, run them using `pytest` (if implemented).
    *   **Manual Testing:** Thoroughly test the affected functionality by running the application components:
        *   `run_host_services.bat`: To test the full application flow (web server, file watcher, system tray).
        *   `run_config_editor.bat`: If configuration changes were made, verify the GUI editor's functionality.
        *   `start_server.bat`: For testing web-related changes in isolation.

3.  **Data Verification:** If data processing logic was changed (e.g., in `upload_script.py`):
    *   Place sample CSV files in `申し込みデータ`.
    *   Verify that `data/processed_bookings.csv` is updated correctly.
    *   Check that processed files are moved to `処理済み`.
    *   Confirm that the web interface (`http://127.0.0.1:5000/`) displays the updated data accurately.

4.  **Linting and Formatting (Suggested):**
    *   Run `flake8 .` to check for style guide violations and potential errors.
    *   Run `black .` to automatically format the code for consistency.

5.  **Commit Changes:**
    *   Stage all relevant changes using `git add .` or `git add <file>`.
    *   Write a clear, concise, and descriptive commit message that explains *why* the changes were made, not just *what* was changed.
    *   Commit the changes using `git commit -m "Your descriptive commit message"`.

6.  **Documentation Update:** If the changes introduce new features, modify existing functionality, or alter the setup/usage, update `README.md` or any other relevant documentation accordingly.

7.  **Communicate:** Inform relevant team members about the completed task and any significant changes or considerations.
