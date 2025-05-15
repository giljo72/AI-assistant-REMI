@echo off
echo Starting AI Assistant services...
echo.

echo Checking PostgreSQL service...
sc query postgresql-x64-17 | find "RUNNING" > nul
if %ERRORLEVEL% NEQ 0 (
    echo PostgreSQL is not running. Please start it manually with admin privileges.
    echo Command: net start postgresql-x64-17
    echo.
    echo Press any key to continue anyway...
    pause > nul
) else (
    echo PostgreSQL service is already running.
)

echo Starting FastAPI backend...
cd backend
call ..\venv_nemo\Scripts\activate
start cmd /k "python -m uvicorn app.main:app --reload --port 8000"

echo Starting React frontend...
cd ..\frontend
start cmd /k "npm run dev"

echo.
echo All services started. The application should be available at:
Frontend: http://localhost:5173
Backend API: http://localhost:8000/docs
echo.
echo Press any key to continue...
pause > nul