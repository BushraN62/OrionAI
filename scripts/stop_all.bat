@echo off
echo ========================================
echo   Stopping All Orion Services
echo ========================================
echo.

echo [1/4] Stopping Frontend (Node/Vite)...
taskkill /F /IM node.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Frontend stopped
) else (
    echo     [INFO] No frontend process found
)

echo [2/4] Stopping Backend (Python)...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Backend stopped
) else (
    echo     [INFO] No backend process found
)

echo [3/4] Stopping Ollama Server...
taskkill /F /IM ollama.exe >nul 2>&1
taskkill /F /IM ollama_llama_server.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Ollama stopped
) else (
    echo     [INFO] No Ollama process found
)

echo [4/4] Cleaning up ports...
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   All services stopped
echo ========================================
pause
