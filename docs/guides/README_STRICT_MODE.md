# Running Orion in STRICT Mode

## The Issue
In strict mode, Orion uses Ollama (local AI) instead of OpenAI. Ollama needs to be running as a background server.

## Solution: Start Ollama in a Separate Terminal

### Method 1: Manual (Recommended)
1. Open a **separate PowerShell/CMD window**
2. Run: `ollama serve`
3. **Keep that window open** - the Ollama server will keep running
4. In your original terminal, start Orion: `python server/main.py`

### Method 2: Using the Startup Script
Run: `.\start_orion.ps1` (PowerShell) or `start_orion.bat` (CMD)

This will automatically start Ollama first, then Orion.

## Verify Ollama is Running

Test with:
```powershell
Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing
```

Or:
```bash
curl http://localhost:11434/api/tags
```

## Troubleshooting

**Error: "Connection refused"**
- Make sure Ollama is running in a separate terminal
- Check Windows Firewall isn't blocking port 11434

**Error: "Model not found"**
- Run: `ollama pull zephyr:7b-beta`
- Wait for the 4.1GB download to complete

**Want to run in Hybrid/Cloud mode instead?**
- Change `.env`: `ORION_MODE=hybrid`
- No need for Ollama in hybrid/cloud mode
