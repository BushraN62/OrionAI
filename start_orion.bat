@echo off
echo Starting Orion AI Assistant...
echo.

REM Start Ollama server in background
echo [1/2] Starting Ollama server...
start "Ollama Server" /B cmd /c "ollama serve"
timeout /t 5 /nobreak > nul

REM Check if Ollama is running
echo [2/2] Starting Orion server...
python server/main.py

pause
