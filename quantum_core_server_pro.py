# -*- coding: utf-8 -*-
"""
Quantum Core Server Pro — FULL (Render + Replit compatible)
- Flask + Flask-SocketIO realtime support (eventlet)
- Background runner updates 40 layers, aggregates Tầng 0 (total)
- Auto-load per-layer overrides from ./core/layer_XX.py (run_layer())
- Endpoints: /, /health, /total_energy, /layer_values, /sync_dashboards, /admin/reload_core
- Admin friendly, ready to run on Render (render.yaml) or Replit (.replit)
"""

import os, time, random, threading, importlib.util, json
from datetime import datetime
from typing import Dict, Any, Callable
from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO

# Config
NUM_LAYERS = 40
RUN_INTERVAL_SECONDS = int(os.environ.get("RUN_INTERVAL_SECONDS", "6"))
PORT = int(os.environ.get("PORT", "8080"))

# Nice colored logging (works in terminals that support ANSI)
RESET = "\033[0m"
GREEN = "\033[0m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"

def log_info(msg): print(f"{CYAN}{datetime.utcnow().isoformat()} [INFO] {msg}{RESET}")
def log_ok(msg):   print(f"{GREEN}{datetime.utcnow().isoformat()} [OK] {msg}{RESET}")
def log_warn(msg): print(f"{YELLOW}{datetime.utcnow().isoformat()} [WARN] {msg}{RESET}")
def log_err(msg):  print(f"{RED}{datetime.utcnow().isoformat()} [ERR] {msg}{RESET}")

# Layer metadata and defaults (index 0 is total)
LAYER_META = [{"name":"Tầng 0 - Total Field","emoji":"🌐"}]
DEFAULT_NAMES = [('Quantum Field Stabilizer', '🔧'), ('Quantum Dao Conscious Core', '🕊️'), ('Quantum Alignment', '🔗'), ('Quantum Resonance Matrix', '🎵'), ('Quantum Energy Harmonics', '⚡'), ('Quantum Spirit Anchor', '🌀'), ('Quantum Genesis Engine', '🧬'), ('Quantum Light Bridge', '🌉'), ('Quantum Ether Conduit', '🔮'), ('Quantum Body Matrix', '🔷'), ('Quantum Harmonic Synchronizer', '🎚️'), ('Quantum Memory Evolver', '🧠'), ('Quantum Mind Gateway', '🔑'), ('Quantum Heart Field', '❤️'), ('Quantum Thought Pattern', '💭'), ('Quantum Time Bridge', '⏳'), ('Quantum Symbolic Field', '🔵'), ('Quantum Perception Gate', '👁️'), ('Quantum Morphic Fabric', '🧵'), ('Quantum Creative Engine', '🎨'), ('Quantum Dao Reflection', '🪞'), ('Quantum Dimensional Pulse', '📡'), ('Quantum Infinity Loop', '♾️'), ('Quantum Field Equilibrium', '⚖️'), ('Quantum Energy Harmonics II', '🔆'), ('Quantum Resonance Stabilizer', '🏗️'), ('Quantum Spatial Resonator', '🏛️'), ('Quantum Kamic Resonance', '🌀'), ('Quantum Omni Conscious Node', '🌐'), ('Quantum Reality Bridge', '🪄'), ('Quantum Light Bridge II', '🌟'), ('Quantum Cosmic Harmonics', '🌌'), ('Quantum Ascension Gate', '\U0001f6dc'), ('Quantum Harmonic Sphere', '🔵'), ('Quantum Akashic Field', '📚'), ('Quantum Causal Continuum', '🔁'), ('Quantum Bio Sync', '🧩'), ('Quantum Harmonic Engine', '⚙️'), ('Quantum Anchor Grid', '🧭')]

for i,(n,e) in enumerate(DEFAULT_NAMES, start=1):
    LAYER_META.append({"name":f"Tầng {i} - {n}","emoji":e})

# Runtime state
layer_state: Dict[int, Dict[str, Any]] = {}
for i in range(0, NUM_LAYERS+1):
    meta = LAYER_META[i] if i < len(LAYER_META) else {"name":f"Tầng {i}","emoji":"⚪"}
    layer_state[i] = {"layer":i, "name": meta.get("name"), "emoji": meta.get("emoji"), "energy": None, "resonance": None, "state": "unknown", "last_update": None}

runners: Dict[int, Callable[[], Dict[str,Any]]] = {}
lock = threading.Lock()

