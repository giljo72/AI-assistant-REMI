@echo off
echo ========================================
echo AI Assistant Complete Model Installation
echo ========================================
echo.

echo This script will install all required models for the multi-model architecture.
echo Make sure Ollama is running before proceeding.
echo.
pause

echo.
echo [1/3] Installing DeepSeek-Coder-V2-Lite (Code Analysis)...
echo Size: ~9GB
ollama pull deepseek-coder-v2:16b-lite-instruct-q4_K_M

echo.
echo [2/3] Installing Qwen 2.5 32B (Fast Business Reasoning)...
echo Size: ~17GB
ollama pull qwen2.5:32b-instruct-q4_K_M

echo.
echo [3/3] Checking Mistral-Nemo (Already installed)...
ollama pull mistral-nemo:latest

echo.
echo ========================================
echo Ollama Models Installation Complete!
echo ========================================
echo.
echo Installed models:
ollama list

echo.
echo ========================================
echo NVIDIA NIM Models Setup Instructions
echo ========================================
echo.
echo The following models require NVIDIA NIM containers:
echo.
echo 1. Llama 3.1 70B Instruct (Business Reasoning)
echo    docker run --runtime=nvidia --gpus all -p 8000:8000 ^
echo    -e NGC_API_KEY=your_key_here ^
echo    nvcr.io/nim/meta/llama-3.1-70b-instruct:latest
echo.
echo 2. NV-Embedqa-E5-v5 (Document Embeddings)
echo    docker run --runtime=nvidia --gpus all -p 8001:8000 ^
echo    -e NGC_API_KEY=your_key_here ^
echo    nvcr.io/nim/nvidia/nv-embedqa-e5-v5:latest
echo.
echo Note: You need an NVIDIA NGC API key from https://ngc.nvidia.com
echo.
echo ========================================
echo Total VRAM Requirements:
echo - Mistral-Nemo: 7GB
echo - DeepSeek-Coder: 9GB  
echo - Qwen 32B: 17GB
echo - Llama 70B: 22GB (NIM)
echo - NV-Embedqa: 2GB (NIM)
echo.
echo The orchestrator will manage loading/unloading to fit in 24GB VRAM.
echo ========================================
echo.
pause