# server/main.py - FIXED personality value handling
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from orion.app.agents import get_agent_registry
from orion.app.memory.store import OrionMemory
from orion.app.orchestrator import process_query
from orion.app.session import get_session_manager, Session, Message
from orion.app.cli import (
    chat, 
    list_memories, 
    add_memory, 
    delete_memory,
    set_personality,
    get_personality
)

import sys
import os
import tempfile
import base64
import asyncio
import concurrent.futures
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# === LOCAL AI IMPORTS (ALWAYS USED FOR TTS/STT) ===
try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except ImportError:
    print("[WARNING] Coqui TTS not available")
    COQUI_AVAILABLE = False

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    print("[WARNING] Faster Whisper not available")
    FASTER_WHISPER_AVAILABLE = False

try:
    import torch
    import soundfile as sf
    import numpy as np
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    print("[WARNING] Audio processing libraries not available")
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
        
        print(f"[STT] Loading Faster Whisper model '{WHISPER_MODEL}' on {WHISPER_DEVICE}...")
        whisper_model = WhisperModel(
            WHISPER_MODEL, 
            device=WHISPER_DEVICE, 
            compute_type=WHISPER_COMPUTE_TYPE
        )
        print("[OK] Faster Whisper loaded successfully")
    except Exception as e:
        print(f"[WARNING] Failed to load Faster Whisper: {e}")
        whisper_model = None

tts_model = None
if COQUI_AVAILABLE:
    try:
        COQUI_TTS_MODEL = os.getenv("COQUI_TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")
        print(f"[TTS] Loading Coqui TTS model '{COQUI_TTS_MODEL}'...")
        tts_model = TTS(model_name=COQUI_TTS_MODEL, progress_bar=False)
        print("[OK] Coqui TTS loaded successfully")
    except Exception as e:
        print(f"[WARNING] Failed to load Coqui TTS: {e}")
        tts_model = None
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
    voice_model: Optional[str] = None
    speaker_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent: Optional[str] = "conversational"  # Add this
    model: Optional[str] = "qwen2.5:1.5b"    # Add this
    audio: Optional[str] = None
    audioformat: Optional[str] = None
    mode: str = "strict"
    
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
    voice_model: Optional[str] = None
    speaker_id: Optional[str] = None

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
    """Health check that verifies LLM availability in strict mode"""
    llm_healthy = True
    
    # In strict mode, verify Ollama is actually running
    if ORION_MODE == "strict":
        llm_healthy = _ollama_running()
        try:
            # Also verify the model is available
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_exists = any(m.get("name", "") == OLLAMA_MODEL for m in models)
                if not model_exists:
                    llm_healthy = False
        except:
            llm_healthy = False
    
    status = "healthy" if llm_healthy else "degraded"
    
    return {
        "status": status,
        "service": "orion-multi-mode",
        "mode": ORION_MODE,
        "llm_available": llm_healthy,
        "ai_services": {
            "llm": f"Ollama ({OLLAMA_MODEL})" if ORION_MODE == "strict" else f"OpenAI GPT-4 (Cloud)",
            "tts": "Coqui TTS (Local)" if tts_model is not None else "None",
            "stt": "Faster Whisper (Local)" if whisper_model is not None else "None",
        }
    }

