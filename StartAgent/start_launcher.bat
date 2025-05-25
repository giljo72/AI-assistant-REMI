@echo off
title AI Assistant Launcher
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the launcher
echo Starting AI Assistant Launcher...
python launcher.py

REM If launcher crashes, show error
if errorlevel 1 (
    echo.
    echo ERROR: Launcher failed to start
    pause
)