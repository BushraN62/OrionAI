# test_vctk_speakers.py
from TTS.api import TTS
import tempfile
import os
from playsound import playsound

# VCTK has many different speakers
tts = TTS("tts_models/en/vctk/vits")
test_text = "Hello, I'm Orion, your personal AI assistant."

# Popular VCTK speaker IDs (different accents/genders)
speakers = [
    "p225",  # Female, English
    "p226",  # Male, English  
    "p227",  # Male, English
    "p228",  # Female, English
    "p229",  # Female, English
    "p230",  # Female, English
    "p231",  # Female, English
    "p232",  # Male, English
    "p233",  # Female, English
    "p236",  # Female, English
    "p237",  # Male, English
    "p238",  # Female, English
    "p239",  # Female, English
    "p240",  # Female, English
    "p241",  # Male, English
]

for speaker in speakers:
    print(f"\nTesting speaker: {speaker}")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            wav_path = tmp_file.name
        
        tts.tts_to_file(text=test_text, speaker=speaker, file_path=wav_path)
        
        input(f"Press Enter to play speaker {speaker}...")
        playsound(wav_path)
        
        os.remove(wav_path)
        
        choice = input(f"Like speaker {speaker}? (y/n/q): ").lower()
        if choice == 'y':
            print(f"\nYou chose speaker: {speaker}")
            print("Add these to your .env file:")
            print("COQUI_TTS_MODEL=tts_models/en/vctk/vits")
            print(f"COQUI_TTS_SPEAKER={speaker}")
            break
        elif choice == 'q':
            break
            
    except Exception as e:
        print(f"Error with speaker {speaker}: {e}")