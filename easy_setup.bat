@echo off
setlocal enabledelayedexpansion

REM ===================================
REM   Meeting Room System Easy Setup
REM ===================================

echo.
echo ============================================
echo        Meeting Room System Easy Setup
echo.
echo  Double-click this file to complete
echo  all setup automatically!
echo ============================================
echo.

REM Check Python
echo Step 1: Checking environment...
echo    Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed.
    echo.
    echo Do you want to install Python automatically?
    echo    [1] Yes - Auto install Python 3.11
    echo    [2] No - Manual installation
    echo    [3] Exit
    echo.
    choice /c 123 /n /m "Please select (1,2,3): "

    if !errorlevel!==1 (
        echo.
        echo Opening Python download page...
        start "" "https://python.org/downloads/"
        echo Please install Python and run this file again.
        pause
        exit /b 1
    ) else if !errorlevel!==2 (
        echo.
        echo Please follow these steps:
        echo    1. Go to https://python.org
        echo    2. Download Python 3.11 or later
        echo    3. Check "Add Python to PATH" during install
        echo    4. Run this file again after installation
        echo.
        start "" "https://python.org/downloads/"
        pause
        exit /b 1
    ) else (
        echo Cancelled.
        pause
        exit /b 0
    )
) else (
    echo    OK: Python installed
)

REM Install libraries
echo.
echo Step 2: Installing required libraries...
echo    Installing packages...

python -m pip install --upgrade pip >nul 2>&1
if exist requirements.txt (
    python -m pip install -r requirements.txt >nul 2>&1
    if !errorlevel!==0 (
        echo    OK: Libraries installed
    ) else (
        echo    WARNING: Some libraries failed to install
        echo       Please check your network connection
    )
) else (
    echo    WARNING: requirements.txt not found
)

REM Create folders
echo.
echo Step 3: Creating required folders...
if not exist "data" (
    mkdir "data"
    echo    OK: data folder created
) else (
    echo    OK: data folder exists
)

if not exist "uploads" (
    mkdir "uploads"
    echo    OK: uploads folder created
) else (
    echo    OK: uploads folder exists
)

if not exist "processed" (
    mkdir "processed"
    echo    OK: processed folder created
) else (
    echo    OK: processed folder exists
)

REM Check config file
echo.
echo Step 4: Checking configuration...
if not exist "config.json" (
    if exist "config_distribution.json" (
        copy "config_distribution.json" "config.json" >nul
        echo    OK: Initial config created
    ) else (
        echo    WARNING: Config file not found
    )
) else (
    echo    OK: Config file exists
)

REM Setup configuration
echo.
echo Step 5: Initial configuration
echo.
echo Do you want to configure meeting rooms now?
echo    [1] Yes - Configure now (Recommended)
echo    [2] Later - Use sample settings
echo.
choice /c 12 /n /m "Please select (1,2): "

if !errorlevel!==1 (
    echo.
    echo Starting configuration editor...
    echo    Please set up meeting rooms in the window that opens
    echo.
    if exist "config_editor.pyw" (
        start "" "python" "config_editor.pyw"
        echo    Please press any key after completing setup...
        pause >nul
    ) else (
        echo    WARNING: Configuration editor not found
    )
) else (
    echo    OK: Using sample configuration
)

REM Start system
echo.
echo Step 6: Start system now?
echo    [1] Yes - Start now
echo    [2] No - Start manually later
echo.
choice /c 12 /n /m "Please select (1,2): "

if !errorlevel!==1 (
    echo.
    echo Starting system...
    echo.
    echo ============================================
    echo             Setup Complete!
    echo.
    echo  Browser will open automatically
    echo  URL: http://localhost:5003
    echo.
    echo  To stop the system:
    echo  Press Ctrl+C in this window
    echo ============================================
    echo.

    REM Open browser after 3 seconds
    start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5003"

    REM Start Python application
    python server_fixed.py

) else (
    echo.
    echo ============================================
    echo             Setup Complete!
    echo.
    echo  To start the system:
    echo  Double-click: start_server.bat
    echo.
    echo  To change settings:
    echo  Double-click: run_config_editor.bat
    echo ============================================
    echo.
)

echo Enjoy your Meeting Room System!
pause
exit /b 0