# quantum_core_server_pro.py
# Quantum Core Server FULL – Auto Dashboard + JSON API + KeepAlive 24/24

from flask import Flask, jsonify, render_template_string, request
from flask_socketio import SocketIO
import threading, time, requests, datetime, os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ==========================
# 🔹 KEEPALIVE: Ngăn Render ngủ
# ==========================
KEEPALIVE_URL = "https://quantum-core-server-full.onrender.com/total_energy"

def keep_alive_loop():
    while True:
        try:
            r = requests.get(KEEPALIVE_URL, timeout=10)
            print(f"[KeepAlive ✅] Ping Render {r.status_code} at {datetime.datetime.now()}")
        except Exception as e:
            print(f"[KeepAlive ⚠️] Error: {e}")
        time.sleep(600)  # 10 phút

threading.Thread(target=keep_alive_loop, daemon=True).start()

# ==========================
# 🔹 DỮ LIỆU NỘI BỘ (Mô phỏng năng lượng Thiên-Địa-Nhân)
# ==========================
total_energy_state = {
    "heaven_energy": 3200,
    "earth_energy": 2850,
    "human_energy": 3050,
    "last_update": str(datetime.datetime.now())
}

# ==========================
# 🔹 API + Dashboard
# ==========================
@app.route("/total_energy", methods=["GET"])
def total_energy():
    # Nếu client yêu cầu JSON (ví dụ API call)
    if request.headers.get("Accept") == "application/json" or request.args.get("json") == "1":
        total_energy_state["last_update"] = str(datetime.datetime.now())
        return jsonify({
            "status": "online",
            "data": total_energy_state
        })
    
    # Nếu truy cập bằng trình duyệt, trả HTML
    html_template = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Quantum Core Server Dashboard</title>
        <style>
            body { font-family: Arial; background-color: #0a0a0a; color: #00ffea; text-align: center; }
            h1 { color: #00ffc3; }
            .energy-box { border: 1px solid #00ffaa; border-radius: 10px; padding: 20px; width: 60%; margin: 20px auto; background: #101010; }
            .value { font-size: 22px; color: #00c8ff; }
            footer { margin-top: 40px; color: #888; font-size: 14px; }
        </style>
    </head>
    <body>
        <h1>⚡ Quantum Core Energy Dashboard ⚡</h1>
        <div class="energy-box">
            <p class="value">🔹 Năng lượng Thiên: {{heaven}} ⚛</p>
            <p class="value">🔹 Năng lượng Địa: {{earth}} ⚛</p>
            <p class="value">🔹 Năng lượng Nhân: {{human}} ⚛</p>
            <hr>
            <p>Cập nhật lần cuối: {{last_update}}</p>
        </div>
        <footer>Quantum Core Server Pro — Flask + SocketIO + KeepAlive 24/24</footer>
    </body>
    </html>
    """
    total_energy_state["last_update"] = str(datetime.datetime.now())
    return render_template_string(
        html_template,
        heaven=total_energy_state["heaven_energy"],
        earth=total_energy_state["earth_energy"],
        human=total_energy_state["human_energy"],
        last_update=total_energy_state["last_update"]
    )

# ==========================
# 🔹 Đồng bộ Dashboard (API POST)
# ==========================
@app.route("/sync_dashboards", methods=["POST"])
def sync_dashboards():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Không có dữ liệu gửi lên!"}), 400
    
    total_energy_state.update(data)
    total_energy_state["last_update"] = str(datetime.datetime.now())
    socketio.emit("sync_update", total_energy_state)
    print(f"[SYNC] Dashboard đã cập nhật: {data}")
    return jsonify({"status": "success", "data": total_energy_state}), 200

# ==========================
# 🔹 RUN SERVER
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Quantum Core Server Pro đang khởi động trên cổng {port} ...")
    socketio.run(app, host="0.0.0.0", port=port, debug=False)