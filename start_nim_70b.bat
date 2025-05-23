@echo off
echo Starting NVIDIA NIM Llama 3.1 70B container...
echo This requires ~22GB VRAM and may take 5-10 minutes for first startup
echo.

REM Start the container
docker-compose up -d nim-generation-70b

echo.
echo Waiting for container to be ready...
timeout /t 10 /nobreak > nul

REM Check container status
docker ps --filter "name=nim-generation-70b" --format "table {{.Names}}\t{{.Status}}"

echo.
echo Checking health status (this may take a few minutes)...
echo Press Ctrl+C to stop checking (container will continue running)
echo.

:healthcheck
timeout /t 5 /nobreak > nul
curl -s http://localhost:8000/v1/health/ready
if %errorlevel% equ 0 (
    echo.
    echo ✓ Llama 3.1 70B NIM is ready!
    echo Access at: http://localhost:8000
    echo.
    echo To stop the container: docker-compose stop nim-generation-70b
    pause
    exit /b 0
) else (
    echo Still starting up...
    goto healthcheck
)