@echo off
echo Setting up NVIDIA NIM Llama 3.1 70B Container
echo =============================================
echo.
echo This will set up the Llama 70B model via NVIDIA NIM
echo Note: This requires ~40GB disk space for the container
echo.
echo IMPORTANT: You need an NVIDIA API key for this
echo Get one from: https://build.nvidia.com/
echo.
pause

echo.
echo First, let's stop the 8B container since we won't use it...
docker stop nim-generation-8b
docker rm nim-generation-8b

echo.
echo Pulling Llama 3.1 70B NIM container...
docker pull nvcr.io/nim/meta/llama-3.1-70b-instruct:latest

echo.
echo Creating and starting Llama 70B container...
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
echo Waiting for container to start (this may take 2-3 minutes)...
timeout /t 30

echo.
echo Checking container status...
docker ps | findstr nim-generation-70b

echo.
echo Testing health endpoint...
curl -s http://localhost:8083/v1/health/ready

echo.
echo Setup complete! 
echo.
echo The Llama 70B model should now be available on port 8083
echo You can check Docker Desktop to verify it's running
echo.
pause