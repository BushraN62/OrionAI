# server/main_optimized.py - Performance Optimized Version
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

# === LOCAL AI IMPORTS ===
try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

try:
    import torch
    import soundfile as sf
    import numpy as np
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False

from dotenv import load_dotenv
load_dotenv(override=True)

ORION_MODE = os.getenv("ORION_MODE", "hybrid").lower()

# === LAZY INITIALIZATION FOR MODELS (Faster Startup) ===
whisper_model = None
tts_model = None
tts_model_cache = {}  # Cache for multiple TTS models

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cuda" if AUDIO_LIBS_AVAILABLE and hasattr(torch, 'cuda') and torch.cuda.is_available() else "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "float16" if WHISPER_DEVICE == "cuda" else "float32")
COQUI_TTS_MODEL = os.getenv("COQUI_TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")

def get_whisper_model():
    """Lazy load Whisper model on first use - reduces startup time by ~3-5 seconds"""
    global whisper_model
    if whisper_model is None and FASTER_WHISPER_AVAILABLE:
        try:
            print(f"[STT] Loading Faster Whisper '{WHISPER_MODEL}' on {WHISPER_DEVICE}...")
            whisper_model = WhisperModel(
                WHISPER_MODEL, 
                device=WHISPER_DEVICE, 
                compute_type=WHISPER_COMPUTE_TYPE
            )
            print("[OK] Faster Whisper loaded")
        except Exception as e:
            print(f"[WARN] Failed to load Faster Whisper: {e}")
    return whisper_model

def get_tts_model(model_name: str = None):
    """Lazy load TTS model with caching - reduces latency for different voices"""
    global tts_model, tts_model_cache
    model_name = model_name or COQUI_TTS_MODEL
    
    # Return cached model if available (instant)
    if model_name in tts_model_cache:
        return tts_model_cache[model_name]
    
    # Load default model on first call
    if tts_model is None and model_name == COQUI_TTS_MODEL and COQUI_AVAILABLE:
        try:
            print(f"[TTS] Loading Coqui TTS '{COQUI_TTS_MODEL}'...")
            tts_model = TTS(model_name=COQUI_TTS_MODEL, progress_bar=False)
            tts_model_cache[COQUI_TTS_MODEL] = tts_model
            print("[OK] Coqui TTS loaded")
            return tts_model
        except Exception as e:
            print(f"[WARN] Failed to load Coqui TTS: {e}")
            return None
    
    # Load custom model if requested
    if model_name != COQUI_TTS_MODEL and COQUI_AVAILABLE:
        try:
            print(f"[TTS] Loading model '{model_name}'...")
            model = TTS(model_name=model_name, progress_bar=False)
            tts_model_cache[model_name] = model
            return model
        except Exception as e:
            print(f"[WARN] Failed to load TTS model '{model_name}': {e}")
            return None
    
    return tts_model

app = FastAPI(title="Orion AI Assistant - Optimized")

from server.routers.zephyr_ops import router as zephyr_router
app.include_router(zephyr_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for TTS generation (optimized worker count)
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
    agent: Optional[str] = "conversational"
    model: Optional[str] = "qwen2.5:1.5b"
    audio: Optional[str] = None
    audioformat: Optional[str] = None
    mode: str = "strict"
    
class MemoryRequest(BaseModel):
    memory: str
    
class PersonalityRequest(BaseModel):
    humor: float = 0.5
    verbosity: float = 0.5
    formality: float = 0.5
    creativity: float = 0.6
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
            content={"error": f"UI file not found at {ui_path}."}
        )
    return FileResponse(ui_path)

@app.get("/health")
async def health_check():
    """Health check with lazy model checking"""
    llm_healthy = True
    
    if ORION_MODE == "strict":
        llm_healthy = _ollama_running()
    
    return {
        "status": "healthy" if llm_healthy else "degraded",
        "service": "orion-optimized",
        "mode": ORION_MODE,
        "llm_available": llm_healthy,
        "ai_services": {
            "llm": f"Ollama" if ORION_MODE == "strict" else "OpenAI GPT-4",
            "tts": "Lazy-loaded" if COQUI_AVAILABLE else "None",
            "stt": "Lazy-loaded" if FASTER_WHISPER_AVAILABLE else "None",
        }
    }

def generate_tts_sync(text: str, voice_model: Optional[str] = None, speaker_id: Optional[str] = None) -> tuple:
    """Optimized TTS generation with model caching"""
    if not AUDIO_LIBS_AVAILABLE or not text.strip():
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
    """Main chat endpoint with multi-agent support"""
    try:
        memory = OrionMemory()
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

