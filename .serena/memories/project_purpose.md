# Project Purpose

This project is a local meeting room booking system designed to display booking statuses via a web browser.

## Key Features:
*   **Local Data Management:** All booking data is stored and processed locally on the PC, without reliance on external services like Google Sheets.
*   **Automated Data Processing:** Monitors a designated folder (`申し込みデータ`) for new or updated CSV files. These files are automatically processed, validated, de-duplicated, and used to update the local booking database (`data/processed_bookings.csv`).
*   **Web-based Calendar View:** Provides a web interface (accessible via `http://127.0.0.1:5000/`) to view meeting room availability in a calendar format (monthly, weekly, daily).
*   **Configurable:** Allows users to configure meeting room names, display order, and details shown in booking pop-ups via a dedicated GUI editor.
*   **Background Operation:** Runs as a background service with a system tray icon, ensuring continuous operation even when the console window is closed.
*   **Network Accessibility:** The web interface can be accessed from other devices on the same local network after appropriate firewall configuration.
