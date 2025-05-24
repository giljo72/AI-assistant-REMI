@echo off
echo Starting Backend API in new window...
cd /d "F:\Assistant\backend"
start "Backend API" cmd /k "..\venv_nemo\Scripts\python.exe" -m uvicorn app.main:app --reload --port 8000
echo Backend window should now be open
pause