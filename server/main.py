# server/main.py - FIXED personality value handling
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import sys
import os
import tempfile
import base64
import asyncio
import concurrent.futures

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orion.app.cli import (
    chat, 
    list_memories, 
    add_memory, 
    delete_memory,
    set_personality,
    get_personality
)

# === LOCAL AI IMPORTS (ALWAYS USED FOR TTS/STT) ===
try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except ImportError:
    print("âš ï¸ Coqui TTS not available")
    COQUI_AVAILABLE = False

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    print("âš ï¸ Faster Whisper not available")
    FASTER_WHISPER_AVAILABLE = False

try:
    import torch
    import soundfile as sf
    import numpy as np
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    print("âš ï¸ Audio processing libraries not available")
    AUDIO_LIBS_AVAILABLE = False

from dotenv import load_dotenv
load_dotenv(override=True)

ORION_MODE = os.getenv("ORION_MODE", "hybrid").lower()

# === INITIALIZE LOCAL SERVICES (ALWAYS LOADED) ===
whisper_model = None
if FASTER_WHISPER_AVAILABLE:
    try:
        WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
        WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
        WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "float16" if torch.cuda.is_available() else "float32")
        
        print(f"ðŸŽ¤ Loading Faster Whisper model '{WHISPER_MODEL}' on {WHISPER_DEVICE}...")
        whisper_model = WhisperModel(
            WHISPER_MODEL, 
            device=WHISPER_DEVICE, 
            compute_type=WHISPER_COMPUTE_TYPE
        )
        print("âœ… Faster Whisper loaded successfully")
    except Exception as e:
        print(f"âš ï¸ Failed to load Faster Whisper: {e}")
        whisper_model = None

tts_model = None
if COQUI_AVAILABLE:
    try:
        COQUI_TTS_MODEL = os.getenv("COQUI_TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")
        print(f"ðŸ—£ï¸ Loading Coqui TTS model '{COQUI_TTS_MODEL}'...")
        tts_model = TTS(model_name=COQUI_TTS_MODEL, progress_bar=False)
        print("âœ… Coqui TTS loaded successfully")
    except Exception as e:
        print(f"âš ï¸ Failed to load Coqui TTS: {e}")
        tts_model = None

app = FastAPI(title="Orion AI Assistant - Multi-Mode Edition")
from server.routers.zephyr_ops import router as zephyr_router
app.include_router(zephyr_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for TTS generation
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    mode: str = "hybrid"
    personality: Optional[Dict] = None
    enable_tts: bool = False

class ChatResponse(BaseModel):
    response: str
    mode: str
    audio: Optional[str] = None
    audio_format: Optional[str] = None
    
class MemoryRequest(BaseModel):
    memory: str
    
class PersonalityRequest(BaseModel):
    humor: float = 0.5  # FIXED: Changed from int to float
    verbosity: float = 0.5  # FIXED: Changed from int to float
    formality: float = 0.5  # FIXED: Added formality
    creativity: float = 0.6  # FIXED: Added creativity
    speak: bool = False

class TTSRequest(BaseModel):
    text: str

# Check if assets directory exists
assets_dir = "ui/web/assets"
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir, exist_ok=True)

if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/")
async def serve_ui():
    ui_path = "ui/web/index.html"
    if not os.path.exists(ui_path):
        return JSONResponse(
            status_code=404,
            content={"error": f"UI file not found at {ui_path}. Please ensure the file exists."}
        )
    return FileResponse(ui_path)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "orion-multimode",
        "mode": ORION_MODE,
        "ai_services": {
            "llm": f"Ollama (Local)" if ORION_MODE == "strict" else f"OpenAI GPT-4 (Cloud)",
            "tts": "Coqui TTS (Local)" if tts_model else "None",
            "stt": "Faster Whisper (Local)" if whisper_model else "None"
        }
    }

