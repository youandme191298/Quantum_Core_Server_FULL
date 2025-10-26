# ==========================================================
# Quantum Core Server Pro (Render Edition)
# ----------------------------------------------------------
# Phiên bản: 3.0.2 - Có tích hợp KeepAlive 24/24
# ----------------------------------------------------------
# Mục đích:
# - Quản lý, điều phối và giám sát năng lượng lượng tử đa tầng
# - Hỗ trợ Flask REST API + SocketIO real-time
# - Tự động duy trì hoạt động server Render không bao giờ “ngủ”
# ==========================================================

from flask import Flask, jsonify
from flask_socketio import SocketIO
import importlib
import os
import time
import random
import threading
import traceback

# ----------------------------------------------------------
# 1. Khởi tạo Flask + SocketIO
# ----------------------------------------------------------
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

print("✅ Flask + SocketIO đã khởi tạo (async_mode = threading).")

# ----------------------------------------------------------
# 2. Tải động các tầng năng lượng trong thư mục core/
# ----------------------------------------------------------
CORE_FOLDER = "core"

def load_core_layers():
    layers = []
    try:
        for file in sorted(os.listdir(CORE_FOLDER)):
            if file.endswith(".py") and file not in ["__init__.py", "__core_loader__.py"]:
                module_name = f"{CORE_FOLDER}.{file[:-3]}"
                try:
                    importlib.import_module(module_name)
                    layers.append(file)
                except Exception as e:
                    print(f"[⚠️] Không thể nạp {file}: {e}")
        print(f"🔹 Đã tải {len(layers)} tầng năng lượng:")
        for idx, layer in enumerate(layers, 1):
            print(f"    {idx:02d}. {layer}")
    except Exception as e:
        print(f"[❌] Lỗi khi nạp core: {e}")
        traceback.print_exc()

load_core_layers()

# ----------------------------------------------------------
# 3. API chính (Endpoints)
# ----------------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "status": "Quantum Core Server Pro Online",
        "description": "Nền điều phối năng lượng lượng tử đa tầng.",
        "version": "3.0.2",
        "endpoints": ["/total_energy", "/sync_dashboards"]
    })

@app.route("/total_energy")
def total_energy():
    try:
        # Giả lập năng lượng tổng dao động
        total = round(random.uniform(4.6, 4.9), 4)
        layers = random.randint(35, 40)
        msg = {
            "Tầng năng lượng": layers,
            "Dao động": total,
            "Trạng thái": random.choice(["Stable", "Resonant", "Harmonized"])
        }
        print(f"[OK] Total Energy Updated: {msg}")
        return jsonify(msg)
    except Exception as e:
        print(f"[❌] Lỗi total_energy: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/sync_dashboards")
def sync_dashboards():
    try:
        msg = {"sync": True, "timestamp": time.time()}
        print("🔄 Đồng bộ dashboard thành công.")
        return jsonify(msg)
    except Exception as e:
        print(f"[❌] Lỗi sync_dashboards: {e}")
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# 4. KeepAlive Bot (Duy trì 24/24)
# ----------------------------------------------------------

def start_keepalive():
    """Luồng nền ping tới chính server Render để giữ hoạt động"""
    try:
        import requests
        url = os.environ.get("KEEPALIVE_PING_URL", "https://quantum-core-server-full.onrender.com/total_energy")
        interval = int(os.environ.get("KEEPALIVE_INTERVAL", "600"))  # 600s = 10 phút
        print(f"[KeepAlive 🔁] Khởi động ping nền mỗi {interval}s -> {url}")

        def ping_loop():
            while True:
                try:
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        print(f"[KeepAlive ✅] Ping thành công ({len(r.text)} bytes)")
                    else:
                        print(f"[KeepAlive ⚠️] Ping trả về HTTP {r.status_code}")
                except Exception as e:
                    print(f"[KeepAlive ❌] Ping lỗi: {e}")
                time.sleep(interval)

        threading.Thread(target=ping_loop, daemon=True).start()
    except Exception as e:
        print(f"[KeepAlive ❌] Không thể khởi động: {e}")


# ----------------------------------------------------------
# 5. Khởi chạy Flask server
# ----------------------------------------------------------

if __name__ == "__main__":
    try:
        # Bật KeepAlive trước khi khởi động Flask
        start_keepalive()

        PORT = int(os.environ.get("PORT", 10000))
        print(f"🚀 Quantum Core Server Pro đang khởi động trên cổng {PORT} ...")
        print("🌐 Dashboard endpoints: /total_energy | /sync_dashboards")
        print("⚡ Đang điều phối năng lượng Thiên–Địa–Nhân ...")

        socketio.run(app, host="0.0.0.0", port=PORT, allow_unsafe_werkzeug=True)

    except Exception as e:
        print(f"[❌] Lỗi khởi động server: {e}")
        traceback.print_exc()