@app.post("/api/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert speech to text using Faster Whisper (lazy-loaded)"""
    try:
        print(f"Received audio: {audio.filename}")
        
        model = get_whisper_model()
        if not model:
            return {"transcript": "", "status": "error", "error": "Faster Whisper not available"}
        
        content = await audio.read()
        
        # Determine file extension
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
            print("Using Faster Whisper...")
            
            final_file = tmp_file_path
            converted_file = None
            
            if suffix in [".webm", ".mp4", ".ogg"]:
                try:
                    from pydub import AudioSegment
                    print(f"Converting {suffix} to WAV...")
                    audio_segment = AudioSegment.from_file(tmp_file_path)
                    converted_file = tmp_file_path.replace(suffix, ".wav")
                    audio_segment.export(converted_file, format="wav", parameters=["-ac", "1", "-ar", "16000"])
                    final_file = converted_file
                except Exception as e:
                    print(f"Conversion failed, using original: {e}")
            
            segments, info = model.transcribe(
                final_file, 
                beam_size=5,
                language="en",
                task="transcribe"
            )
            
            text = " ".join([segment.text for segment in segments]).strip()
            
            if len(text) >= 2:
                return {"transcript": text, "status": "success", "service": "faster-whisper"}
            else:
                return {"transcript": "", "status": "error", "error": "No speech detected"}
                
        finally:
            try:
                os.remove(tmp_file_path)
                if converted_file and os.path.exists(converted_file):
                    os.remove(converted_file)
            except:
                pass
                
    except Exception as e:
        print(f"STT Error: {e}")
        return {"transcript": "", "status": "error", "error": str(e)}

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using Coqui TTS (lazy-loaded)"""
    try:
        if not request.text:
            return {"status": "error", "error": "No text provided"}
        
        voice_model = request.voice_model
        speaker_id = request.speaker_id
        
        if voice_model and "|" in voice_model:
            model_parts = voice_model.split("|")
            voice_model = model_parts[0]
            speaker_id = model_parts[1] if len(model_parts) > 1 else speaker_id
        
        loop = asyncio.get_event_loop()
        audio_data, audio_format = await loop.run_in_executor(
            executor, 
            generate_tts_sync, 
            request.text,
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
    """Get status of AI services"""
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
# Note: Ollama runs as independent service, not tracked as subprocess

def _ollama_running() -> bool:
    """Check if Ollama server is running"""
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        if r.status_code == 200:
            return True
    except:
        pass
    return False

def _start_ollama_server(wait_secs: float = 30.0):
    """Start Ollama server as independent background service"""
    if _ollama_running():
        print("✅ Ollama server is already running")
        return True
    
    try:
        print("🚀 Starting Ollama server as independent service...")
        
        if os.name == 'nt':  # Windows
            subprocess.Popen(
                ['cmd', '/c', 'start', '/B', 'ollama', 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                shell=False
            )
        else:  # Unix/Linux/Mac
            subprocess.Popen(
                ['nohup', 'ollama', 'serve', '&'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                shell=True
            )
        
        print("   Ollama started as independent background service")
        
        t0 = time.time()
        while time.time() - t0 < wait_secs:
            if _ollama_running():
                print("✅ Ollama server is ready")
                return True
            time.sleep(0.5)
        
        print("⚠️ Ollama may still be starting...")
        return False
    except Exception as e:
        print(f"❌ Failed to start Ollama: {e}")
        print("   Please start manually: 'ollama serve'")
        return False

@app.get("/llm/on")
async def start_ollama_model():
    if not _ollama_running():
        if not _start_ollama_server():
            return {"status": "error", "error": "Failed to start Ollama server"}

    time.sleep(2)

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": "hi",
                "stream": False,
                "keep_alive": "10m"
            },
            timeout=120
        )
        if response.status_code == 200:
            return {"status": "started", "model": OLLAMA_MODEL}
        else:
            return {"status": "error", "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/llm/off")
async def stop_ollama_model():
    """Unload model from memory but keep Ollama server running"""
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": "hi", "keep_alive": "0s"},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Model {OLLAMA_MODEL} unloaded from memory")
            return {
                "status": "unloaded",
                "note": "Model unloaded from memory. Ollama server still running."
            }
        else:
            return {
                "status": "error",
                "error": f"Failed to unload model: {response.status_code}"
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/llm/status")
async def status_ollama_model():
    """Get detailed LLM/Ollama status"""
    try:
        server_running = _ollama_running()
        return {
            "enabled": server_running,
            "server_running": server_running,
            "model": OLLAMA_MODEL
        }
    except Exception as e:
        return {
            "enabled": False,
            "server_running": False,
            "model": OLLAMA_MODEL
        }

@app.get("/api/agents/status")
async def get_agent_status():
    """Get status of all agents"""
    try:
        registry = get_agent_registry()
        return registry.status()
    except Exception as e:
        return {"error": str(e)}

# Session Management
session_manager = get_session_manager()

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
    try:
        session = session_manager.create_session(title=request.title)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
async def list_sessions(limit: int = 50):
    try:
        sessions = session_manager.list_sessions(limit=limit)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, request: SessionUpdateRequest):
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
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    try:
        success = session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "deleted", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/messages")
async def add_message_to_session(session_id: str, message: MessageAddRequest):
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
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/{session_id}/messages")
async def clear_session_messages(session_id: str):
    try:
        session = session_manager.clear_messages(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Settings Management
SETTINGS_FILE = "data/settings.json"

class SettingsRequest(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
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
    """Load settings from file with defaults"""
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
                defaults.update(saved)
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
    try:
        return load_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/settings")
async def update_settings(request: SettingsRequest):
    try:
        current = load_settings()
        updates = request.dict(exclude_unset=True)
        current.update(updates)
        save_settings(current)
        return current
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/settings/reset")
async def reset_settings():
    try:
        defaults = load_settings()  # Gets defaults
        save_settings(defaults)
        return defaults
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if ORION_MODE == "strict":
    print("🚨 STRICT MODE: Ensuring Ollama server is running...")
    _start_ollama_server()

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("ORION_HOST", "0.0.0.0")
    port = int(os.getenv("ORION_PORT", 9000))
    print(f"🚀 Orion Optimized server starting at http://{host}:{port}")
    uvicorn.run("server.main_optimized:app", host=host, port=port, reload=False)
