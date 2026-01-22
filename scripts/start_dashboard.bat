@echo off
echo ========================================
echo   Starting Orion Dashboard
echo ========================================
echo.

REM Kill any existing Ollama processes first
echo [CLEANUP] Stopping any existing Ollama processes...
taskkill /F /IM ollama.exe >nul 2>&1
taskkill /F /IM ollama_llama_server.exe >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Orion Backend*" >nul 2>&1
taskkill /F /IM node.exe /FI "WINDOWTITLE eq Orion Frontend*" >nul 2>&1
timeout /t 3 /nobreak >nul
echo     [OK] Cleanup complete

echo [1/3] Starting Ollama Server...
start "Ollama Server" cmd /c "ollama serve"
echo     Waiting for Ollama to initialize...
timeout /t 8 /nobreak >nul

REM Verify Ollama is responding
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Ollama server is running!
) else (
    echo     [WARNING] Ollama may not be ready yet
)

echo.
echo [2/3] Starting Backend Server (Port 9000)...
start "Orion Backend" cmd /k "cd /d "W:\VS Code Projects\Orion  ( Qwen2.5 VL 7B )" && orion-env\Scripts\activate && python -m uvicorn server.main:app --host 0.0.0.0 --port 9000 --reload"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Starting Frontend Server (Port 5174)...
start "Orion Frontend" cmd /k "cd /d "W:\VS Code Projects\Orion  ( Qwen2.5 VL 7B )\ui\dashboard" && set PATH=C:\Program Files\nodejs;%PATH% && "C:\Program Files\nodejs\npm.cmd" run dev"

echo.
echo ========================================
echo   Servers Starting...
echo ========================================
echo.
echo Backend:  http://localhost:9000
echo Frontend: http://localhost:5174
echo.
echo Wait ~10 seconds then open your browser to:
echo http://localhost:5174
echo.
echo Press any key to exit this window...
echo (The servers will keep running in separate windows)
pause >nul
