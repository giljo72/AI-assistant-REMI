@echo off
title Ollama Service - Local Mode
echo Starting Ollama service on localhost only...
echo.
echo Ollama will be available at:
echo - http://localhost:11434
echo.
echo This is more secure and avoids firewall issues.
echo.

REM Start Ollama (default binds to localhost only)
ollama serve

pause