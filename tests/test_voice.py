# test_simple_voices.py
from TTS.api import TTS
import tempfile
import os
from playsound import playsound

print("Testing simple TTS voices (no espeak required)...")

# Test different English voices that don't need espeak
test_text = "Hello, my name is Orion. I am your AI assistant. How do you like this voice?"

# Simple models that work without espeak
simple_voices = [
    ("LJSpeech Tacotron2", "tts_models/en/ljspeech/tacotron2-DDC"),  # Current - Female, clear
    ("LJSpeech Glow-TTS", "tts_models/en/ljspeech/glow-tts"),       # Female, different tone  
    ("LJSpeech Speedy", "tts_models/en/ljspeech/speedy-speech"),    # Female, faster
    ("Jenny", "tts_models/en/jenny/jenny"),                         # Female, different voice
]

for i, (name, model_name) in enumerate(simple_voices, 1):
    print(f"\n{i}. Testing: {name}")
    print(f"   Model: {model_name}")
    
    try:
        print("   Loading model...")
        tts = TTS(model_name=model_name, progress_bar=False)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            wav_path = tmp_file.name
        
        print("   Generating speech...")
        tts.tts_to_file(text=test_text, file_path=wav_path)
        
        input(f"   Press Enter to play {name}...")
        playsound(wav_path)
        
        # Clean up
        os.remove(wav_path)
        
        choice = input("   Like this voice? (y/n/s=skip to next, q=quit): ").lower()
        if choice == 'y':
            print(f"\n✅ You chose: {name}")
            print(f"Add this to your .env file:")
            print(f"COQUI_TTS_MODEL={model_name}")
            print(f"COQUI_TTS_SPEAKER=")
            break
        elif choice == 'q':
            break
            
    except Exception as e:
        print(f"   ❌ Error with {name}: {e}")
        continue

print("\nVoice testing complete!")