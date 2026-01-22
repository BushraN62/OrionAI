# Orion Dashboard - Quick Start & Troubleshooting

## 🚀 Quick Start

### Method 1: Automated Startup (Recommended)
```powershell
.\start_dashboard.bat
```
This will automatically:
1. Clean up any existing processes
2. Start Ollama server
3. Start Backend (FastAPI on port 9000)
4. Start Frontend (Vite on port 5174)

Wait ~10 seconds, then open: **http://localhost:5174**

---

## 🔧 Troubleshooting

### Issue: "Hey Orion!" message stuck / No response

**Cause:** Backend can't connect to Ollama or Ollama isn't responding

**Solution 1: Check Service Status**
```powershell
.\check_status.bat
```
This will show you which services are running and which are not.

**Solution 2: Hard Reset**
```powershell
# Stop everything
.\stop_all.bat

# Wait 5 seconds
# Then restart
.\start_dashboard.bat
```

**Solution 3: Manual Startup (More Control)**
```powershell
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Backend (wait 10 seconds after Ollama)
cd "W:\VS Code Projects\Orion  ( Qwen2.5 VL 7B )"
orion-env\Scripts\activate
python -m uvicorn server.main:app --host 0.0.0.0 --port 9000 --reload

# Terminal 3: Start Frontend
cd ui\dashboard
npm run dev
```

---

### Issue: Ollama not responding

**Check if Ollama is installed:**
```powershell
ollama --version
```

**Manually test Ollama:**
```powershell
# Start Ollama
ollama serve

# In another terminal, test it
ollama list
```

**Check if port 11434 is blocked:**
```powershell
netstat -ano | findstr ":11434"
```

---

### Issue: Backend fails to start

**Check Python environment:**
```powershell
orion-env\Scripts\activate
python --version
```

**Check if port 9000 is already in use:**
```powershell
netstat -ano | findstr ":9000"
```

**Kill process on port 9000:**
```powershell
# Find PID from netstat output, then:
taskkill /F /PID <PID_NUMBER>
```

---

### Issue: Frontend fails to start

**Check Node.js:**
```powershell
node --version
npm --version
```

**Reinstall dependencies:**
```powershell
cd ui\dashboard
npm install
```

**Check if port 5174 is already in use:**
```powershell
netstat -ano | findstr ":5174"
```

---

## 📋 Utility Scripts

| Script | Purpose |
|--------|---------|
| `start_dashboard.bat` | Start all services (Ollama + Backend + Frontend) |
| `stop_all.bat` | Stop all Orion services |
| `check_status.bat` | Check which services are running |

---

## 🔍 Debug Mode

If issues persist, run backend manually to see detailed logs:

```powershell
cd "W:\VS Code Projects\Orion  ( Qwen2.5 VL 7B )"
orion-env\Scripts\activate
python -m server.main
```

Watch for errors in the output. Common issues:
- `[WARNING] Failed to load Faster Whisper` - STT won't work (optional)
- `[WARNING] Failed to load Coqui TTS` - TTS won't work (optional)
- Connection errors to Ollama - Ollama isn't running

---

## ✅ Healthy Startup Looks Like:

```
[STT] Loading Faster Whisper model 'base' on cpu...
[OK] Faster Whisper loaded successfully
[TTS] Loading Coqui TTS model 'tts_models/en/jenny/jenny'...
[OK] Coqui TTS loaded successfully
[OK] Loaded memory from data/memory.json

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9000
```

---

## 🆘 Still Stuck?

1. Run `.\check_status.bat` - Note which services fail
2. Run `.\stop_all.bat` - Clean slate
3. Manually start Ollama: `ollama serve`
4. Wait 10 seconds
5. Run `.\start_dashboard.bat`

If Ollama keeps crashing:
```powershell
# Reinstall Ollama or update it
ollama pull qwen2.5:1.5b
```