def generate_tts_sync(text: str) -> tuple:
    """Synchronous TTS generation for thread pool"""
    if not tts_model or not AUDIO_LIBS_AVAILABLE:
        return None, None
        
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            wav_path = tmp_wav.name
        
        COQUI_TTS_SPEAKER = os.getenv("COQUI_TTS_SPEAKER", "")
        if COQUI_TTS_SPEAKER:
            tts_model.tts_to_file(text=text, speaker=COQUI_TTS_SPEAKER, file_path=wav_path)
        else:
            tts_model.tts_to_file(text=text, file_path=wav_path)
        
        with open(wav_path, "rb") as f:
            audio_bytes = f.read()
        
        try:
            os.remove(wav_path)
        except:
            pass
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        return audio_base64, "wav"
        
    except Exception as e:
        print(f"TTS generation error: {e}")
        return None, None

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # FIXED: Pass personality values as floats (0.0-1.0), not integers
        if request.personality:
            print(f"ðŸ” DEBUG - Received personality from frontend: {request.personality}")
            
            set_personality(
                humor=float(request.personality.get("humor", 0.5)),  # FIXED: Keep as float
                verbosity=float(request.personality.get("verbosity", 0.5)),  # FIXED: Keep as float
                formality=float(request.personality.get("formality", 0.5)),  # FIXED: Added
                creativity=float(request.personality.get("creativity", 0.6)),  # FIXED: Added
                speak=request.personality.get("speak", False)
            )
            
            # Debug: Check what was set
            current_personality = get_personality()
            print(f"ðŸ” DEBUG - Personality after setting: {current_personality}")
        
        # Process via mode-aware orchestrator
        response_text = chat(request.message, mode=request.mode)
        
        # Generate TTS in parallel if requested
        audio_data = None
        audio_format = None
        
        if request.enable_tts and tts_model:
            loop = asyncio.get_event_loop()
            audio_data, audio_format = await loop.run_in_executor(
                executor, 
                generate_tts_sync, 
                response_text
            )
        
        return ChatResponse(
            response=response_text,
            mode=ORION_MODE,
            audio=audio_data,
            audio_format=audio_format
        )
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory")
async def get_memories():
    try:
        memories = list_memories()
        return {"memories": memories}
    except Exception as e:
        print(f"Error in get_memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory")
async def add_memory_endpoint(request: MemoryRequest):
    try:
        add_memory(request.memory)
        return {"status": "success", "memory": request.memory}
    except Exception as e:
        print(f"Error in add_memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/memory")
async def delete_memory_endpoint(request: MemoryRequest):
    try:
        delete_memory(request.memory)
        return {"status": "success", "deleted": request.memory}
    except Exception as e:
        print(f"Error in delete_memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/personality")
async def get_personality_endpoint():
    try:
        personality = get_personality()
        return personality
    except Exception as e:
        print(f"Error in get_personality: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/personality")
