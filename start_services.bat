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

echo Checking for pgvector extension...
call :check_pgvector

echo Creating required directories...
if not exist "backend\data\uploads" mkdir "backend\data\uploads"
if not exist "backend\data\processed" mkdir "backend\data\processed"
if not exist "backend\data\logs" mkdir "backend\data\logs"
if not exist "backend\data\hierarchy" mkdir "backend\data\hierarchy"

echo Verifying database setup...
cd backend
call ..\venv_nemo\Scripts\activate
python -m app.db.init_db
if %ERRORLEVEL% NEQ 0 (
    echo Database initialization failed. Please check error messages above.
    echo Press any key to continue anyway...
    pause > nul
) else (
    echo Database initialized successfully.
)

echo Starting FastAPI backend...
start cmd /k "title AI Assistant Backend && ..\venv_nemo\Scripts\python -m uvicorn app.main:app --reload --port 8000"

echo Starting React frontend...
cd ..\frontend
start cmd /k "title AI Assistant Frontend && npm run dev"

echo.
echo All services started. The application should be available at:
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000/docs
echo.
echo Press any key to exit this setup window...
pause > nul
exit /b 0

:check_pgvector
@echo off
setlocal EnableDelayedExpansion

:: Create a temporary SQL file to check pgvector
echo SELECT * FROM pg_extension WHERE extname = 'vector'; > check_pgvector.sql

:: Run the query
set "PG_OUTPUT="
for /F "usebackq delims=" %%A in (`"postgresql-x64-17\bin\psql -U postgres -d ai_assistant -f check_pgvector.sql"`) do (
    set "PG_OUTPUT=!PG_OUTPUT!%%A"
)

:: Delete the temporary file
del check_pgvector.sql

:: Check if the output contains 'vector'
echo !PG_OUTPUT! | findstr /C:"vector" > nul
if %ERRORLEVEL% NEQ 0 (
    echo Pgvector extension is not installed. Attempting to install it...
    echo CREATE EXTENSION IF NOT EXISTS vector; > install_pgvector.sql
    "postgresql-x64-17\bin\psql" -U postgres -d ai_assistant -f install_pgvector.sql
    del install_pgvector.sql
    
    :: Check if installation succeeded
    echo SELECT * FROM pg_extension WHERE extname = 'vector'; > check_pgvector.sql
    "postgresql-x64-17\bin\psql" -U postgres -d ai_assistant -f check_pgvector.sql | findstr /C:"vector" > nul
    if %ERRORLEVEL% NEQ 0 (
        echo NOTICE: Pgvector installation may have failed. Vector search may not work properly.
        echo Please install pgvector extension manually from https://github.com/pgvector/pgvector
    ) else (
        echo Pgvector extension installed successfully.
    )
    del check_pgvector.sql
) else (
    echo Pgvector extension is already installed.
)

endlocal
exit /b 0