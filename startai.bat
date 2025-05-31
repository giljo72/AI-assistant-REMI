@echo off
title AI Assistant - Comprehensive Startup
color 0A

REM Check for debug mode
if "%1"=="debug" goto :debug_mode
if "%1"=="monitor" goto :monitor_mode

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ================================================
    echo Requesting Administrator privileges...
    echo ================================================
    echo.
    
    REM Create a temporary VBS script to run this batch file as admin
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /b
)

echo ================================================
echo AI Assistant - Comprehensive Startup (Admin Mode)
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv_nemo\Scripts\python.exe" (
    echo ERROR: Virtual environment 'venv_nemo' not found
    echo.
    echo Current directory: %CD%
    echo Looking for: %CD%\venv_nemo\Scripts\python.exe
    echo.
    echo Make sure you're running this script from the F:\Assistant directory
    echo or that venv_nemo exists in the current directory.
    echo.
    echo If venv_nemo doesn't exist, you need to create it:
    echo   python -m venv venv_nemo
    echo   venv_nemo\Scripts\activate
    echo   pip install -r backend\requirements.txt
    pause
    exit /b 1
)

REM Run the comprehensive startup script
echo Launching AI Assistant services with enhanced monitoring...
echo.
echo Starting services:
echo - PostgreSQL database
echo - Ollama service
echo - Docker Desktop (if needed)
echo - NVIDIA NIM containers
echo - Backend API server
echo - Frontend development server
echo.
venv_nemo\Scripts\python.exe start_assistant.py

REM If the script exits abnormally, show error
if errorlevel 1 (
    echo.
    echo ================================================
    echo ERROR: Startup failed. Check the logs for details.
    echo ================================================
    pause
)
exit /b

:debug_mode
echo ================================================
echo AI Assistant - Debug Mode
echo ================================================
echo Starting services in separate windows for debugging...
echo.
call startai_debug.bat
exit /b

:monitor_mode
echo ================================================
echo AI Assistant - Monitor Mode
echo ================================================
echo Starting services with debug monitor...
echo.
call startai_monitor.bat
exit /b