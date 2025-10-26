from flask import Flask, jsonify, render_template_string, request
from flask_socketio import SocketIO
import threading, time, datetime, os

# === Khởi tạo Flask + SocketIO ===
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# === Biến toàn cục ===
total_energy = {
    "heaven": 3210,
    "earth": 2875,
    "human": 3088,
    "last_update": str(datetime.datetime.now())
}

# === Hàm KeepAlive ===
KEEPALIVE_URL = "https://quantum-core-server-full.onrender.com/total_energy"

def keep_alive():
    import requests
    while True:
        try:
            r = requests.get(KEEPALIVE_URL, timeout=10)
            print(f"[KeepAlive ✅] Ping {KEEPALIVE_URL} → {r.status_code}")
        except Exception as e:
            print(f"[KeepAlive ⚠️] {e}")
        time.sleep(600)

threading.Thread(target=keep_alive, daemon=True).start()

# === Giao diện Dashboard ===
@app.route("/total_energy")
def dashboard():
    total_energy["last_update"] = str(datetime.datetime.now())
    if request.args.get("json") == "1":
        return jsonify({"status": "ok", "data": total_energy})
    html = """
    <html><head><meta charset='utf-8'>
    <title>Quantum Core Energy Dashboard</title>
    <style>
      body {background:#0a0a0a;color:#00ffe1;text-align:center;font-family:Consolas;}
      h1 {color:#00ffc3;}
      .box{margin:auto;width:60%;background:#111;border-radius:15px;padding:20px;
           box-shadow:0 0 15px #00ffcc;}
      .v{font-size:20px;margin:8px;}
    </style></head><body>
      <h1>⚡ Quantum Core Energy Dashboard ⚡</h1>
      <div class='box'>
        <div class='v'>Thiên khí: {{h}}</div>
        <div class='v'>Địa khí: {{e}}</div>
        <div class='v'>Nhân khí: {{n}}</div>
        <hr><div>Cập nhật: {{t}}</div>
      </div>
    </body></html>
    """
    return render_template_string(
        html,
        h=total_energy["heaven"],
        e=total_energy["earth"],
        n=total_energy["human"],
        t=total_energy["last_update"]
    )

# === API cập nhật dữ liệu ===
@app.route("/sync_dashboards", methods=["POST"])
def sync_data():
    data = request.get_json(silent=True, force=True)
    if not data:
        return jsonify({"status":"error","msg":"no data"}), 400
    total_energy.update(data)
    total_energy["last_update"] = str(datetime.datetime.now())
    socketio.emit("sync_update", total_energy)
    print(f"[SYNC] Dashboard updated: {data}")
    return jsonify({"status":"ok","data":total_energy})

# === Kiểm tra ===
@app.route("/")
@app.route("/test")
def test():
    return "✅ Quantum Core Server is online!"

# === Khởi động server (Render-safe) ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Quantum Core Server Pro on port {port}")
    socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)