async def set_personality_endpoint(request: PersonalityRequest):
    try:
        # FIXED: Pass as floats
        set_personality(
            humor=float(request.humor),
            verbosity=float(request.verbosity),
            formality=float(request.formality),
            creativity=float(request.creativity),
            speak=request.speak
        )
        return {"status": "success", "personality": request.dict()}
    except Exception as e:
        print(f"Error in set_personality: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Local STT (Faster Whisper only)
@app.post("/api/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert speech to text using Faster Whisper (local only)"""
    try:
        print(f"Received audio file: {audio.filename}, type: {audio.content_type}")
        
        if not whisper_model:
            return {"transcript": "", "status": "error", "error": "Faster Whisper not available"}
        
        # Save audio with appropriate extension based on content type
        content = await audio.read()
        
        # Determine file extension from content type or default to webm
        suffix = ".webm"
        if audio.content_type:
            if "mp4" in audio.content_type or "m4a" in audio.content_type:
                suffix = ".mp4"
            elif "wav" in audio.content_type:
                suffix = ".wav"
            elif "ogg" in audio.content_type:
                suffix = ".ogg"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            print("🎤 Using Faster Whisper...")
            
            # Try to convert webm/mp4/ogg to wav using available libraries
            final_file = tmp_file_path
            converted_file = None
            
            if suffix in [".webm", ".mp4", ".ogg"]:
                print(f"⚠️ Browser recorded {suffix} format - Whisper prefers WAV/MKV")
                print("Attempting conversion...")
                
                # Try pydub first (requires ffmpeg)
                try:
                    from pydub import AudioSegment
                    print(f"Converting {suffix} to WAV using pydub...")
                    audio = AudioSegment.from_file(tmp_file_path)
                    converted_file = tmp_file_path.replace(suffix, ".wav")
                    audio.export(converted_file, format="wav", parameters=["-ac", "1", "-ar", "16000"])
                    final_file = converted_file
                    print("✓ Conversion successful")
                except Exception as pydub_error:
                    print(f"⚠️ Pydub conversion failed: {pydub_error}")
                    print("Trying direct Whisper on original file (may work with faster-whisper v1+)...")
                    # Will try original file
            
            print(f"Transcribing with Whisper from: {final_file}")
            segments, info = whisper_model.transcribe(
                final_file, 
                beam_size=5,
                language="en",
                task="transcribe"
            )
            
            text = ""
            for segment in segments:
                text += segment.text + " "
            text = text.strip()
            
            if len(text) >= 2:
                print(f"Faster Whisper transcribed: {text}")
                return {"transcript": text, "status": "success", "service": "faster-whisper"}
            else:
                return {"transcript": "", "status": "error", "error": "No speech detected"}
                
        finally:
            # Clean up both original and converted files
            try:
                os.remove(tmp_file_path)
                if converted_file and os.path.exists(converted_file):
                    os.remove(converted_file)
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up temp files: {cleanup_error}")
                
    except Exception as e:
        print(f"STT Error: {e}")
        return {"transcript": "", "status": "error", "error": str(e)}

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using Coqui TTS (local only)"""
    try:
        text = request.text
        if not text:
            return {"status": "error", "error": "No text provided"}
        
        loop = asyncio.get_event_loop()
        audio_data, audio_format = await loop.run_in_executor(
            executor, 
            generate_tts_sync, 
            text
        )
        
        if audio_data:
            return {
                "status": "success",
                "audio": audio_data,
                "format": audio_format,
                "service": "coqui-tts"
            }
        else:
            return {"status": "error", "error": "TTS generation failed"}
            
    except Exception as e:
        print(f"TTS Error: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/api/status")
async def ai_status():
    """Get status of AI services across modes"""
    return {
        "current_mode": ORION_MODE,
        "modes": {
            "strict": {
                "description": "Fully local (Ollama + Local Speech)",
                "llm": "Ollama",
                "privacy": "Maximum - No cloud calls"
            },
            "hybrid": {
                "description": "Cloud LLM + Local Speech + PII Redaction",
                "llm": "OpenAI GPT-4",
                "privacy": "High - Speech local, API calls logged & PII redacted"
            },
            "cloud": {
                "description": "Cloud LLM + Local Speech + Logging",
                "llm": "OpenAI GPT-4", 
                "privacy": "Medium - Speech local, API calls logged"
            }
        },
        "local_services": {
            "coqui_tts": {
                "available": tts_model is not None,
                "model": os.getenv("COQUI_TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")
            },
            "faster_whisper": {
                "available": whisper_model is not None,
                "model": os.getenv("WHISPER_MODEL", "base"),
                "device": os.getenv("WHISPER_DEVICE", "cpu")
            }
        },
        "privacy_features": {
            "api_logging": os.getenv("API_LOGGING_ENABLED", "true").lower() == "true" and ORION_MODE != "strict",
            "pii_redaction": os.getenv("PII_REDACTION_ENABLED", "true").lower() == "true" and ORION_MODE == "hybrid",
            "local_speech": True
        }
    }

import subprocess
import requests
import time

OLLAMA_HOST = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
ollama_process = None

def _ollama_running() -> bool:
    """Check if Ollama server is running"""
    try:
        # Try direct connection first
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        if r.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    
    # Also check if ollama process exists (fallback)
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, 
                              timeout=3,
                              creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
        return result.returncode == 0
    except:
        return False

def _start_ollama_server(wait_secs: float = 30.0):
    """Start Ollama server if not running"""
    global ollama_process
    
    if _ollama_running():
        print("✅ Ollama server is already running")
        return True
    
    try:
        print("🚀 Starting Ollama server...")
        
        # Check if already running via ollama list command
        try:
            result = subprocess.run(["ollama", "list"], 
                                  capture_output=True, 
                                  timeout=5,
                                  creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            if result.returncode == 0:
                print("✅ Ollama is already running in service mode")
                return True
        except:
            pass
        
        # Start the server as a detached process
        print("   Launching ollama serve as background process...")
        
        if os.name == 'nt':  # Windows
            # On Windows, use simple DETACHED_PROCESS to run in background
            # Note: Some Windows versions have issues with complex flags
            ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS,
                shell=False,
                close_fds=True
            )
        else:  # Unix/Linux
            ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        print(f"   Process started with PID {ollama_process.pid}")
        
        # Wait for server to be ready
        t0 = time.time()
        attempts = 0
        while time.time() - t0 < wait_secs:
            if _ollama_running():
                print("✅ Ollama server started successfully")
                return True
            attempts += 1
            if attempts % 10 == 0:  # Print progress every 5 seconds
                print(f"   Still waiting for Ollama... ({int(time.time() - t0)}s)")
            time.sleep(0.5)
        
        print("⚠️ Ollama server did not become ready in time")
        print("   Trying direct connection test...")
        
        # Final check
        time.sleep(2)
        if _ollama_running():
            print("✅ Ollama server is now ready")
            return True
        
        return False
    except Exception as e:
        print(f"❌ Failed to start Ollama server: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.get("/llm/on")
async def start_zephyr():
    """Start Zephyr model (ensures Ollama server is running)"""
    print("📡 Received LLM start request...")
    
    # First, check if Ollama is already running
    if _ollama_running():
        print("✅ Ollama already running, skipping startup")
    else:
        # Try to start Ollama if needed
        print("🚀 Attempting to start Ollama server...")
        success = _start_ollama_server()
        if not success:
            return {"status": "error", "error": "Failed to start Ollama server. Please start Ollama manually: open a new terminal and run 'ollama serve'"}
    
    # Wait a moment for server to fully initialize
    print("⏳ Waiting for Ollama to be ready...")
    time.sleep(2)
    
    # Pull/warm up the model
    try:
        print("🔥 Warming up zephyr:7b-beta model...")
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": "zephyr:7b-beta",
                "prompt": "hi",
                "stream": False,
                "keep_alive": "10m"  # Keep in memory for 10 minutes
            },
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Model warmed up successfully")
            return {"status": "started", "model": "zephyr:7b-beta", "keep_alive": "10m"}
        else:
            error_msg = f"Model warm-up failed with status {response.status_code}: {response.text}"
            print(f"❌ {error_msg}")
            return {"status": "error", "error": error_msg}
    except requests.exceptions.ConnectionError as e:
        error_msg = "Ollama server is not running. Please start it manually in a separate terminal: 'ollama serve'"
        print(f"❌ {error_msg}")
        return {"status": "error", "error": error_msg}
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error warming up model: {error_msg}")
        return {"status": "error", "error": error_msg}

@app.get("/llm/off")
async def stop_zephyr():
    """Stop Zephyr model and Ollama server"""
    global ollama_process
    
    try:
        # Clear model from memory
        try:
            requests.post(f"{OLLAMA_HOST}/api/generate", json={
                "model": "zephyr:7b-beta",
                "prompt": "hi",
                "keep_alive": "0s"  # Remove from memory
            }, timeout=5)
        except:
            pass  # Server might already be stopping
        
        # Stop the Ollama server process
        if ollama_process:
            try:
                print(f"🛑 Stopping Ollama server (PID {ollama_process.pid})...")
                if hasattr(ollama_process, 'terminate'):
                    ollama_process.terminate()
                # Wait for graceful shutdown
                try:
                    ollama_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    ollama_process.kill()
                ollama_process = None
                print("✅ Ollama server stopped")
            except Exception as e:
                print(f"⚠️ Error stopping Ollama: {e}")
        
        return {"status": "stopped", "note": "Ollama server stopped"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/llm/status")
async def status_zephyr():
    """Check Ollama server and model status"""
    try:
        # Quick check with timeout
        server_running = _ollama_running()
        
        # Try to check model status with quick timeout
        try:
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=1)
            if response.status_code == 200:
                models = response.json().get("models", [])
                zephyr_loaded = any(m.get("name", "").startswith("zephyr") for m in models)
                return {
                    "server_running": server_running,
                    "model_available": zephyr_loaded
                }
        except:
            pass
        
        return {"server_running": server_running, "model_available": False}
    except Exception as e:
        # Fail gracefully
        return {"server_running": False, "model_available": False}

if __name__ == "__main__":
    import uvicorn
    
    if not os.path.exists("ui/web/index.html"):
        print("âŒ ERROR: ui/web/index.html not found!")
        print("ðŸ“ Please ensure you've saved the HTML file to ui/web/index.html")
        sys.exit(1)
    
    print("ðŸŒŒ Starting Orion Multi-Mode Server...")
    print(f"ðŸ”§ Mode: {ORION_MODE.upper()}")
    if ORION_MODE == "strict":
        print("ðŸ”’ LLM: Ollama (Local)")
    else:
        print("â˜ï¸ LLM: OpenAI GPT-4 (Cloud)")
    print(f"ðŸ—£ï¸ TTS: {'Coqui TTS (Local)' if tts_model else 'None'}")
    print(f"ðŸŽ¤ STT: {'Faster Whisper (Local)' if whisper_model else 'None'}")
    print("ðŸ“ Open http://localhost:8000 in your browser")
    print("âš¡ Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "server.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"Using fallback method: {e}")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )