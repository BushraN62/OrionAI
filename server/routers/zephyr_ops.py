"""
server/routers/zephyr_ops.py
--------------------------------
Backend endpoints to let your team fine-tune, quantize, and test the Zephyr 7B model
on your machine via the FastAPI server (server/main.py).
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import os, json, shutil, subprocess, threading, time
from pathlib import Path
import requests, psutil  # pip install psutil
import threading, atexit

# ===== On-demand Ollama control =====
OLLAMA_HOST = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_CMD = os.getenv("OLLAMA_CMD", "ollama")  # path to ollama exe if needed
OLLAMA_IDLE_SECONDS = int(os.getenv("OLLAMA_IDLE_SECONDS", "900"))  # 15 min default

_last_activity = time.time()
_reaper_started = False
_reaper_lock = threading.Lock()

def _touch_activity():
    global _last_activity
    _last_activity = time.time()

def _ollama_running() -> bool:
    # Cheap health probe first
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        if r.status_code == 200:
            return True
    except Exception:
        pass
    # Fallback: check process table
    for p in psutil.process_iter(attrs=["name"]):
        if p.info["name"] and "ollama" in p.info["name"].lower():
            return True
    return False

def _start_ollama_if_needed(wait_secs: float = 30.0):
    if _ollama_running():
        return
    # Try to spawn ollama serve
    try:
        subprocess.Popen([OLLAMA_CMD, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Ollama: {e}")
    # Wait until health passes or timeout
    t0 = time.time()
    while time.time() - t0 < wait_secs:
        if _ollama_running():
            return
        time.sleep(0.5)
    raise HTTPException(status_code=504, detail="Ollama did not become ready in time")

def _stop_ollama():
    killed = 0
    for p in psutil.process_iter(attrs=["name", "pid"]):
        if p.info["name"] and "ollama" in p.info["name"].lower():
            try:
                psutil.Process(p.info["pid"]).terminate()
                killed += 1
            except Exception:
                pass
    return killed

def _idle_reaper():
    global _reaper_started
    with _reaper_lock:
        if _reaper_started:
            return
        _reaper_started = True
    # simple background loop
    while True:
        try:
            idle = time.time() - _last_activity
            if idle > OLLAMA_IDLE_SECONDS and _ollama_running():
                _stop_ollama()
            time.sleep(5)
        except Exception:
            time.sleep(5)

# Start the reaper thread when the module loads
threading.Thread(target=_idle_reaper, daemon=True).start()
atexit.register(_stop_ollama)  # ensure we shut it down on server exit

# =============== CONFIG ===============
DATA_ROOT = Path("data")  # relative to project root
DATASETS_DIR = DATA_ROOT / "datasets"
JOBS_DIR = DATA_ROOT / "jobs"
MODELS_DIR = DATA_ROOT / "models"
LOGS_DIR = DATA_ROOT / "logs"

for p in [DATASETS_DIR, JOBS_DIR, MODELS_DIR, LOGS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

API_TOKEN = os.getenv("ORION_TEAM_TOKEN", None)
STATE_PATH = DATA_ROOT / "ft_jobs.json"

# =============== AUTH GUARD ===============
def require_token(authorization: Optional[str] = None):
    if API_TOKEN is None:
        return True  # unsecured mode for local testing
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    return True

router = APIRouter(prefix="/zephyr", tags=["zephyr"], dependencies=[Depends(require_token)])

# =============== DATA MODELS ===============
class TrainRequest(BaseModel):
    base_model: str = "zephyr:7b-beta"
    job_name: Optional[str] = None
    train_files: List[str]
    eval_files: Optional[List[str]] = None
    epochs: int = 1
    lr: float = 2e-5
    batch_size: int = 4
    grad_accum: int = 4
    lora_r: int = 16
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    bf16: bool = True
    use_qlora: bool = True
    wandb_project: Optional[str] = None
    train_script: Optional[str] = None  # optional custom script path

class QuantizeRequest(BaseModel):
    adapter_path: str
    new_model_name: str
    qtype: str = "q4_K_M"

class InferenceRequest(BaseModel):
    model: str
    prompt: str
    temperature: float = 0.2
    top_p: float = 0.9
    max_tokens: int = 512

# =============== INTERNAL HELPERS ===============
def _load_state() -> Dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except json.JSONDecodeError:
            pass
    return {"jobs": {}}

def _save_state(state: Dict):
    STATE_PATH.write_text(json.dumps(state, indent=2))

def _job_id(prefix: str = "job"):
    return f"{prefix}_{int(time.time())}"

# =============== ENDPOINTS ===============
@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a dataset file and save it under data/datasets"""
    ds_id = f"ds_{int(time.time())}_{file.filename}"
    dest = DATASETS_DIR / ds_id
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    file.file.close()
    return {"dataset_id": ds_id, "path": str(dest)}

