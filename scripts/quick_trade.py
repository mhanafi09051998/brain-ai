import urllib.request, json

url = "https://data-api.binance.vision/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=15"
data = json.loads(urllib.request.urlopen(url).read().decode())
candles = [{"high": float(c[2]), "low": float(c[3]), "close": float(c[4])} for c in data]

trs = []
for i in range(1, len(candles)):
    h, l = candles[i]["high"], candles[i]["low"]
    prev_c = candles[i-1]["close"]
    trs.append(max(h-l, abs(h-prev_c), abs(l-prev_c)))

atr = sum(trs) / len(trs)
curr = candles[-1]["close"]

print(f"Current: {curr:.2f}")
print(f"ATR: {atr:.2f}")
