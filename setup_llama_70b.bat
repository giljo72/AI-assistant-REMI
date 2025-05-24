@echo off
echo Setting up Llama 3.1 70B NIM Container
echo ======================================
echo.

REM Load NGC_API_KEY from .env file if not already set
if "%NGC_API_KEY%"=="" (
    echo Loading NGC_API_KEY from .env file...
    for /f "tokens=2 delims==" %%a in ('findstr /B "NGC_API_KEY=" "%~dp0.env"') do set NGC_API_KEY=%%a
)

REM Check if NGC_API_KEY is now set
if "%NGC_API_KEY%"=="" (
    echo ERROR: NGC_API_KEY not found in environment or .env file!
    echo Please create a .env file with: NGC_API_KEY=your-key-here
    pause
    exit /b 1
)

echo NGC_API_KEY loaded successfully. Proceeding with setup...
echo.

echo Step 1: Stopping and removing the 8B container...
docker stop nim-generation-8b
docker rm nim-generation-8b

echo.
echo Step 2: Pulling Llama 3.1 70B container (this may take a while)...
docker pull nvcr.io/nim/meta/llama-3.1-70b-instruct:latest

echo.
echo Step 3: Creating Llama 70B container...
docker run -d ^
  --name nim-generation-70b ^
  --runtime=nvidia ^
  --gpus all ^
  -e NGC_API_KEY=%NGC_API_KEY% ^
  -p 8083:8000 ^
  --shm-size=16g ^
  --ulimit memlock=-1 ^
  --ulimit stack=67108864 ^
  --restart unless-stopped ^
  nvcr.io/nim/meta/llama-3.1-70b-instruct:latest

echo.
echo Waiting for container to initialize (this takes 2-3 minutes)...
timeout /t 60

echo.
echo Checking container status...
docker ps -a | findstr nim-generation-70b

echo.
echo Done! The Llama 70B container should now be running on port 8083.
echo You can verify in Docker Desktop.
echo.
pause