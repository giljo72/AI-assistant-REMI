@echo off
echo Starting AI Assistant services...
echo.

echo Starting PostgreSQL service...
net start postgresql-x64-17

echo Starting FastAPI backend...
cd backend
call ..\venv_nemo\Scripts\activate
start cmd /k "python -m uvicorn app.main:app --reload --port 8000"

echo Starting React frontend...
cd ..\frontend
start cmd /k "npm run dev"

echo.
echo All services started. The application should be available at:
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000/docs
echo.
echo Press any key to continue...
pause > nul