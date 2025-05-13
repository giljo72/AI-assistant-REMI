@echo off
echo Stopping AI Assistant services...
echo.

echo Stopping frontend servers...
taskkill /f /im node.exe

echo Stopping backend servers...
taskkill /f /im uvicorn.exe
taskkill /f /im python.exe

echo Stopping Ollama...
taskkill /f /im ollama.exe

echo Stopping PostgreSQL service...
net stop postgresql-x64-17

echo.
echo All services stopped.
echo.
echo Press any key to continue...
pause > nul