def generate_tts_sync(text: str, voice_model: Optional[str] = None, speaker_id: Optional[str] = None) -> tuple:
    """Optimized TTS generation with model caching"""
    if not AUDIO_LIBS_AVAILABLE:
        return None, None
    
    if not text or not text.strip():
        return None, None
        
    try:
        model_to_use = voice_model or COQUI_TTS_MODEL
        tts_instance = get_tts_model(model_to_use)
        
        if not tts_instance:
            return None, None
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            wav_path = tmp_wav.name
        
        speaker = speaker_id or os.getenv("COQUI_TTS_SPEAKER", "")
        
        try:
            if speaker:
                tts_instance.tts_to_file(text=text, speaker=speaker, file_path=wav_path)
            else:
                tts_instance.tts_to_file(text=text, file_path=wav_path)
            
            with open(wav_path, "rb") as f:
                audio_bytes = f.read()
            
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            return audio_base64, "wav"
        finally:
            # Always cleanup temp file
            if os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except:
                    pass
        
    except Exception as e:
        print(f"TTS error: {e}")
        return None, None

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint with multi-agent support
    """
    try:
        memory = OrionMemory()
        
        # Get personality settings
        personality = request.personality or {}
        
        # Process query with multi-agent orchestrator
        response = process_query(
            query=request.message,
            memory=memory,
            outputhint="voice" if request.enable_tts else "text",
            username=None,
            legalname=None,
            traits=personality,
            profile=None,
            detectedemotion=None,
            strict=(request.mode == "strict")
        )
        
        # Handle both dict (new multi-agent) and string (old) responses
        if isinstance(response, dict):
            response_text = response.get("answer", "")
            agent_name = response.get("agent", "conversational")
            model_name = response.get("model", "qwen2.5:1.5b")
        else:
            response_text = response
            agent_name = "conversational"
            model_name = "qwen2.5:7b"
        
        # Handle TTS if enabled
        audio_data = None
        audio_format = None
        
        if request.enable_tts and COQUI_AVAILABLE:
            try:
                # Parse voice model and speaker from voice_model string
                voice_model = request.voice_model
                speaker_id = request.speaker_id
                
                # Handle VCTK format: "model|speaker"
                if voice_model and "|" in voice_model:
                    model_parts = voice_model.split("|")
                    voice_model = model_parts[0]
                    speaker_id = model_parts[1] if len(model_parts) > 1 else speaker_id
                
                # Generate TTS audio
                loop = asyncio.get_event_loop()
                audio_data, audio_format = await loop.run_in_executor(
                    executor,
                    generate_tts_sync,
                    response_text,
                    voice_model,
                    speaker_id
                )
            except Exception as tts_error:
                print(f"TTS Error: {tts_error}")
        
        return ChatResponse(
            response=response_text,
            agent=agent_name,
            model=model_name,
            audio=audio_data,
            audioformat=audio_format,
            mode=request.mode
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
        
        model = get_whisper_model()
        if not model:
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
            segments, info = model.transcribe(
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
        
        # Parse voice model and speaker
        voice_model = request.voice_model
        speaker_id = request.speaker_id
        
        # Handle VCTK format: "model|speaker"
        if voice_model and "|" in voice_model:
            model_parts = voice_model.split("|")
            voice_model = model_parts[0]
            speaker_id = model_parts[1] if len(model_parts) > 1 else speaker_id
        
        loop = asyncio.get_event_loop()
        audio_data, audio_format = await loop.run_in_executor(
            executor, 
            generate_tts_sync, 
            text,
            voice_model,
            speaker_id
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
                "privacy": "High - Speech local, API calls logged + PII redacted"
            },
            "cloud": {
                "description": "Cloud LLM + Local Speech + Logging",
                "llm": "OpenAI GPT-4",
                "privacy": "Medium - Speech local, API calls logged"
            }
        },
        "local_services": {
            "coqui_tts": {
                "available": COQUI_AVAILABLE,
                "loaded": tts_model is not None,
                "cached_models": len(tts_model_cache),
                "model": COQUI_TTS_MODEL
            },
            "faster_whisper": {
                "available": FASTER_WHISPER_AVAILABLE,
                "loaded": whisper_model is not None,
                "model": WHISPER_MODEL,
                "device": WHISPER_DEVICE
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
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-vl:7b-instruct")
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
async def start_ollama_model():
    print("📡 Received LLM start request...")

    if not _ollama_running():
        print("🚀 Attempting to start Ollama server...")
        if not _start_ollama_server():
            return {"status": "error", "error": "Failed to start Ollama server. Start it manually with 'ollama serve'."}

    print("⏳ Waiting for Ollama to be ready...")
    time.sleep(2)

    try:
        model = OLLAMA_MODEL
        print(f"🔥 Warming up {model} ...")
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": "hi",
                "stream": False,
                "keep_alive": "10m"
            },
            timeout=120
        )
        if response.status_code == 200:
            print("✅ Model warmed up successfully")
            return {"status": "started", "model": model, "keep_alive": "10m"}
        else:
            msg = f"Model warm-up failed with status {response.status_code}: {response.text}"
            print(f"❌ {msg}")
            return {"status": "error", "error": msg}
    except requests.exceptions.ConnectionError:
        msg = "Ollama server is not running. Start it in another terminal: 'ollama serve'."
        print(f"❌ {msg}")
        return {"status": "error", "error": msg}
    except Exception as e:
        print(f"❌ Error warming up model: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/llm/off")
async def stop_ollama_model():
    global ollama_process
    try:
        try:
            requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": "hi", "keep_alive": "0s"},
                timeout=5
            )
        except:
            pass

        if ollama_process:
            print(f"🛑 Stopping Ollama server (PID {ollama_process.pid})...")
            try:
                if hasattr(ollama_process, 'terminate'):
                    ollama_process.terminate()
                try:
                    ollama_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    ollama_process.kill()
            finally:
                ollama_process = None
                print("✅ Ollama server stopped")

        return {"status": "stopped", "note": "Ollama server stopped"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/llm/status")
async def status_ollama_model():
    """Get detailed LLM/Ollama status"""
    try:
        server_running = _ollama_running()
        model_available = False
        model_loaded = False
        
        if server_running:
            try:
                # Check if model is available
                response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_available = any(m.get("name", "") == OLLAMA_MODEL for m in models)
                
                # Check if model is currently loaded (warm)
                try:
                    ps_response = requests.get(f"{OLLAMA_HOST}/api/ps", timeout=2)
                    if ps_response.status_code == 200:
                        running_models = ps_response.json().get("models", [])
                        model_loaded = any(m.get("name", "") == OLLAMA_MODEL for m in running_models)
                except:
                    pass
                    
            except Exception as e:
                print(f"Error checking model status: {e}")
        
        return {
            "enabled": server_running and model_available,
            "server_running": server_running,
            "model_available": model_available,
            "model_loaded": model_loaded,
            "model": OLLAMA_MODEL
        }
    except Exception as e:
        print(f"Error in llm/status: {e}")
        return {
            "enabled": False,
            "server_running": False,
            "model_available": False,
            "model_loaded": False,
            "model": OLLAMA_MODEL
        }
if ORION_MODE == "strict":
    print("🚨 STRICT MODE: Ensuring Ollama server is running...")
    _start_ollama_server()
if __name__ == "__main__":
    import uvicorn
    import os

    host = os.getenv("ORION_HOST", "0.0.0.0")
    port = int(os.getenv("ORION_PORT", 9000))

    print(f"🚀 Orion server starting at http://{host}:{port}")
    uvicorn.run("server.main:app", host=host, port=port, reload=False)

@app.get("/api/agents/status")
async def get_agent_status():
    """Get status of all agents and which one is currently active"""
    try:
        registry = get_agent_registry()
        return registry.status()
    except Exception as e:
        print(f"Error getting agent status: {e}")
        return {"error": str(e)}


# ============================================================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================================================

# Initialize session manager
session_manager = get_session_manager()

# Request Models for Sessions
class SessionCreateRequest(BaseModel):
    title: Optional[str] = "New Chat"

class SessionUpdateRequest(BaseModel):
    title: Optional[str] = None

class MessageAddRequest(BaseModel):
    role: str
    content: str
    agent: Optional[str] = None
    model: Optional[str] = None


@app.post("/api/sessions")
async def create_session(request: SessionCreateRequest):
    """Create a new chat session"""
    try:
        session = session_manager.create_session(title=request.title)
        return session
    except Exception as e:
        print(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions(limit: int = 50):
    """List all sessions, sorted by most recent"""
    try:
        sessions = session_manager.list_sessions(limit=limit)
        return {"sessions": sessions}
    except Exception as e:
        print(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session with all messages"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, request: SessionUpdateRequest):
    """Update session (rename, update metadata)"""
    try:
        session = session_manager.update_session(
            session_id=session_id,
            title=request.title
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        success = session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "deleted", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/{session_id}/messages")
async def add_message_to_session(session_id: str, message: MessageAddRequest):
    """Add a message to a session"""
    try:
        msg = Message(
            role=message.role,
            content=message.content,
            timestamp=datetime.now().isoformat(),
            agent=message.agent,
            model=message.model
        )
        session = session_manager.add_message(session_id, msg)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding message to session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sessions/{session_id}/messages")
async def clear_session_messages(session_id: str):
    """Clear all messages from a session"""
    try:
        session = session_manager.clear_messages(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error clearing messages from session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SETTINGS MANAGEMENT ENDPOINTS
# ============================================================================

SETTINGS_FILE = "data/settings.json"

# Request Model for Settings
class SettingsRequest(BaseModel):
    theme: Optional[str] = None  # 'dark', 'light', 'auto'
    language: Optional[str] = None  # 'en', 'es', etc.
    enable_sounds: Optional[bool] = None
    enable_notifications: Optional[bool] = None
    auto_play_tts: Optional[bool] = None
    default_model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    voiceInput: Optional[bool] = None
    voiceOutput: Optional[bool] = None
    voiceSpeed: Optional[float] = None
    voiceType: Optional[str] = None


def load_settings() -> dict:
    """Load settings from file"""
    # Default settings
    defaults = {
        "theme": "dark",
        "language": "en",
        "enable_sounds": True,
        "enable_notifications": True,
        "auto_play_tts": False,
        "default_model": "qwen2.5:1.5b",
        "temperature": 0.7,
        "max_tokens": 2048,
        "voiceInput": True,
        "voiceOutput": False,
        "voiceSpeed": 1.0,
        "voiceType": "tts_models/en/jenny/jenny"
    }
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                # Merge saved settings with defaults (saved takes precedence)
                defaults.update(saved)
                return defaults
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    return defaults


def save_settings(settings: dict) -> None:
    """Save settings to file"""
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


@app.get("/api/settings")
async def get_settings():
    """Get current user settings"""
    try:
        return load_settings()
    except Exception as e:
        print(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/settings")
async def update_settings(request: SettingsRequest):
    """Update user settings (partial update)"""
    try:
        # Load current settings
        current = load_settings()
        
        # Apply updates (only non-None values)
        updates = request.dict(exclude_unset=True)
        print(f"[SETTINGS] Received updates: {updates}")
        current.update(updates)
        print(f"[SETTINGS] Merged settings: {current}")
        
        # Save
        save_settings(current)
        
        return current
    except Exception as e:
        print(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/settings/reset")
async def reset_settings():
    """Reset settings to defaults"""
    try:
        defaults = {
            "theme": "dark",
            "language": "en",
            "notifications": True,
            "soundEffects": True,
            "enable_sounds": True,
            "enable_notifications": True,
            "auto_play_tts": False,
            "default_model": "qwen2.5:1.5b",
            "temperature": 0.7,
            "max_tokens": 2048,
            "fontSize": 14,
            "compactMode": False,
            "voiceInput": True,
            "voiceOutput": False,
            "voiceSpeed": 1.0,
            "voiceType": "tts_models/en/jenny/jenny",
            "privacyMode": False,
            "saveHistory": True
        }
        save_settings(defaults)
        return defaults
    except Exception as e:
        print(f"Error resetting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))