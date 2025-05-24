@echo off
title AI Assistant - Clean Shutdown
color 0E

echo ================================================
echo AI Assistant - Clean Shutdown
echo ================================================
echo.

REM Remove the services running flag first (this signals all monitored processes to stop)
if exist "%~dp0.services_running" (
    echo Signaling services to stop...
    del "%~dp0.services_running" 2>nul
    timeout /t 2 >nul
)

REM Kill specific processes gracefully
echo.
echo Stopping services...

REM Stop Frontend (npm/node processes)
echo - Stopping Frontend...
taskkill /F /IM node.exe 2>nul
timeout /t 1 >nul

REM Stop Backend (Python/uvicorn)
echo - Stopping Backend...
for /f "tokens=2" %%i in ('tasklist ^| findstr /i "python.exe"') do (
    tasklist /FI "PID eq %%i" | findstr /i "uvicorn" >nul
    if not errorlevel 1 (
        taskkill /PID %%i /F 2>nul
    )
)
timeout /t 1 >nul

REM Stop Debug Monitor
echo - Stopping Debug Monitor...
for /f "tokens=2" %%i in ('tasklist ^| findstr /i "python.exe"') do (
    tasklist /FI "PID eq %%i" | findstr /i "debug_monitor" >nul
    if not errorlevel 1 (
        taskkill /PID %%i /F 2>nul
    )
)

REM Stop Ollama
echo - Stopping Ollama...
taskkill /F /IM ollama.exe 2>nul
timeout /t 1 >nul

REM Optional: Stop PostgreSQL (commented out by default)
REM echo - Stopping PostgreSQL...
REM net stop postgresql-x64-17 2>nul
REM net stop postgresql 2>nul

echo.
echo ================================================
echo All services stopped.
echo ================================================
echo.
pause