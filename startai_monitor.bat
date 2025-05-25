@echo off
title AI Assistant - Startup Launcher
color 0A

echo ================================================
echo AI Assistant - Startup Launcher
echo ================================================
echo.
echo Launching the AI Assistant service manager...
echo.

REM Check if venv_nemo exists
if not exist "%~dp0venv_nemo\Scripts\python.exe" (
    echo ERROR: Virtual environment 'venv_nemo' not found
    echo Please create it first with: python -m venv venv_nemo
    pause
    exit /b 1
)

REM Launch the GUI startup manager
cd /d "%~dp0StartAgent"
"%~dp0venv_nemo\Scripts\python.exe" launcher.py

REM If launcher exits, clean up
if exist "%~dp0.services_running" del "%~dp0.services_running"

echo.
echo Launcher closed.
pause