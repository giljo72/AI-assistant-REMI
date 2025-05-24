@echo off
title AI Assistant - Debug Mode Launcher
color 0A

echo ================================================
echo AI Assistant - Debug Mode (Separate Windows)
echo ================================================
echo.
echo This will start each service in its own window:
echo - PostgreSQL (if not running)
echo - Ollama (if not running)
echo - Backend API Server
echo - Frontend Development Server
echo.
pause

REM Check if we're in the right directory
if not exist "backend" (
    echo ERROR: Cannot find backend directory
    echo Make sure you're running this from F:\Assistant
    pause
    exit /b 1
)

REM Start PostgreSQL if needed
echo Checking PostgreSQL...
sc query postgresql-x64-17 | find "RUNNING" >nul
if errorlevel 1 (
    echo Starting PostgreSQL...
    net start postgresql-x64-17 2>nul
    if errorlevel 1 (
        net start postgresql 2>nul
    )
    timeout /t 3 >nul
)

REM Start Ollama in a new window if not running
echo.
echo Checking Ollama...
tasklist | find "ollama.exe" >nul
if errorlevel 1 (
    echo Starting Ollama in a new window...
    start "Ollama Service" cmd /k "ollama serve"
    timeout /t 5 >nul
)

REM Start Backend in a new window
echo.
echo Starting Backend API Server in a new window...
start "Backend API" cmd /c "start_backend.bat"
timeout /t 5 >nul

REM Start Frontend in a new window
echo.
echo Starting Frontend Development Server in a new window...
start "Frontend Dev" cmd /c "start_frontend.bat"
timeout /t 3 >nul

REM Open browser after a delay
echo.
echo Waiting for services to fully start...
timeout /t 5 >nul

echo.
echo Opening application in browser...
start http://localhost:5173

echo.
echo ================================================
echo All services started in separate windows!
echo.
echo Backend API: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
echo To stop all services:
echo - Close each window (Ctrl+C then Y)
echo - Or run: stopai.bat
echo ================================================
echo.
echo This window will close in 10 seconds...
timeout /t 10 >nul