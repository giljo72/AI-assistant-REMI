@echo off
title AI Assistant - Comprehensive Shutdown
color 0C

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
echo AI Assistant - Comprehensive Shutdown (Admin Mode)
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Using fallback shutdown method...
    goto fallback_shutdown
)

REM Run the comprehensive shutdown script
echo Stopping AI Assistant services...
echo.
echo Stopping:
echo - Frontend development server
echo - Backend API server
echo - NVIDIA NIM containers
echo - Ollama service
echo - Docker containers
echo.
python stop_assistant.py
goto end

:fallback_shutdown
echo Performing manual shutdown...
echo.

REM Stop Docker containers
echo [1/5] Stopping Docker containers...
docker-compose down >nul 2>&1

REM Stop specific NIM containers
echo [2/5] Stopping NIM containers...
docker stop nim-embeddings >nul 2>&1
docker stop nim-generation-70b >nul 2>&1
docker stop nim-generation-8b >nul 2>&1

REM Stop Ollama
echo [3/5] Stopping Ollama...
taskkill /f /im ollama.exe >nul 2>&1

REM Stop Node processes
echo [4/5] Stopping Frontend...
taskkill /f /im node.exe >nul 2>&1

REM Stop Python processes
echo [5/5] Stopping Backend...
wmic process where "name='python.exe' and commandline like '%%uvicorn%%'" delete >nul 2>&1

echo.
echo Manual shutdown complete.

:end
echo.
echo All services stopped.
echo Press any key to close...
pause >nul