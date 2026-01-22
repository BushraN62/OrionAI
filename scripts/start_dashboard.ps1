# Start Orion Dashboard (Backend + Frontend)
Write-Host "Starting Orion Dashboard..." -ForegroundColor Cyan
Write-Host ""

# Start Ollama server
Write-Host "[1/3] Starting Ollama server..." -ForegroundColor Yellow
$ollamaProcess = Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized -PassThru
Start-Sleep -Seconds 5

# Verify Ollama is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    Write-Host "   [OK] Ollama server is running!" -ForegroundColor Green
} catch {
    Write-Host "   [WARNING] Could not verify Ollama server status" -ForegroundColor Yellow
}

# Start Backend (FastAPI)
Write-Host "[2/3] Starting Backend (FastAPI on port 9000)..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m", "server.main" -WindowStyle Normal -PassThru
Start-Sleep -Seconds 3

# Start Frontend (Vite)
Write-Host "[3/3] Starting Frontend (Vite dev server)..." -ForegroundColor Yellow
Set-Location "ui\dashboard"
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Normal -PassThru
Set-Location "..\..\"

Write-Host ""
Write-Host "[SUCCESS] Orion Dashboard is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:9000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5175" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services..." -ForegroundColor Yellow

# Keep script running and handle cleanup
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host ""
    Write-Host "[SHUTDOWN] Stopping services..." -ForegroundColor Red
    
    if ($frontendProcess -and !$frontendProcess.HasExited) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "   Stopped Frontend" -ForegroundColor Yellow
    }
    
    if ($backendProcess -and !$backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "   Stopped Backend" -ForegroundColor Yellow
    }
    
    if ($ollamaProcess -and !$ollamaProcess.HasExited) {
        Stop-Process -Id $ollamaProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "   Stopped Ollama" -ForegroundColor Yellow
    }
    
    Write-Host "[OK] All services stopped" -ForegroundColor Green
}
