from flask import Flask, jsonify
import requests, time, random

app = Flask(__name__)

PLACE_ID = 2753915549

cache = []
last_scan = 0

headers = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# SCAN SERVER
# =========================
def scan_servers():
    global cache, last_scan

    cache = []
    cursor = None

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
    last_scan = time.time()


# =========================
# GET CACHE
# =========================
def get_cache():
    global last_scan

    if time.time() - last_scan > 60 or not cache:
        scan_servers()

    return cache


# =========================
# API: RANDOM SERVER
# =========================
@app.route("/hop")
def hop():
    servers = get_cache()

    if not servers:
        return jsonify({
            "success": False,
            "data": None
        })

    pick = random.choice(servers[:20])

    return jsonify({
        "success": True,
        "data": {
            "jobId": pick["id"]
        }
    })


# =========================
# API: LIST SERVER
# =========================
@app.route("/servers")
def servers():
    return jsonify(get_cache())


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "API OK"


# ❌ KHÔNG DÙNG app.run() KHI DEPLOY RENDER
