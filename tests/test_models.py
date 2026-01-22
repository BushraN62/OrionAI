# Create a test file: test_models.py
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing model loading...")

# Test 1: Faster Whisper
try:
    print("🎤 Testing Faster Whisper...")
    from faster_whisper import WhisperModel
    
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")  # Force CPU for testing
    WHISPER_COMPUTE_TYPE = "float32"  # Force float32 for compatibility
    
    print(f"Loading Whisper model: {WHISPER_MODEL} on {WHISPER_DEVICE}")
    whisper_model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
    print("✅ Faster Whisper loaded successfully")
except Exception as e:
    print(f"❌ Faster Whisper failed: {e}")

# Test 2: Coqui TTS
try:
    print("🗣️ Testing Coqui TTS...")
    from TTS.api import TTS
    
    COQUI_TTS_MODEL = os.getenv("COQUI_TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")
    print(f"Loading TTS model: {COQUI_TTS_MODEL}")
    tts_model = TTS(model_name=COQUI_TTS_MODEL, progress_bar=True)  # Enable progress bar
    print("✅ Coqui TTS loaded successfully")
except Exception as e:
    print(f"❌ Coqui TTS failed: {e}")

print("Model loading test complete!")