@echo off
echo ================================================
echo Removing CodeLlama from Ollama
echo ================================================
echo.

echo Removing codellama:13b-instruct-q4_0...
ollama rm codellama:13b-instruct-q4_0

echo.
echo CodeLlama has been removed.
echo.
pause