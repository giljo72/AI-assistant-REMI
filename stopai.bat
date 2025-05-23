@echo off
title Stop AI Assistant - Full Stack
color 0C

echo ================================================
echo Stopping AI Assistant - Full Stack
echo ================================================
cd /d "F:\assistant"

:: Stop Docker containers (NIM services)
echo [1/5] Stopping NVIDIA NIM containers...
docker-compose down
if %errorlevel% equ 0 (
    echo     NIM containers stopped successfully!
) else (
    echo     Warning: Some containers may not have stopped cleanly
)

:: Stop Ollama service
echo [2/5] Stopping Ollama service...
taskkill /f /im ollama.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo     Ollama service stopped!
) else (
    echo     Ollama was not running
)

:: Stop Frontend (Node.js processes)
echo [3/5] Stopping React frontend...
taskkill /f /im node.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo     Frontend processes stopped!
) else (
    echo     No frontend processes found
)

:: Stop Backend (Python processes) - Be more selective
echo [4/5] Stopping FastAPI backend...
wmic process where "name='python.exe' and commandline like '%%uvicorn%%'" delete >nul 2>&1
if %errorlevel% equ 0 (
    echo     Backend process stopped!
) else (
    echo     No backend processes found
)

:: Optional: Stop PostgreSQL (commented out - usually want to keep running)
echo [5/5] PostgreSQL database left running (use 'net stop postgresql-x64-17' to stop)

echo ================================================
echo AI Assistant Services Stopped Successfully!
echo ================================================
echo The following services have been stopped:
echo - NVIDIA NIM containers (embeddings, generation)
echo - Ollama service
echo - React frontend
echo - FastAPI backend
echo ================================================
echo PostgreSQL database left running for data persistence
echo Docker Desktop left running for other containers
echo ================================================

echo Press any key to close this window...
pause >nul