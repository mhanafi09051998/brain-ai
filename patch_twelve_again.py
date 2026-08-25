import re

file_path = '/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py'

with open(file_path, 'r') as f:
    c = f.read()

# Replace Tiingo source with TwelveData
old_assets = '''ASSETS = [
    {"id": "GOLD", "pair": "XAUUSD", "source": "tiingo", "ticker": "xauusd"}
]'''

new_assets = '''ASSETS = [
    {"id": "GOLD", "pair": "XAUUSD", "source": "twelve", "ticker": "XAU/USD"}
]'''

c = c.replace(old_assets, new_assets)

old_msg = '''msg = (
        f"🟡 <b>CLAUDIA 5.0 DEDICATED GOLD QUANT AKTIF</b>\\n"
        f"━━━━━━━━━━━━━━━━━━━━━\\n"
        f"⚡ <b>Fokus:</b> Emas Spot (XAU/USD)\\n"
        f"📊 <b>Strategi:</b> SMC FVG + EMA 20/50 + ATR\\n"
        f"🛡️ <b>Engine:</b> Tiingo FX (Real-time)\\n"
        f"━━━━━━━━━━━━━━━━━━━━━\\n"
        f"✨ <i>Gold Watchdog is Live.</i>"
    )'''

new_msg = '''msg = (
        f"🟡 <b>CLAUDIA 5.0 DEDICATED GOLD QUANT AKTIF</b>\\n"
        f"━━━━━━━━━━━━━━━━━━━━━\\n"
        f"⚡ <b>Fokus:</b> Emas Spot (XAU/USD)\\n"
        f"📊 <b>Strategi:</b> SMC FVG + EMA 20/50 + ATR\\n"
        f"🛡️ <b>Engine:</b> TwelveData FX (Real-time)\\n"
        f"━━━━━━━━━━━━━━━━━━━━━\\n"
        f"✨ <i>Gold Watchdog is Live.</i>"
    )'''

c = c.replace(old_msg, new_msg)

# Re-inject TwelveData fetcher
twelve_fetcher = '''
TWELVE_API_KEY = "958225eca53b4155b28c09f3159e44a5"

def fetch_klines_twelve(ticker: str):
    url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval=15min&outputsize=60&apikey={TWELVE_API_KEY}&timezone=Asia/Jakarta"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Claudia/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if "values" not in data: return []
        candles = []
        for c in reversed(data["values"]):
            candles.append({
                "time": c["datetime"],
                "open": float(c["open"]),
                "high": float(c["high"]),
                "low": float(c["low"]),
                "close": float(c["close"])
            })
        return candles
    except Exception as e:
        print(f"[ERROR] fetch_twelve {ticker}: {e}")
        return []
'''

if "def fetch_klines_twelve" not in c:
    c = c.replace("def fetch_klines_tiingo", twelve_fetcher + "\ndef fetch_klines_tiingo")

# Update scan_asset logic
c = c.replace('if asset["source"] == "tiingo":', 'if asset["source"] == "twelve":\n        candles = fetch_klines_twelve(asset["ticker"])\n    elif asset["source"] == "tiingo":')

with open(file_path, 'w') as f:
    f.write(c)
