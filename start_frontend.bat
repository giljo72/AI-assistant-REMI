@echo off
title AI Assistant - Frontend Development Server
color 0B
echo ================================================
echo AI Assistant Frontend Development Server
echo ================================================
echo.

REM Change to the frontend directory
cd /d "%~dp0frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo node_modules not found. Installing dependencies...
    echo.
    npm install
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting Vite development server...
echo.
echo Frontend will be available at: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

REM Run the development server
npm run dev

REM Keep window open if server crashes
if errorlevel 1 (
    echo.
    echo ================================================
    echo ERROR: Frontend server crashed!
    echo Check the error messages above.
    echo ================================================
    pause
)