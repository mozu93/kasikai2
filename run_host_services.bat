@echo off
chcp 65001 > nul

:: Run the host application in the background without a console window
start "kasikai Host" pythonw.exe host_app.py
