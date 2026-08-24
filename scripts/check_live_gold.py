import urllib.request
import json
import time

def check_gold():
    url = "https://data-api.binance.vision/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=60"
    req = urllib.request.Request(url, headers={"User-Agent": "Claudia/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    
    candles = [{"time": c[0], "open": float(c[1]), "high": float(c[2]), "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])} for c in data]
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    
    def calc_ema(arr, period):
        k = 2 / (period + 1)
        ema = [sum(arr[:period]) / period]
        for v in arr[period:]:
            ema.append((v * k) + (ema[-1] * (1 - k)))
        return ema[-1]
    
    ema20 = calc_ema(closes, 20)
    ema50 = calc_ema(closes, 50)
    
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i-1]
        gains.append(d if d > 0 else 0)
        losses.append(abs(d) if d < 0 else 0)
    avg_gain = sum(gains[-14:]) / 14
    avg_loss = sum(losses[-14:]) / 14 or 0.0001
    rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
    
    trs = [max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1])) for i in range(1, len(candles))]
    atr = sum(trs[-14:]) / 14
    
    c1, c2, c3 = candles[-3], candles[-2], candles[-1]
    bullish_fvg = (c3["low"] > c1["high"]) and (c3["low"] - c1["high"] > 0.2 * atr)
    bearish_fvg = (c3["high"] < c1["low"]) and (c1["low"] - c3["high"] > 0.2 * atr)
    
    # 5 Institutional Conditions Checklist
    # 1. EMA Trend Structure
    trend_bull = ema20 > ema50
    trend_bear = ema20 < ema50
    trend_status = "BULLISH (EMA20 > EMA50)" if trend_bull else "BEARISH (EMA20 < EMA50)"
    
    # 2. RSI Health Zone
    rsi_bull_ok = 40 <= rsi <= 68
    rsi_bear_ok = 32 <= rsi <= 60
    
    # 3. Fair Value Gap (FVG) Imbalance
    fvg_status = "BULLISH FVG DETECTED" if bullish_fvg else ("BEARISH FVG DETECTED" if bearish_fvg else "NO FVG (BALANCED)")
    
    # 4. ATR Volatility Expansion
    atr_ok = atr >= 1.5  # normal 15m Gold ATR is $2-$6
    
    # 5. Price Position relative to EMA20
    price_aligned_bull = closes[-1] > ema20
    price_aligned_bear = closes[-1] < ema20
    
    print(json.dumps({
        "current_price": closes[-1],
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
        "rsi_14": round(rsi, 1),
        "atr_14": round(atr, 2),
        "trend_status": trend_status,
        "fvg_status": fvg_status,
        "checklist": {
            "1_trend_confirmation": "READY (BULLISH)" if trend_bull else "READY (BEARISH)",
            "2_rsi_momentum": f"READY ({round(rsi,1)})" if (rsi_bull_ok or rsi_bear_ok) else f"OVERHEATED ({round(rsi,1)})",
            "3_fvg_imbalance": "READY (IMBALANCE FORMED)" if (bullish_fvg or bearish_fvg) else "WAITING (MARKET BALANCED / NO GAP)",
            "4_atr_volatility": f"READY (${round(atr,2)})",
            "5_price_alignment": "READY (ABOVE EMA20)" if price_aligned_bull else "READY (BELOW EMA20)"
        }
    }, indent=2))

if __name__ == "__main__":
    check_gold()
