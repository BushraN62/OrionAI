# orion_quicktunnel.ps1 (clean version)
# Starts Ollama (11434), (optionally) your FastAPI (8000), and opens two Cloudflare Quick Tunnels.
# Prints the public URLs after waiting for cloudflared to output them.

param(
  [int]$OllamaPort = 11434,
  [int]$OrionPort = 8000,
  [string]$PythonExe = "python",
  [switch]$StartOrion = $true   # set to $false if your FastAPI is already running
)

function Ensure-Command($name) {
  $exists = (Get-Command $name -ErrorAction SilentlyContinue)
  if (-not $exists) {
    Write-Error "Missing required command: $name. Add it to PATH first."
    exit 1
  }
}
Ensure-Command "cloudflared"

# Optional: start Orion FastAPI if port isn't listening
function Test-Port($port) {
  try {
    $c = New-Object System.Net.Sockets.TcpClient("127.0.0.1", $port)
    $c.Close()
    return $true
  } catch { return $false }
}

# Try to start ollama serve if not already running
if (-not (Get-Process -Name "ollama" -ErrorAction SilentlyContinue)) {
  Write-Host "Starting Ollama..."
  Start-Process -FilePath "ollama" -ArgumentList @("serve") -WindowStyle Hidden
  Start-Sleep -Seconds 3
}

# Optionally start FastAPI
if ($StartOrion -and -not (Test-Port $OrionPort)) {
  Write-Host "Starting Orion FastAPI on port $OrionPort..."
  Start-Process -FilePath $PythonExe -ArgumentList @("server/main.py") -WindowStyle Hidden
  Start-Sleep -Seconds 3
}

# Start two cloudflared Quick Tunnels and redirect logs
Write-Host "Opening Cloudflare Quick Tunnel for Ollama on port $OllamaPort..."
$ollamaOut = Join-Path $env:TEMP "ollama_tunnel.log"
$ollamaErr = Join-Path $env:TEMP "ollama_tunnel.err"
$ollamaArgs = @("tunnel","--url","http://127.0.0.1:$OllamaPort","--loglevel","info")
$ollamaJob  = Start-Process -FilePath "cloudflared" -ArgumentList $ollamaArgs -NoNewWindow -PassThru `
                -RedirectStandardOutput $ollamaOut -RedirectStandardError $ollamaErr

Write-Host "Opening Cloudflare Quick Tunnel for Orion on port $OrionPort..."
$orionOut = Join-Path $env:TEMP "orion_tunnel.log"
$orionErr = Join-Path $env:TEMP "orion_tunnel.err"
$orionArgs = @("tunnel","--url","http://127.0.0.1:$OrionPort","--loglevel","info")
$orionJob  = Start-Process -FilePath "cloudflared" -ArgumentList $orionArgs -NoNewWindow -PassThru `
               -RedirectStandardOutput $orionOut -RedirectStandardError $orionErr

function Get-TunnelUrlFromLog($logPaths, $timeoutSeconds = 30) {
  $pattern = "https://[a-z0-9\-]+\.trycloudflare\.com"
  $sw = [Diagnostics.Stopwatch]::StartNew()
  while ($sw.Elapsed.TotalSeconds -lt $timeoutSeconds) {
    foreach ($logPath in $logPaths) {
      if (Test-Path $logPath) {
        $content = Get-Content $logPath -Raw -ErrorAction SilentlyContinue
        if ($content) {
          $m = [Regex]::Match($content, $pattern)
          if ($m.Success) { return $m.Value }
        }
      }
    }
    Start-Sleep -Milliseconds 500
  }
  return $null
}

# Wait up to 30s for each URL to appear in either stdout or stderr log
$ollamaUrl = Get-TunnelUrlFromLog @($ollamaOut, $ollamaErr) 30
$orionUrl  = Get-TunnelUrlFromLog @($orionOut,  $orionErr)  30

Write-Host ""
Write-Host "===== QUICK TUNNELS READY ====="
if ($ollamaUrl) {
  Write-Host "OLLAMA_URL: $ollamaUrl"
  Write-Host "Set for teammate shell:  \$Env:OLLAMA_BASE_URL=$ollamaUrl"
} else {
  Write-Warning "Could not detect Ollama tunnel URL. Check $ollamaOut and $ollamaErr"
}
if ($orionUrl) {
  Write-Host "ORION_API_URL: $orionUrl"
  Write-Host "Open UI at:       $orionUrl/"
  Write-Host "Health check:     $orionUrl/health"
} else {
  Write-Warning "Could not detect Orion tunnel URL. Check $orionOut and $orionErr"
}
Write-Host "================================"
Write-Host "To stop tunnels: close this PowerShell window, or end 'cloudflared' processes."
