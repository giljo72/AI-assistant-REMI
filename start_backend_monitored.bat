@echo off
title AI Assistant - Backend (Monitored)
cd /d "%~dp0backend"

:check_flag
if not exist "..\.services_running" (
    echo.
    echo Services shutdown detected. Stopping backend...
    exit
)

echo Starting Backend API Server...
echo.

REM Activate virtual environment
call ..\venv_nemo\Scripts\activate

REM Create a Python script to handle the monitoring
echo import subprocess > monitor_backend.py
echo import sys >> monitor_backend.py
echo import time >> monitor_backend.py
echo import os >> monitor_backend.py
echo. >> monitor_backend.py
echo proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app', '--reload', '--host', '10.1.0.224', '--port', '8000']) >> monitor_backend.py
echo while proc.poll() is None and os.path.exists('../.services_running'): >> monitor_backend.py
echo     time.sleep(1) >> monitor_backend.py
echo if proc.poll() is None: >> monitor_backend.py
echo     proc.terminate() >> monitor_backend.py

REM Run the monitoring script
python monitor_backend.py

REM Clean up
del monitor_backend.py

REM If we get here, either the server crashed or shutdown was requested
if exist "..\.services_running" (
    echo.
    echo Backend server stopped unexpectedly!
    timeout /t 5 >nul
    goto :check_flag
) else (
    echo Backend shutdown complete.
    exit
)