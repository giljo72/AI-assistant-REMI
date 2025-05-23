@echo off
echo ========================================
echo AI Assistant Model Installation Script
echo ========================================
echo.

echo Installing DeepSeek-Coder-V2-Lite model...
echo This may take some time depending on your internet connection.
echo.

REM Pull the DeepSeek-Coder model
echo [1/2] Pulling DeepSeek-Coder-V2-Lite model...
ollama pull deepseek-coder-v2:16b-lite-instruct-q4_K_M

echo.
echo [2/2] Verifying installation...
ollama list

echo.
echo ========================================
echo Installation complete!
echo.
echo Available models:
ollama list
echo.
echo To test the model, run:
echo   ollama run deepseek-coder-v2:16b-lite-instruct-q4_K_M "Write a Python hello world"
echo.
pause