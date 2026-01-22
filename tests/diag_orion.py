# diag_orion.py — offline, stdlib-only
import os, re

ROOT = os.path.dirname(os.path.dirname(__file__))  # repo root
files = [
    "orion/app/cli.py",
    "orion/app/orchestrator.py",
    "orion/app/memory/store.py",
]
code = ""
for f in files:
    p = os.path.join(ROOT, f)
    try:
        code += f"\n# --- {f} ---\n" + open(p, "r", encoding="utf-8", errors="ignore").read()
    except Exception as e:
        code += f"\n# --- {f}: read error {e} ---\n"

def has(pattern): return re.search(pattern, code, re.I|re.M|re.S) is not None

signals = {
  "stt_whisper": has(r"whisper|openai.*audio|speech_recognition"),
  "stt_vosk": has(r"vosk"),
  "vad": has(r"webrtcvad|voice.?activity"),
  "tts_eleven": has(r"elevenlabs"),
  "tts_coqui": has(r"coqui|tts\.models"),
  "llm_openai": has(r"openai|gpt-"),
  "prompt_comp": has(r"(system|persona).*(prompt)|compose_.*prompt|build_.*prompt"),
  "personality_sliders": has(r"humor|verbosity|formality|sarcasm|initiative|creativity"),
  "profiles": has(r"user_name_legal|user_name_preferred"),  # simple proxy
  "mode_voice_text": has(r"(switch|toggle).*(voice|text)|say this reply out loud|start listening|i.?ll type now"),
  "memory_json": has(r"json.dump|json.loads|memory\.json"),
  "memory_sqlite": has(r"sqlite3|sqlcipher"),
  "vector_store": has(r"faiss|chroma|sentence[-_ ]?transformers|MiniLM"),
  "memory_editor": has(r"forget my name|export memory|purge session"),
  "ledger": has(r"(log|ledger).*(api|request|token)|requests.*hooks|logging"),
  "redaction": has(r"redact|mask|pii|sanitize"),
  "skills": has(r"def get_weather|skill"),
  "calendar": has(r"calendar|googleapiclient"),
  "web_search": has(r"serpapi|bing|duckduckgo|requests.get\\(.+search)"),
  "ui": has(r"fastapi|flask|streamlit|pyqt|electron"),
  "scheduler": has(r"apscheduler|schedule\\.every|cron"),
  "explainability": has(r"why|explain.*reason|context preview"),
  "focus_mode": has(r"focus mode|do not disturb|dnd"),
  "wake_word": has(r"porcupine|wake word"),
  "tests": True,
}

weights = {
  "Core I/O loop": 20,
  "Orchestrator & prompt": 10,
  "Personality": 10,
  "Interaction modes": 10,
  "Memory system": 15,
  "Privacy & ledger": 10,
  "Skills": 5,
  "UI/UX": 5,
  "Explainability/wellbeing": 5,
  "Offline readiness": 5,
  "Routines & wake word": 5,
}

score = 0
details = []

io_ok = sum(int(signals[k]) for k in ["stt_whisper","tts_eleven","llm_openai","vad"])
score += weights["Core I/O loop"] * (0.25 * io_ok); details.append(("Core I/O loop", io_ok, 4))
score += weights["Orchestrator & prompt"] * (1 if signals["prompt_comp"] else 0); details.append(("Orchestrator & prompt", int(signals["prompt_comp"]), 1))
p_hits = int(signals["personality_sliders"]) + int(signals["profiles"]); score += weights["Personality"] * (p_hits/2); details.append(("Personality", p_hits, 2))
score += weights["Interaction modes"] * (1 if signals["mode_voice_text"] else 0); details.append(("Interaction modes", int(signals["mode_voice_text"]), 1))
mem_hits = int(signals["memory_json"] or signals["memory_sqlite"]) + int(signals["vector_store"]) + int(signals["memory_editor"])
score += weights["Memory system"] * (mem_hits/3); details.append(("Memory system", mem_hits, 3))
priv_hits = int(signals["ledger"]) + int(signals["redaction"]); score += weights["Privacy & ledger"] * (priv_hits/2); details.append(("Privacy & ledger", priv_hits, 2))
skills_hits = int(signals["skills"] or signals["calendar"] or signals["web_search"]); score += weights["Skills"] * skills_hits; details.append(("Skills", skills_hits, 1))
score += weights["UI/UX"] * (1 if signals["ui"] else 0); details.append(("UI/UX", int(signals["ui"]), 1))
exp_hits = int(signals["explainability"]) + int(signals["focus_mode"]); score += weights["Explainability/wellbeing"] * (exp_hits/2); details.append(("Explainability/wellbeing", exp_hits, 2))
off_hits = int(signals["stt_vosk"]) + int(signals["tts_coqui"]); score += weights["Offline readiness"] * (off_hits/2); details.append(("Offline readiness", off_hits, 2))
rw_hits = int(signals["scheduler"]) + int(signals["wake_word"]); score += weights["Routines & wake word"] * (rw_hits/2); details.append(("Routines & wake word", rw_hits, 2))

print("== Orion Progress Estimate ==")
for k,(name,hit,need) in enumerate(details,1):
    print(f"{k:02}. {name:<26} {hit}/{need}")
print(f"\nApprox overall progress: {round(score):d}%")
print("\nSignals:"); [print(f"- {k}: {'yes' if v else 'no'}") for k,v in signals.items()]
print("\nSourced files:", ", ".join(files))
