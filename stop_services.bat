@echo off
echo Stopping AI Assistant services...
echo.

echo Stopping frontend service...
taskkill /FI "WINDOWTITLE eq AI Assistant Frontend*" /F
if %ERRORLEVEL% EQU 0 (
    echo Frontend service stopped.
) else (
    echo No running frontend service found.
)

echo Stopping backend service...
taskkill /FI "WINDOWTITLE eq AI Assistant Backend*" /F
if %ERRORLEVEL% EQU 0 (
    echo Backend service stopped.
) else (
    echo No running backend service found.
)

rem We don't want to kill all Node.js or Python processes, as they might be unrelated
rem We also don't want to stop PostgreSQL automatically as other apps might be using it

echo.
echo AI Assistant services have been stopped.
echo.
echo Note: PostgreSQL service was not stopped as other applications might be using it.
echo If you want to stop PostgreSQL, run: net stop postgresql-x64-17
echo.
echo Press any key to continue...
pause > nul