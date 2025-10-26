# ======================================================
# Quantum Core Server Pro (Render Final Stable Build)
# Flask + SocketIO + KeepAlive + Auto Port Detection
# ======================================================

from flask import Flask, jsonify, render_template_string, request
from flask_socketio import SocketIO
import threading, time, datetime, os

# === Flask + SocketIO initialization ===
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# === Energy state ===
total_energy = {
    "heaven": 3210,
    "earth": 2875,
    "human": 3088,
    "last_update": str(datetime.datetime.now())
}

# === KeepAlive (ping server every 10 minutes) ===
KEEPALIVE_URL = "https://quantum-core-server-full.onrender.com/total_energy"

def keep_alive():
    try:
        import requests
    except ImportError:
        print("[KeepAlive ⚠️] requests module not installed — skipping ping loop.")
        return
    while True:
        try:
            r = requests.get(KEEPALIVE_URL, timeout=10)
            print(f"[KeepAlive ✅] Ping {KEEPALIVE_URL} → {r.status_code}")
        except Exception as e:
            print(f"[KeepAlive ⚠️] Ping error: {e}")
        time.sleep(600)  # 10 minutes interval

threading.Thread(target=keep_alive, daemon=True).start()

# === HTML Template ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Quantum Core - Total Energy</title>
<style>
  body { background-color:#020c14; color:#00fff0; font-family:Consolas,monospace; text-align:center; }
  h1 { color:#00ffe1; margin-top:40px; }
  .panel { margin:auto; width:60%; padding:20px; border:2px solid #00ffe1; border-radius:15px; background:#06141c; }
  .v { font-size:20px; margin:10px 0; }
  footer { margin-top:20px; font-size:12px; color:#80cfcf; }
</style>
</head>
<body>
  <h1>⚡ Quantum Core Server Dashboard ⚡</h1>
  <div class="panel">
    <div class="v">Thiên khí: <b>{{h}}</b></div>
    <div class="v">Địa khí: <b>{{e}}</b></div>
    <div class="v">Nhân khí: <b>{{n}}</b></div>
    <hr/>
    <div>Cập nhật: {{t}}</div>
  </div>
  <footer>API JSON: /total_energy?json=1 | Sync endpoint: /sync_dashboards</footer>
</body>
</html>
"""

# === Routes ===
@app.route("/")
def index():
    return "✅ Quantum Core Server Pro đang hoạt động! Dùng /total_energy để xem dashboard."

@app.route("/total_energy", methods=["GET"])
def total_energy_dashboard():
    total_energy["last_update"] = str(datetime.datetime.now())
    if request.args.get("json") == "1":
        return jsonify({"status":"ok", "data":total_energy})
    return render_template_string(
        HTML_TEMPLATE,
        h=total_energy["heaven"],
        e=total_energy["earth"],
        n=total_energy["human"],
        t=total_energy["last_update"]
    )

@app.route("/sync_dashboards", methods=["POST"])
def sync_dashboards():
    data = request.get_json(silent=True, force=True)
    if not data:
        return jsonify({"status":"error", "message":"No data received"}), 400
    total_energy.update(data)
    total_energy["last_update"] = str(datetime.datetime.now())
    socketio.emit("sync_update", total_energy)
    print(f"[SYNC] Dashboard updated: {data}")
    return jsonify({"status":"ok", "data":total_energy}), 200

@app.route("/test")
def test_route():
    return jsonify({"status":"running", "time":str(datetime.datetime.now())})

# === SocketIO Events ===
@socketio.on("connect")
def handle_connect():
    print("[SocketIO] Client connected")
    socketio.emit("sync_update", total_energy)

@socketio.on("ping_server")
def handle_ping(msg=None):
    print(f"[SocketIO] Ping from client: {msg}")
    socketio.emit("pong", {"time": str(datetime.datetime.now())})

# === Run server (Render-safe, auto PORT) ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render auto-assigns this
    print(f"🚀 Quantum Core Server Pro running on Render port {port}")
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )