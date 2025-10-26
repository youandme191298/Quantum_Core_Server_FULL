# ============================================================
# Quantum Core Server Pro - Render Stable Release v2
# Flask + SocketIO + KeepAlive 24/24 + Auto Port + Render Fix
# ============================================================

from flask import Flask, jsonify, render_template_string, request
from flask_socketio import SocketIO
import threading, time, requests, datetime, os

# ===============================
# 🔹 Flask setup
# ===============================
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ===============================
# 🔹 KeepAlive Function (ping Render)
# ===============================
KEEPALIVE_URL = "https://quantum-core-server-full.onrender.com/total_energy"

def keep_alive_loop():
    while True:
        try:
            res = requests.get(KEEPALIVE_URL, timeout=10)
            print(f"[KeepAlive ✅] Ping Render {res.status_code} at {datetime.datetime.now()}")
        except Exception as e:
            print(f"[KeepAlive ⚠️] Error: {e}")
        time.sleep(600)  # ping mỗi 10 phút

threading.Thread(target=keep_alive_loop, daemon=True).start()

# ===============================
# 🔹 Dữ liệu mẫu năng lượng
# ===============================
total_energy_state = {
    "heaven_energy": 3210,
    "earth_energy": 2875,
    "human_energy": 3088,
    "last_update": str(datetime.datetime.now())
}

# ===============================
# 🔹 HTML Dashboard
# ===============================
@app.route("/total_energy", methods=["GET"])
def total_energy():
    total_energy_state["last_update"] = str(datetime.datetime.now())
    if request.args.get("json") == "1":
        return jsonify({
            "status": "online",
            "data": total_energy_state
        })
    
    html_template = """
    <html>
    <head>
        <meta charset="utf-8">
        <title>Quantum Core Dashboard</title>
        <style>
            body { background:#0b0b0b; color:#00ffe1; text-align:center; font-family:Consolas, monospace; }
            h1 { color:#00ffc3; }
            .box { margin:auto; width:60%; background:#111; border-radius:15px; padding:20px; box-shadow:0 0 15px #00ffcc; }
            .val { margin:10px; font-size:20px; }
        </style>
    </head>
    <body>
        <h1>⚡ Quantum Core Energy Dashboard ⚡</h1>
        <div class="box">
            <div class="val">🔹 Năng lượng Thiên: {{h}} ⚛</div>
            <div class="val">🔹 Năng lượng Địa: {{e}} ⚛</div>
            <div class="val">🔹 Năng lượng Nhân: {{n}} ⚛</div>
            <hr>
            <div>Cập nhật: {{t}}</div>
        </div>
        <footer style="margin-top:30px; color:#666; font-size:13px;">
            Quantum Core Server Pro — Flask + SocketIO + KeepAlive 24/24
        </footer>
    </body>
    </html>
    """
    return render_template_string(
        html_template,
        h=total_energy_state["heaven_energy"],
        e=total_energy_state["earth_energy"],
        n=total_energy_state["human_energy"],
        t=total_energy_state["last_update"]
    )

# ===============================
# 🔹 Đồng bộ Dashboard (API)
# ===============================
@app.route("/sync_dashboards", methods=["POST"])
def sync_dashboards():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Không có dữ liệu gửi lên!"}), 400
    
    total_energy_state.update(data)
    total_energy_state["last_update"] = str(datetime.datetime.now())
    socketio.emit("sync_update", total_energy_state)
    print(f"[SYNC] Dashboard cập nhật: {data}")
    return jsonify({"status": "success", "data": total_energy_state}), 200

# ===============================
# 🔹 Kiểm tra nhanh
# ===============================
@app.route("/")
@app.route("/test")
def test():
    return "✅ Quantum Core Server is running successfully on Render!"

# ===============================
# 🔹 Khởi động server
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Quantum Core Server Pro đang chạy trên cổng {port} ...")
    # ⚙️ allow_unsafe_werkzeug để Render không chặn
    socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)