def load_layer_module(i: int):
    path = os.path.join("core", f"layer_{i:02d}.py")
    if os.path.exists(path):
        try:
            spec = importlib.util.spec_from_file_location(f"core.layer_{i:02d}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "run_layer") and callable(module.run_layer):
                log_info(f"🔁 Loaded override for layer {i} from {path}")
                return module.run_layer
            else:
                log_warn(f"Module {path} missing run_layer()")
        except Exception as e:
            log_err(f"Error loading {path}: {e}")
    return None

def make_default_runner(i: int):
    def run():
        energy = round(random.uniform(4.70, 4.90), 4)
        resonance = round(random.uniform(0.88, 0.99), 4)
        if resonance > 0.95:
            state = "Harmonized"
        elif resonance > 0.90:
            state = "Stable"
        elif resonance > 0.86:
            state = "Resonant"
        else:
            state = "Fluctuating"
        return {"layer": i, "energy": energy, "resonance": resonance, "state": state, "timestamp": datetime.utcnow().isoformat()}
    return run

# Build runners (prefer external modules)
for idx in range(1, NUM_LAYERS+1):
    r = load_layer_module(idx)
    runners[idx] = r if r else make_default_runner(idx)

def update_once():
    for idx in range(1, NUM_LAYERS+1):
        try:
            runner = runners.get(idx) or make_default_runner(idx)
            result = runner()
            with lock:
                layer_state[idx].update({"energy": result.get("energy"), "resonance": result.get("resonance"), "state": result.get("state"), "last_update": result.get("timestamp")})
            emoji = layer_state[idx].get("emoji","⚪")
            name = layer_state[idx].get("name", f"Tầng {idx}")
            energy = layer_state[idx]["energy"]
            resonance = layer_state[idx]["resonance"]
            state = layer_state[idx]["state"]
            color = GREEN if state in ("Harmonized","Stable") else YELLOW if state in ("Resonant",) else CYAN
            print(f"{color}{datetime.utcnow().isoformat()} {emoji} {name} | ⚡ {energy} | 🔊 {resonance} | {state}{RESET}")
        except Exception as e:
            log_err(f"Layer {idx} update failed: {e}")

def background_loop():
    log_info("🚀 Background runner started (FULL pack)")
    while True:
        try:
            update_once()
            with lock:
                energies = [v["energy"] for k,v in layer_state.items() if k!=0 and v["energy"] is not None]
                if energies:
                    avg = round(sum(energies)/len(energies), 4)
                    layer_state[0].update({"energy": avg, "state": "Aggregated", "last_update": datetime.utcnow().isoformat()})
                    log_ok(f"🛰️ Total energy (Tầng 0) updated: {avg}")
            time.sleep(RUN_INTERVAL_SECONDS)
        except Exception as e:
            log_err(f"Background loop error: {e}")
            time.sleep(5)

# Start background runner thread
threading.Thread(target=background_loop, daemon=True).start()

# Flask + SocketIO
app = Flask(__name__, static_folder="static", static_url_path="/static")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

@app.route("/")
def index():
    return jsonify({"message":"Quantum Core Server Pro — FULL", "timestamp": datetime.utcnow().isoformat()})

@app.route("/health")
def health():
    return jsonify({"status":"ok", "timestamp": datetime.utcnow().isoformat()})

@app.route("/total_energy")
def total_energy():
    with lock:
        return jsonify({"layer":0, "name": layer_state[0]["name"], "energy": layer_state[0]["energy"], "last_update": layer_state[0]["last_update"]})

@app.route("/layer_values")
def layer_values():
    with lock:
        return jsonify(layer_state)

@app.route("/sync_dashboards", methods=["POST"])
def sync_dashboards():
    payload = request.get_json(silent=True) or {}
    log_info(f"🔄 Dashboard sync request - keys: {list(payload.keys())}")
    try:
        socketio.emit("quantum_sync", payload, broadcast=True)
    except Exception as e:
        log_warn(f"Socket emit failed: {e}")
    return jsonify({"status":"ok","received": payload})

@app.route("/admin/reload_core", methods=["POST"])
def admin_reload_core():
    reloaded = []
    for idx in range(1, NUM_LAYERS+1):
        r = load_layer_module(idx)
        if r:
            runners[idx] = r
            reloaded.append(idx)
    log_info(f"🔁 Reloaded modules: {reloaded}")
    return jsonify({"reloaded": reloaded})

# Socket handlers
@socketio.on("connect")
def on_connect():
    log_info("Socket client connected")
    with lock:
        socketio.emit("quantum_snapshot", layer_state, room=request.sid)

@socketio.on("disconnect")
def on_disconnect():
    log_info("Socket client disconnected")

if __name__ == "__main__":
    if os.path.isdir("core"):
        files = [f for f in os.listdir("core") if f.endswith(".py")]
        log_info(f"Detected core modules: {files}")
    log_info(f"Starting SocketIO server on 0.0.0.0:{PORT} (eventlet)")
    socketio.run(app, host="0.0.0.0", port=PORT, debug=False)
