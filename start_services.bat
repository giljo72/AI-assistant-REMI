@echo off
setlocal EnableDelayedExpansion

echo Starting AI Assistant services...
echo.

REM Check for PostgreSQL service
echo Checking PostgreSQL service...
sc query postgresql-x64-17 | find "RUNNING" > nul
if %ERRORLEVEL% NEQ 0 (
    echo PostgreSQL is not running. Attempting to start...
    net start postgresql-x64-17
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to start PostgreSQL. Please start it manually with admin privileges.
        echo Command: net start postgresql-x64-17
        echo.
        echo Press any key to continue anyway...
        pause > nul
    ) else (
        echo PostgreSQL service started successfully.
    )
) else (
    echo PostgreSQL service is already running.
)

REM Create required directories
echo Creating required directories...
if not exist "backend\data\uploads" mkdir "backend\data\uploads"
if not exist "backend\data\processed" mkdir "backend\data\processed"
if not exist "backend\data\logs" mkdir "backend\data\logs"
if not exist "backend\data\hierarchy" mkdir "backend\data\hierarchy"

REM Skip pgvector check for now as it might cause issues
echo Skipping pgvector check for now.

REM Start backend
echo Starting FastAPI backend...
cd backend
if exist "..\venv_nemo\Scripts\activate.bat" (
    call ..\venv_nemo\Scripts\activate.bat
) else (
    echo Warning: venv_nemo not found. Using system Python.
)

REM Initialize database
echo Initializing database...
python -m app.db.init_db
if %ERRORLEVEL% NEQ 0 (
    echo Database initialization failed. Please check error messages above.
    echo Press any key to continue anyway...
    pause > nul
) else (
    echo Database initialized successfully.
)

REM Start backend server in a new window
start "AI Assistant Backend" cmd /k "echo Starting backend server... && python -m uvicorn app.main:app --reload --port 8000"

REM Start frontend
echo Starting React frontend...
cd ..\frontend
start "AI Assistant Frontend" cmd /k "echo Starting frontend server... && npm run dev"

echo.
echo All services should be starting. The application should be available at:
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000/docs
echo.
echo NOTE: It may take a few moments for the servers to fully initialize.
echo Press any key to exit this window...
pause > nul
endlocal