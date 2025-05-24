@echo off
echo AI Assistant Model Cleanup
echo ========================
echo.
echo This will optimize your model collection to:
echo   - Qwen 32B (default)
echo   - Llama 70B NIM (complex tasks)
echo   - Mistral Nemo (speed)
echo   - DeepSeek Coder (coding)
echo.
echo Models to REMOVE:
echo   - mistral-nemo:12b-instruct-2407-q4_0 (duplicate)
echo   - llama3.1:8b-instruct (redundant)
echo   - Any other unused models
echo.

cd /d "%~dp0"

if exist venv_nemo\Scripts\activate.bat (
    call venv_nemo\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

python scripts\cleanup_models.py

pause