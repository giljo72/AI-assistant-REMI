@echo off
title AI Assistant - Full Stack
color 0A

echo ================================================
echo Starting AI Assistant - Full Stack
echo ================================================
cd /d "F:\assistant"

:: Kill any existing Ollama processes to ensure clean start
echo [1/7] Stopping existing Ollama processes...
taskkill /f /im ollama.exe >nul 2>&1

:: Start Docker Desktop if needed
echo [2/7] Starting Docker Desktop...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo     Docker not running, starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    :wait_docker
    timeout /t 5 /nobreak >nul
    docker info >nul 2>&1
    if %errorlevel% neq 0 goto wait_docker
    echo     Docker Desktop started successfully!
) else (
    echo     Docker Desktop already running!
)

:: Start PostgreSQL
echo [3/7] Starting PostgreSQL database...
net start postgresql-x64-17 >nul 2>&1
if %errorlevel% equ 0 (
    echo     PostgreSQL started successfully!
) else (
    echo     PostgreSQL already running or failed to start
)

:: Start NVIDIA NIM containers
echo [4/7] Starting NVIDIA NIM containers...
docker-compose up -d nim-embeddings nim-generation-8b
if %errorlevel% equ 0 (
    echo     NIM containers started successfully!
    echo     - Embeddings: http://localhost:8081
    echo     - Generation 8B: http://localhost:8082
) else (
    echo     Warning: NIM containers may have failed to start
)

:: Start Ollama with proper network binding
echo [5/7] Starting Ollama service...
start "Ollama Service" cmd /c "set OLLAMA_HOST=0.0.0.0:11434 && ollama serve"
timeout /t 3 /nobreak >nul
echo     Ollama started on all interfaces (port 11434)

:: Start backend
echo [6/7] Starting FastAPI backend...
start "AI Backend" cmd /k "cd /d F:\assistant\backend && ..\venv_nemo\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
echo     Backend started on http://0.0.0.0:8000 (accessible on LAN)

:: Start frontend
echo [7/7] Starting React frontend...
start "AI Frontend" cmd /k "cd /d F:\assistant\frontend && npm run dev"
timeout /t 5 /nobreak >nul
echo     Frontend started on http://0.0.0.0:5173 (accessible on LAN)

:: Display service summary
echo ================================================
echo AI Assistant Services Started Successfully!
echo ================================================
echo Backend:     http://localhost:8000 ^(LAN: http://10.1.0.224:8000^)
echo Frontend:    http://localhost:5173 ^(LAN: http://10.1.0.224:5173^)
echo NIM Embed:   http://localhost:8081
echo NIM Gen 8B:  http://localhost:8082  
echo Ollama:      http://localhost:11434 ^(LAN: http://10.1.0.224:11434^)
echo PostgreSQL:  localhost:5432
echo ================================================

:: Open the application
start http://localhost:5173

echo Press any key to close this window...
pause >nul