@echo off
echo Installing Required AI Models
echo =============================
echo.
echo This will install your 4 core models in Ollama:
echo   1. Qwen 2.5 32B (Primary model)
echo   2. Mistral Nemo (Fast responses)
echo   3. DeepSeek Coder v2 16B (Coding)
echo   4. Llama 70B is via NVIDIA NIM (Docker)
echo.
echo Note: This will download ~35GB of model data
echo.
pause

echo.
echo Installing Qwen 2.5 32B...
ollama pull qwen2.5:32b-instruct-q4_K_M

echo.
echo Installing Mistral Nemo...
ollama pull mistral-nemo:latest

echo.
echo Installing DeepSeek Coder v2 16B...
ollama pull deepseek-coder-v2:16b-lite-instruct-q4_K_M

echo.
echo Installation complete!
echo.
echo To verify installation, run: ollama list
echo.
pause