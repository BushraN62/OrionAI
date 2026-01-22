@echo off
echo ========================================
echo Starting Orion AI Assistant...
echo ========================================
echo.

REM Check if Ollama is already running
echo [1/3] Checking Ollama status...
curl -s http://localhost:11434/api/tags > nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] Ollama is already running!
) else (
    echo    Starting Ollama server...
    start "Ollama Server" /MIN cmd /c "ollama serve"
    timeout /t 8 /nobreak > nul
    
    curl -s http://localhost:11434/api/tags > nul 2>&1
    if %errorlevel% equ 0 (
        echo    [OK] Ollama server started successfully!
    ) else (
        echo    [WARNING] Could not verify Ollama. The server may start it automatically.
    )
)
echo.

REM Activate virtual environment
echo [2/3] Activating Python environment...
if exist "orion-env\Scripts\activate.bat" (
    call orion-env\Scripts\activate.bat
    echo    [OK] Virtual environment activated
) else (
    echo    [WARNING] Virtual environment not found, using system Python
)
echo.

REM Start Orion
echo [3/3] Starting Orion server...
echo.
echo ========================================
echo  Orion will be available at:
echo  http://localhost:9000
echo  Dashboard: http://localhost:5173
echo ========================================
echo.

python server/main.py

pause
