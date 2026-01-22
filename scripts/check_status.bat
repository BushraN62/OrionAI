@echo off
echo ========================================
echo   Orion Service Status Check
echo ========================================
echo.

echo [1/3] Checking Ollama Server (Port 11434)...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Ollama is running and responding
) else (
    echo     [ERROR] Ollama is not responding
    echo     Try running: ollama serve
)

echo.
echo [2/3] Checking Backend Server (Port 9000)...
curl -s http://localhost:9000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Backend is running and responding
) else (
    echo     [ERROR] Backend is not responding
    echo     Check if Python server is running
)

echo.
echo [3/3] Checking Frontend Server (Port 5174)...
curl -s http://localhost:5174 >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Frontend is running and responding
) else (
    echo     [ERROR] Frontend is not responding
    echo     Check if Vite dev server is running
)

echo.
echo ========================================
echo   Running Processes:
echo ========================================
echo.
echo Ollama processes:
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find "ollama.exe" >nul
if %errorlevel% equ 0 (
    tasklist /FI "IMAGENAME eq ollama.exe"
) else (
    echo     [NONE]
)

echo.
echo Python processes (Backend):
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find "python.exe" >nul
if %errorlevel% equ 0 (
    tasklist /FI "IMAGENAME eq python.exe"
) else (
    echo     [NONE]
)

echo.
echo Node processes (Frontend):
tasklist /FI "IMAGENAME eq node.exe" 2>nul | find "node.exe" >nul
if %errorlevel% equ 0 (
    tasklist /FI "IMAGENAME eq node.exe"
) else (
    echo     [NONE]
)

echo.
echo ========================================
pause
