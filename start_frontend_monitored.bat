@echo off
title AI Assistant - Frontend (Monitored)
cd /d "%~dp0frontend"

:check_flag
if not exist "..\.services_running" (
    echo.
    echo Services shutdown detected. Stopping frontend...
    exit
)

echo Starting Frontend Development Server...
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

REM Run npm dev with monitoring
:run_frontend
npm run dev

REM If we get here, either the server crashed or was stopped
if exist "..\.services_running" (
    echo.
    echo Frontend server stopped unexpectedly!
    echo Restarting in 5 seconds...
    timeout /t 5 >nul
    goto :check_flag
) else (
    echo Frontend shutdown complete.
    exit
)