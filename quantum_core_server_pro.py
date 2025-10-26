# quantum_core_server_pro.py
# Quantum Core Server Pro - Render stable single-file
# Flask + Flask-SocketIO (threading mode) + KeepAlive ping + safe werkzeug flag

from flask import Flask, jsonify, render_template_string, request
from flask_socketio import SocketIO
import threading, time, datetime, os, sys

# Optional requests - used by keepalive ping if available
try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    _HAS_REQUESTS = False

# ---------------------------
# Flask + SocketIO init
# ---------------------------
app = Flask(__name__)
# Use threading async mode which is safest on Render
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ---------------------------
# In-memory "state" (sample)
# ---------------------------
total_energy_state = {
    "heaven_energy": 3210,
    "earth_energy": 2875,
    "human_energy": 3088,
    "last_update": str(datetime.datetime.now())
}

# ---------------------------
# KeepAlive ping (daemon thread)
# ---------------------------
# NOTE: update KEEPALIVE_URL to your real public endpoint if different
KEEPALIVE_URL = os.environ.get("KEEPALIVE_URL", "https://quantum-core-server-full.onrender.com/total_energy")

def keep_alive_loop():
    if not _HAS_REQUESTS:
        print("[KeepAlive] requests package not available. KeepAlive ping disabled.")
        return
    while True:
        try:
            r = requests.get(KEEPALIVE_URL, timeout=10)
            print(f"[KeepAlive] pinged {KEEPALIVE_URL} -> {r.status_code} at {datetime.datetime.now()}")
        except Exception as e:
            print(f"[KeepAlive] ping error: {e}")
        # Ping every 600 seconds (10 minutes)
        time.sleep(600)

t = threading.Thread(target=keep_alive_loop, daemon=True)
t.start()

# ---------------------------
# HTML template for dashboard
# ---------------------------
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Quantum Core - Total Energy</title>
  <style>
    body { background:#071019; color:#cfeeee; font-family:Consolas,monospace; }
    .wrap { width:760px; margin:40px auto; padding:20px; background:#0b1620; border-radius:8px; box-shadow:0 6px 30px rgba(0,0,0,0.6);}
    h1 { color:#7ef2d4; }
    .row { display:flex; justify-content:space-between; padding:8px 0; }
    .k { color:#9fe7ff; }
    .v { color:#ffd6a5; font-weight:bold; }
    footer { margin-top:20px; color:#6fa0a6; font-size:12px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>⚡ Quantum Core — Total Energy</h1>
    <div class="row"><div class="k">Năng lượng Thiên</div><div class="v">{{heaven}}</div></div>
    <div class="row"><div class="k">Năng lượng Địa</div><div class="v">{{earth}}</div></div>
    <div class="row"><div class="k">Năng lượng Nhân</div><div class="v">{{human}}</div></div>
    <hr/>
    <div>Cập nhật: {{t}}</div>
    <footer>API: <code>/total_energy?json=1</code> • Sync endpoint: <code>/sync_dashboards</code></footer>
  </div>
</body>
</html>
"""

# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def index():
    return "Quantum Core Server Pro is running. Use /total_energy to view dashboard."

@app.route("/total_energy", methods=["GET"])
def total_energy():
    # update last_update stamp
    total_energy_state["last_update"] = str(datetime.datetime.now())
    # if JSON requested
    if request.args.get("json") == "1":
        return jsonify({"status":"ok", "data": total_energy_state})
    # otherwise return HTML
    return render_template_string(
        HTML_TEMPLATE,
        heaven=total_energy_state.get("heaven_energy"),
        earth=total_energy_state.get("earth_energy"),
        human=total_energy_state.get("human_energy"),
        t=total_energy_state.get("last_update")
    )

@app.route("/sync_dashboards", methods=["POST"])
def sync_dashboards():
    try:
        payload = request.get_json(force=True, silent=True)
    except Exception as e:
        payload = None
    if not payload:
        return jsonify({"status":"error","message":"No JSON payload received"}), 400

    # Merge payload into state (only keys provided)
    for k, v in payload.items():
        total_energy_state[k] = v
    total_energy_state["last_update"] = str(datetime.datetime.now())

    # Notify via socketio
    try:
        socketio.emit("sync_update", total_energy_state)
    except Exception as e:
        print(f"[sync_dashboards] socketio emit error: {e}")

    print(f"[sync_dashboards] updated state: {payload}")
    return jsonify({"status":"ok","data":total_energy_state}), 200

# ---------------------------
# SocketIO events (simple)
# ---------------------------
@socketio.on("connect")
def handle_connect():
    print("[SocketIO] client connected")
    try:
        socketio.emit("sync_update", total_energy_state)
    except Exception as e:
        print(f"[SocketIO] emit on connect failed: {e}")

@socketio.on("ping_server")
def on_ping(msg=None):
    print("[SocketIO] ping:", msg)
    socketio.emit("pong", {"time": str(datetime.datetime.now())})

# ---------------------------
# Run server (Render-compatible)
# ---------------------------
def run():
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Quantum Core Server Pro on port {port} (threading async_mode).")
    # allow_unsafe_werkzeug True to avoid Render blocking dev server (safe in this controlled deployment)
    socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    run()