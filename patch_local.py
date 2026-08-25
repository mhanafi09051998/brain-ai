import re

file_path = 'scripts/claudia_live_watchdog.py'
with open(file_path, 'r') as f: c = f.read()

replacement = '''def fetch_klines_tiingo(ticker: str):
    """Fetch 15m candles from Tiingo FX"""
    import datetime
    start = (datetime.datetime.now() - datetime.timedelta(days=4)).strftime('%Y-%m-%d')
    url = f"https://api.tiingo.com/tiingo/fx/prices?tickers={ticker}&resampleFreq=15min&startDate={start}&token={TIINGO_TOKEN}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Claudia/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if not data: return []
        candles = []
        for c in data:
            candles.append({
                "time": c["date"],
                "open": float(c["open"]),
                "high": float(c["high"]),
                "low": float(c["low"]),
                "close": float(c["close"])
            })
        return candles # Ascending order (oldest first)
    except Exception as e:
        print(f"[ERROR] fetch_tiingo {ticker}: {e}")
        return []'''

c = re.sub(r'def fetch_klines_tiingo\(ticker: str\):.*?return \[\]\s*except Exception as e:.*?return \[\]', replacement, c, flags=re.DOTALL)
with open(file_path, 'w') as f: f.write(c)
