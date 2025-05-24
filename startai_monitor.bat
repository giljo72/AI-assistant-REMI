@echo off
title AI Assistant - Monitored Debug Mode
color 0A

echo ================================================
echo AI Assistant - Monitored Debug Mode
echo ================================================
echo.
echo This will start:
echo 1. Debug Monitor (color-coded status window)
echo 2. Backend API Server
echo 3. Frontend Development Server
echo.
echo To stop all services cleanly:
echo - Press Ctrl+C in the Monitor window
echo - Or run: stopai.bat
echo.
pause

REM Create a shutdown flag file (will be deleted when services stop cleanly)
echo > "%~dp0.services_running"

REM Start Debug Monitor first (this will be our main control window)
start "AI Assistant Monitor" /MIN cmd /c "cd /d "%~dp0" && venv_nemo\Scripts\python.exe debug_monitor.py"
timeout /t 2 >nul

REM Check PostgreSQL
sc query postgresql-x64-17 | find "RUNNING" >nul
if errorlevel 1 (
    echo Starting PostgreSQL...
    net start postgresql-x64-17 2>nul
    if errorlevel 1 (
        net start postgresql 2>nul
    )
    timeout /t 3 >nul
)

REM Check Ollama
tasklist | find "ollama.exe" >nul
if errorlevel 1 (
    echo Starting Ollama...
    start "Ollama Service" /MIN cmd /c "ollama serve"
    timeout /t 5 >nul
)

REM Start Backend with graceful shutdown
echo Starting Backend...
start "Backend API" /MIN cmd /c "cd /d "%~dp0" && if exist .services_running (start_backend_monitored.bat) else (echo Services stopped && exit)"
timeout /t 3 >nul

REM Start Frontend with graceful shutdown
echo Starting Frontend...
start "Frontend Dev" /MIN cmd /c "cd /d "%~dp0" && if exist .services_running (start_frontend_monitored.bat) else (echo Services stopped && exit)"
timeout /t 3 >nul

REM Open browser
echo.
echo Opening browser...
timeout /t 3 >nul
start http://localhost:5173

echo.
echo ================================================
echo All services started!
echo.
echo Monitor Window: Shows real-time status
echo Backend API: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
echo To stop: Press Ctrl+C in the Monitor window
echo ================================================
echo.
pause