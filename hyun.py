from flask import Flask, jsonify, request
import requests, random, time

app = Flask(__name__)

PLACE_ID = 2753915549  # đổi game bạn

visited = set()
cache = []
last_scan = 0

# ========================
# headers
# ========================
headers = {
    "User-Agent": "Mozilla/5.0"
}

res = requests.get(url, headers=headers, timeout=10)

# =========================
# SCAN SERVER (multi page)
# =========================
def scan_servers():
    global cache

    cache = []
    cursor = None

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for _ in range(10):
        url = f"https://games.roblox.com/v1/games/{PLACE_ID}/servers/Public?limit=100"
        if cursor:
            url += f"&cursor={cursor}"

        try:
            res = requests.get(url, headers=headers, timeout=10)
            data = res.json()

            print("FETCH:", len(data.get("data", [])))

        except Exception as e:
            print("Lỗi:", e)
            break

        for s in data.get("data", []):
            cache.append({
                "id": s["id"],
                "players": s["playing"]
            })

        cursor = data.get("nextPageCursor")
        if not cursor:
            break

        time.sleep(1)

    print("TOTAL:", len(cache))
# =========================
# AUTO REFRESH CACHE
# =========================
def get_cache():
    global last_scan

    # refresh mỗi 60s
    if time.time() - last_scan > 60 or not cache:
        scan_servers()

    return cache

if not cache:
    print("Không có server, retry...")
    time.sleep(2)
    scan_servers()



# =========================
# API: lấy server để hop
# =========================
@app.route("/hop")
def hop():
    servers = get_cache()

    if not servers:
        return jsonify({"status": "empty"})

    # random trong top server ngon
    pick = random.choice(servers[:20])

    return jsonify({
        "server_id": pick["id"],
        "players": pick["players"]
    })


# =========================
# API: list server
# =========================
@app.route("/servers")
def servers():
    return jsonify(get_cache())


# =========================
# API: reset cache
# =========================
@app.route("/")
def home():
    return "API OK"

@app.route("/reset")
def reset():
    global cache, visited
    cache = []
    visited = set()
    return "reset done"

@app.route("/health/scan")
def scan_boss():
    boss = request.args.get("boss")

    servers = get_cache()

    if not servers:
        return jsonify({
            "success": False,
            "data": None
        })

    import random
    pick = random.choice(servers[:20])

    return jsonify({
        "success": True,
        "data": {
            "jobId": pick["id"]
        }
    })


# =========================
# RUN
# =========================
app.run(host="0.0.0.0", port=8000)