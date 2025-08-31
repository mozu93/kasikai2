@echo off
:: Switch codepage to UTF-8 to prevent issues
chcp 65001 > nul

:: Run the host application in the background without a console window
start "kasikai Host" pythonw.exe host_app.py