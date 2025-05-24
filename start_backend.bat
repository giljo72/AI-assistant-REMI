@echo off
title AI Assistant - Backend Server
color 0E
echo ================================================
echo AI Assistant Backend Server
echo ================================================
echo.

REM Change to the backend directory
cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist "..\venv_nemo\Scripts\python.exe" (
    echo ERROR: Virtual environment not found at ..\venv_nemo
    echo Please create it first with: python -m venv venv_nemo
    pause
    exit /b 1
)

echo Starting FastAPI backend server...
echo.
echo Server will be available at: http://localhost:8000
echo API Documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

REM Activate virtual environment and run the server
call ..\venv_nemo\Scripts\activate
python -m uvicorn app.main:app --reload --host 10.1.0.224 --port 8000

REM Keep window open if server crashes
if errorlevel 1 (
    echo.
    echo ================================================
    echo ERROR: Backend server crashed!
    echo Check the error messages above.
    echo ================================================
    pause
)