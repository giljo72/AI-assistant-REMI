@echo off
echo ========================================
echo Checking Installed Models
echo ========================================
echo.

echo Currently installed Ollama models:
echo ---------------------------------
ollama list

echo.
echo Checking specific models needed:
echo ---------------------------------

echo.
echo [1] Mistral-Nemo (Chat/Drafting):
ollama list | findstr /i "mistral-nemo" >nul
if %errorlevel%==0 (
    echo    ✓ INSTALLED
) else (
    echo    ✗ NOT INSTALLED
)

echo.
echo [2] DeepSeek-Coder-V2 (Code Analysis):
ollama list | findstr /i "deepseek-coder-v2" >nul
if %errorlevel%==0 (
    echo    ✓ INSTALLED
) else (
    echo    ✗ NOT INSTALLED - Run: ollama pull deepseek-coder-v2:16b-lite-instruct-q4_K_M
)

echo.
echo [3] Qwen 2.5 32B (Business Reasoning):
ollama list | findstr /i "qwen2.5:32b" >nul
if %errorlevel%==0 (
    echo    ✓ INSTALLED
) else (
    echo    ✗ NOT INSTALLED - Run: ollama pull qwen2.5:32b-instruct-q4_K_M
)

echo.
echo [4] Llama 3.1 70B (Deep Business Analysis):
echo    ⚠ Requires NVIDIA NIM Docker container (not Ollama)

echo.
echo [5] NV-Embedqa-E5-v5 (Document Embeddings):
echo    ⚠ Requires NVIDIA NIM Docker container (not Ollama)

echo.
echo ========================================
echo Note: Only Ollama models are checked.
echo NVIDIA NIM models run in Docker containers.
echo ========================================
echo.
pause