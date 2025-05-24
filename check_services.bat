@echo off
title AI Assistant - Service Status Check
color 0F
echo ================================================
echo AI Assistant - Service Status Check
echo ================================================
echo.

REM Check PostgreSQL
echo [PostgreSQL]
sc query postgresql-x64-17 2>nul | find "RUNNING" >nul
if %errorlevel%==0 (
    echo Status: RUNNING
) else (
    sc query postgresql 2>nul | find "RUNNING" >nul
    if %errorlevel%==0 (
        echo Status: RUNNING
    ) else (
        echo Status: NOT RUNNING
    )
)

REM Check Ollama
echo.
echo [Ollama]
tasklist | find "ollama.exe" >nul
if %errorlevel%==0 (
    echo Status: RUNNING
    curl -s http://localhost:11434/api/version >nul 2>&1
    if %errorlevel%==0 (
        echo API: RESPONSIVE
    ) else (
        echo API: NOT RESPONSIVE
    )
) else (
    echo Status: NOT RUNNING
)

REM Check Backend
echo.
echo [Backend API]
curl -s http://localhost:8000/api/health/ping >nul 2>&1
if %errorlevel%==0 (
    echo Status: RUNNING
    echo URL: http://localhost:8000/docs
) else (
    echo Status: NOT RUNNING
)

REM Check Frontend
echo.
echo [Frontend]
netstat -an | findstr :5173 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    echo Status: RUNNING
    echo URL: http://localhost:5173
) else (
    echo Status: NOT RUNNING
)

echo.
echo ================================================
pause