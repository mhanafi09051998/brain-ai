import re

file_path = '/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py'

with open(file_path, 'r') as f:
    c = f.read()

pattern = re.compile(r'def fetch_klines\(.*?\).*?return None', re.DOTALL)

replacement = '''TWELVE_API_KEY = "958225eca53b4155b28c09f3159e44a5"

def fetch_klines(symbol: str, interval: str = "15m", limit: int = 60):
    """Fetch realtime Spot Gold (XAU/USD) via TwelveData API."""
    twelve_interval = "15min" if interval == "15m" else interval
    target_symbol = "XAU/USD"
    url = f"https://api.twelvedata.com/time_series?symbol={target_symbol}&interval={twelve_interval}&outputsize={limit}&apikey={TWELVE_API_KEY}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Claudia/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            
        if "values" not in data:
            print("[ERROR] TwelveData API error:", data)
            return None
            
        candles = []
        for c in reversed(data["values"]):
            candles.append({
                "time": c["datetime"],
                "open": float(c["open"]),
                "high": float(c["high"]),
                "low": float(c["low"]),
                "close": float(c["close"]),
                "volume": 0
            })
        return candles
    except Exception as e:
        print(f"[ERROR] fetch_klines TwelveData: {e}")
        return None'''

c = re.sub(pattern, replacement, c)

with open(file_path, 'w') as f:
    f.write(c)

print("TwelveData API integrated successfully")
