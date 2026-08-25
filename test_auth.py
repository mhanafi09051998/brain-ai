import urllib.request
import json

BASE = "http://localhost:3016"

# 1. Test Register
try:
    reg_data = json.dumps({
        "name": "Muhammad Hanafi",
        "email": "hanafi@goblix.com",
        "password": "supersecretpassword123"
    }).encode()
    req = urllib.request.Request(f"{BASE}/api/auth/register", data=reg_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print("[REGISTER SUCCESS]", res)
        token = res["token"]
except Exception as e:
    print("[REGISTER INFO/EXISTS]", e)

# 2. Test Login
login_data = json.dumps({
    "email": "hanafi@goblix.com",
    "password": "supersecretpassword123"
}).encode()
req = urllib.request.Request(f"{BASE}/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    print("[LOGIN SUCCESS]", res)
    token = res["token"]

# 3. Test Me / Token Validation
req = urllib.request.Request(f"{BASE}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    print("[AUTH ME SUCCESS]", res)
