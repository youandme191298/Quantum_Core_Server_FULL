# ============================================================
# Quantum Core Server Pro (Render Compatible Edition)
# Flask + SocketIO + KeepAlive 24/24 + Auto PORT Fix
# ============================================================

from flask import Flask, jsonify, render_template_string, request
from flask_socketio import SocketIO
import threading, time, requests, datetime, os

# ===============================
# 🔹 Khởi tạo ứng dụng Flask
# ===============================
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ===============================
# 🔹 Cấu hình KeepAlive (ping Render)
# ===============================
KEEPALIVE_URL = "https://quantum-core-server-full.onrender.com/total_energy"

def keep_alive_loop():
    while True:
        try:
            res = requests.get(KEEPALIVE_URL, timeout=10)
            print(f"[KeepAlive ✅] Ping Render {res.status_code} at {datetime.datetime.now()}")
        except Exception as e:
            print(f"[KeepAlive ⚠️] Error: {e}")
        time.sleep(600)  # Ping mỗi 10 phút

threading.Thread(target=keep_alive_loop, daemon=True).start()

# ===============================
# 🔹 Dữ liệu năng lượng mẫu
# ===============================
total_energy_state = {
    "heaven_energy": 3210,
    "earth_energy": 2875,
    "human_energy": 3088,
    "last_update": str(datetime.datetime.now())
}

# ===============================
# 🔹 Endpoint /total_energy
# ===============================
@app.route("/total_energy", methods=["GET"])
def total_energy():
    total_energy_state["last_update"] = str(datetime.datetime.now())

    # JSON mode
    if request.headers.get("Accept") == "application/json" or request.args.get("json") == "1":
        return jsonify({
            "status": "online",
            "data": total_energy_state
        })

    # HTML dashboard
    html_template = """
    <html>
        <head>
            <meta charset="utf-8">
            <title>Quantum Core Dashboard</title>
            <style>
                body { background-color:#0a0a0a; color:#00ffea; text-align:center; font-family:Arial; }
                h1 { color:#00ffc3; }
                .box { border:1px solid #00ffaa; border-radius:10px; width:60%; margin:auto; padding:20px; background:#111; }
                .val { font-size:22px; margin:10px; }
                footer { margin-top:30px; color:#777; font-size:13px; }
            </style>
        </head>
        <body>
            <h1>⚡ Quantum Core Energy Dashboard ⚡</h1>
            <div class="box">
                <div class="val">🔹 Năng lượng Thiên: {{heaven}} ⚛</div>
                <div class="val">🔹 Năng lượng Địa: {{earth}} ⚛</div>
                <div class="val">🔹 Năng lượng Nhân: {{human}} ⚛</div>
                <hr>
                <div>Cập nhật: {{last_update}}</div>
            </div>
            <footer>Quantum Core Server Pro — Flask + SocketIO + KeepAlive 24/24</footer>
        </body>
    </html>
    """
    return render_template_string(
        html_template,
        heaven=total_energy_state["heaven_energy"],
        earth=total_energy_state["earth_energy"],
        human=total_energy_state["human_energy"],
        last_update=total_energy_state["last_update"]
    )

# ===============================
# 🔹 API đồng bộ Dashboard
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
# 🔹 Route test nhanh
# ===============================
@app.route("/test")
def test():
    return "✅ Quantum Core Server is running successfully on Render!"

# ===============================
# 🔹 Chạy server (Render)
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Quantum Core Server Pro đang khởi động trên cổng {port} ...")

    # ⚠️ Render yêu cầu bật allow_unsafe_werkzeug=True
    socketio.run(app,
                 host="0.0.0.0",
                 port=port,
                 debug=False,
                 allow_unsafe_werkzeug=True)