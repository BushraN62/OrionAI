# Start Orion with Ollama - IMPROVED VERSION
Write-Host "Starting Orion AI Assistant..." -ForegroundColor Cyan
Write-Host ""

# Function to check if Ollama is running
function Test-OllamaRunning {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Check if Ollama is already running
Write-Host "[1/3] Checking Ollama status..." -ForegroundColor Yellow
if (Test-OllamaRunning) {
    Write-Host "   ✓ Ollama is already running!" -ForegroundColor Green
} else {
    Write-Host "   Starting Ollama server..." -ForegroundColor Yellow
    
    # Start Ollama in a minimized window
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
    
    # Wait for Ollama to be ready (max 30 seconds)
    $maxAttempts = 30
    $attempt = 0
    $ready = $false
    
    while ($attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 1
        $attempt++
        
        if (Test-OllamaRunning) {
            $ready = $true
            Write-Host "   ✓ Ollama server started successfully!" -ForegroundColor Green
            break
        }
        
        if ($attempt % 5 -eq 0) {
            Write-Host "   Still waiting for Ollama... ($attempt seconds)" -ForegroundColor Gray
        }
    }
    
    if (-not $ready) {
        Write-Host "   ⚠ Ollama didn't start in time. The server may start it automatically." -ForegroundColor Yellow
    }
}

# Activate virtual environment
Write-Host "[2/3] Activating Python environment..." -ForegroundColor Yellow
$envPath = ".\orion-env\Scripts\Activate.ps1"
if (Test-Path $envPath) {
    & $envPath
    Write-Host "   ✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Virtual environment not found, using system Python" -ForegroundColor Yellow
}

# Start Orion
Write-Host "[3/3] Starting Orion server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Orion will be available at: http://localhost:9000" -ForegroundColor Green
Write-Host "  Dashboard: http://localhost:5173" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

python server/main.py