@router.get("/datasets")
async def list_datasets():
    """List all uploaded datasets"""
    datasets = [
        {"name": p.name, "size": p.stat().st_size, "modified": time.ctime(p.stat().st_mtime)}
        for p in DATASETS_DIR.glob("*")
    ]
    return {"datasets": datasets}

# Background worker
def _run_background(cmd: List[str], log_path: Path, job_id: str):
    state = _load_state()
    state["jobs"][job_id] = {"status": "running", "cmd": cmd, "log": str(log_path)}
    _save_state(state)

    with log_path.open("wb") as log:
        try:
            proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
            ret = proc.wait()
            status = "completed" if ret == 0 else f"failed ({ret})"
        except Exception as e:
            status = f"error: {e}"
        state = _load_state()
        state["jobs"][job_id]["status"] = status
        _save_state(state)

@router.post("/train")
async def start_train(req: TrainRequest, bg: BackgroundTasks):
    """Start a Zephyr fine-tuning job in the background."""
    job_id = req.job_name or _job_id("ft")
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{job_id}.log"

    # Resolve dataset paths
    train_paths = [str(DATASETS_DIR / f) for f in req.train_files if (DATASETS_DIR / f).exists()]
    if not train_paths:
        raise HTTPException(status_code=400, detail="No valid dataset files found")

    # Pick training script (default or custom)
    script = req.train_script or str(Path("train_zephyr.py").resolve())
    if not Path(script).exists():
        raise HTTPException(status_code=400, detail=f"Training script not found: {script}")

    cmd = [
        "python", script,
        "--base_model", req.base_model,
        "--output_dir", str(job_dir / "adapter"),
        "--train_files", *train_paths,
        "--epochs", str(req.epochs),
        "--lr", str(req.lr),
        "--batch_size", str(req.batch_size),
        "--grad_accum", str(req.grad_accum),
        "--lora_r", str(req.lora_r),
        "--lora_alpha", str(req.lora_alpha),
        "--lora_dropout", str(req.lora_dropout),
        "--bf16", str(int(req.bf16)),
        "--use_qlora", str(int(req.use_qlora)),
    ]
    if req.wandb_project:
        cmd += ["--wandb_project", req.wandb_project]

    threading.Thread(target=_run_background, args=(cmd, log_path, job_id), daemon=True).start()

    state = _load_state()
    state["jobs"][job_id] = {
        "status": "queued",
        "log": str(log_path),
        "dir": str(job_dir),
        "created": time.ctime()
    }
    _save_state(state)
    return {"job_id": job_id, "log": str(log_path)}

@router.get("/jobs")
async def list_jobs():
    """List all fine-tuning jobs"""
    return _load_state()

@router.get("/jobs/{job_id}")
async def job_status(job_id: str):
    """Get specific job status"""
    state = _load_state()
    job = state["jobs"].get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/quantize")
async def quantize(req: QuantizeRequest):
    """Create a new Ollama model using a fine-tuned adapter"""
    model_dir = MODELS_DIR / req.new_model_name.replace(":", "_")
    model_dir.mkdir(parents=True, exist_ok=True)
    modelfile = model_dir / "Modelfile"

    modelfile.write_text(f"""# Auto-generated Modelfile
FROM {os.getenv('OLLAMA_MODEL', 'zephyr:7b-beta')}
# ADAPTER ./adapter
PARAMETER temperature 0.2
PARAMETER num_ctx 8192
""")

    ap = Path(req.adapter_path)
    if not ap.exists():
        raise HTTPException(status_code=400, detail=f"Adapter path not found: {req.adapter_path}")
    shutil.copytree(ap, model_dir / "adapter", dirs_exist_ok=True)

    result = subprocess.run(["ollama", "create", req.new_model_name, "-f", str(modelfile)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Ollama create failed:\n{result.stderr}")
    return {"status": "ok", "model": req.new_model_name}

@router.post("/infer")
async def infer(req: InferenceRequest):
    _start_ollama_if_needed()   # <-- spin up if not running
    _touch_activity()
    try:
        r = requests.post(f"{OLLAMA_HOST}/api/generate", json={
            "model": req.model,
            "prompt": req.prompt,
            "options": {"temperature": req.temperature, "top_p": req.top_p},
            "stream": False,
            "keep_alive": "5m",
            "max_tokens": req.max_tokens
        }, timeout=600)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to contact Ollama: {e}")
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    _touch_activity()
    data = r.json()
    return {"response": data.get("response", ""), "total_duration": data.get("total_duration")}

