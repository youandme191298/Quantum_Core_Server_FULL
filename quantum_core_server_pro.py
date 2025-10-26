# ======================================================
# Quantum Core Server Pro — FINAL FIX FOR RENDER
# Force Eventlet async mode (Flask-SocketIO)
# ======================================================

import eventlet
eventlet.monkey_patch()  # <— ép Render load eventlet trước Flask

from flask import Flask, jsonify, render_template_string, request
from flask_socketio import SocketIO
import threading, time, datetime, os, requests

# === Flask + SocketIO (Eventlet for production) ===
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# === Energy State ===
total_energy = {
    "heaven": 3210,
    "earth": 2875,
    "human": 3088,
    "last_update": str(datetime.datetime.now())
}

# === Auto-detect domain & KeepAlive setup ===
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://quantum-core-server-full.onrender.com")
KEEPALIVE_URL = f"{RENDER_URL.rstrip('/')}/total_energy"
print(f"[INIT] KeepAlive target set to: {KEEPALIVE_URL}")

def keep_alive():
    while True:
        try:
            r = requests.get(KEEPALIVE_URL, timeout=10)
            if r.status_code == 200:
                print(f"[KeepAlive ✅] Ping success → 200 OK")
            else:
                print(f"[KeepAlive ⚠️] Ping returned {r.status_code}")
        except Exception as e:
            print(f"[KeepAlive ❌] Error: {e}")
        time.sleep(600)  # every 10 minutes

threading.Thread(target=keep_alive, daemon=True).start()

# === HTML Template ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Quantum Core Dashboard</title>
<style>
  body { background:#000; color:#00fff2; font-family:Consolas,monospace; text-align:center; }
  h1 { color:#00ffee; margin-top:40px; }
  .panel { width:60%; margin:auto; padding:20px; border:2px solid #00ffee; border-radius:10px; background:#00141a; }
  .v { margin:10px 0; font-size:18px; }
  footer { margin-top:20px; font-size:12px; color:#aee; }
</style>
</head>
<body>
  <h1>⚡ Quantum Core Server Dashboard ⚡</h1>
  <div class="panel">
    <div class="v">Thiên khí: <b>{{h}}</b></div>
    <div class="v">Địa khí: <b>{{e}}</b></div>
    <div class="v">Nhân khí: <b>{{n}}</b></div>
    <hr/>
    <div class="v">Cập nhật: {{t}}</div>
  </div>
  <footer>API JSON: /total_energy?json=1 | Sync: /sync_dashboards</footer>
</body>
</html>
"""

# === Routes ===
@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Quantum Core Server đang hoạt động"})

@app.route("/total_energy", methods=["GET"])
def dashboard():
    total_energy["last_update"] = str(datetime.datetime.now())
    if request.args.get("json") == "1":
        return jsonify({"status": "ok", "data": total_energy})
    return render_template_string(
        HTML_TEMPLATE,
        h=total_energy["heaven"],
        e=total_energy["earth"],
        n=total_energy["human"],
        t=total_energy["last_update"]
    )

@app.route("/sync_dashboards", methods=["POST"])
def sync_dashboards():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"status":"error","message":"Không nhận được dữ liệu"}),400
    total_energy.update(data)
    total_energy["last_update"] = str(datetime.datetime.now())
    socketio.emit("sync_update", total_energy)
    print(f"[SYNC] Cập nhật năng lượng: {data}")
    return jsonify({"status":"ok","data":total_energy}),200

@app.route("/test")
def test():
    return jsonify({"status":"running","time":str(datetime.datetime.now())})

# === SocketIO ===
@socketio.on("connect")
def handle_connect():
    print("[SocketIO] Client connected")
    socketio.emit("sync_update", total_energy)

# === Run (for Render Production via Gunicorn + Eventlet) ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"\n🚀 Quantum Core Server Pro khởi động trên cổng {port}")
    print("🌐 Render external URL:", RENDER_URL)
    print("🔁 KeepAlive URL:", KEEPALIVE_URL)
    socketio.run(app, host="0.0.0.0", port=port)