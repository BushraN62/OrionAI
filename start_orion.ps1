# Start Orion with Ollama
Write-Host "Starting Orion AI Assistant..." -ForegroundColor Cyan
Write-Host ""

# Start Ollama server
Write-Host "[1/2] Starting Ollama server..." -ForegroundColor Yellow
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
Start-Sleep -Seconds 5

# Check if Ollama started
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    Write-Host "   Ollama server is running!" -ForegroundColor Green
} catch {
    Write-Host "   Warning: Could not verify Ollama server status" -ForegroundColor Yellow
}

# Start Orion
Write-Host "[2/2] Starting Orion server..." -ForegroundColor Yellow
Write-Host ""
python server/main.py
