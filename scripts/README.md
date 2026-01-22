# Orion Scripts

This directory contains utility scripts for starting, stopping, and managing Orion services.

## 🚀 Startup Scripts

### Windows Batch Scripts (.bat)
- `start_orion.bat` - Start Orion backend with Ollama (auto-starts Ollama if not running)
- `start_ollama.bat` - Start Ollama service only
- `start_dashboard.bat` - Start the web dashboard (Vite dev server)
- `stop_all.bat` - Stop all Orion services
- `check_status.bat` - Check status of all services

### PowerShell Scripts (.ps1)
- `start_orion.ps1` - Start Orion backend with Ollama (PowerShell version)
- `start_dashboard.ps1` - Start the web dashboard (PowerShell version)
- `orion_quicktunnel.ps1` - Create a quick tunnel for external access

## 📖 Usage

### Starting Orion (Recommended)

**Option 1: Batch Script (Simple)**
```batch
.\scripts\start_orion.bat
```

**Option 2: PowerShell (More features)**
```powershell
.\scripts\start_orion.ps1
```

This will:
1. Check if Ollama is running
2. Start Ollama if needed
3. Activate Python virtual environment
4. Start the Orion backend server on port 8000

### Starting the Dashboard

**Batch:**
```batch
.\scripts\start_dashboard.bat
```

**PowerShell:**
```powershell
.\scripts\start_dashboard.ps1
```

Dashboard will be available at: http://localhost:5173

### Stopping Services

```batch
.\scripts\stop_all.bat
```

### Checking Status

```batch
.\scripts\check_status.bat
```

## 🔧 Configuration

Scripts use the following default ports:
- **Backend API**: 8000
- **Dashboard**: 5173 (Vite dev server)
- **Ollama**: 11434

## 📝 Notes

- Scripts assume Python virtual environment is at `orion-env/`
- Ollama must be installed for LLM functionality
- Node.js and npm required for dashboard
- PowerShell scripts may require execution policy adjustment:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## 🆘 Troubleshooting

If scripts fail to start services:
1. Check if ports are already in use
2. Ensure Python virtual environment exists
3. Verify Ollama is installed
4. Check logs in `data/logs/` directory

For more help, see [Troubleshooting Guide](../docs/guides/TROUBLESHOOTING.md)
