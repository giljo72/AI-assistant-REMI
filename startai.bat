@echo off
title AI Assistant - Comprehensive Startup
color 0A

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
    echo ERROR: Virtual environment not found
    echo Please run setup_environment.py first
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
python start_assistant.py

REM If the script exits abnormally, show error
if errorlevel 1 (
    echo.
    echo ================================================
    echo ERROR: Startup failed. Check the logs for details.
    echo ================================================
    pause
)