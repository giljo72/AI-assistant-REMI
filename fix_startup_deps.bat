@echo off
echo ================================================
echo Fixing Startup Dependencies
echo ================================================

REM Check if venv_nemo exists
if not exist "venv_nemo\Scripts\python.exe" (
    echo ERROR: Virtual environment venv_nemo not found!
    echo Please create it first with: python -m venv venv_nemo
    pause
    exit /b 1
)

echo Installing required packages for startup script...
venv_nemo\Scripts\python.exe -m pip install psutil requests

echo.
echo Installing backend dependencies...
cd backend
..\venv_nemo\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo Installing additional dependencies...
..\venv_nemo\Scripts\python.exe -m pip install pydantic-settings aiohttp

cd ..

echo.
echo Dependencies installed. You can now run startai.bat
pause