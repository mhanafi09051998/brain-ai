#!/usr/bin/env python3
import urllib.request
import json
from datetime import datetime, timezone, timedelta
import time

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = ***CHAT_ID_REMOVED***

def fetch_data():
    url = "https://data-api.binance.vision/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=60"
    req = urllib.request.Request(url, headers={"User-Agent": "Claudia/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    return data

def calc_ema(arr, period):
    k = 2 / (period + 1)
    ema = [sum(arr[:period]) / period]
    for v in arr[period:]:
        ema.append((v * k) + (ema[-1] * (1 - k)))
    return ema[-1]

def send_signal():
    try:
        data = fetch_data()
        candles = [{"time": c[0], "open": float(c[1]), "high": float(c[2]), "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])} for c in data]
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]

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

        curr_price = closes[-1]
        
        # SMC Imbalance: Deteksi FVG & Pullback Retest (10 candle terakhir)
        bullish_fvg = False
        bearish_fvg = False
        for i in range(len(candles)-10, len(candles)-1):
            if candles[i]["low"] > candles[i-2]["high"] and (candles[i]["low"] - candles[i-2]["high"] > 0.2 * atr):
                if curr_price <= candles[i]["low"] + (0.2 * atr):
                    bullish_fvg = True
            if candles[i]["high"] < candles[i-2]["low"] and (candles[i-2]["low"] - candles[i]["high"] > 0.2 * atr):
                if curr_price >= candles[i]["high"] - (0.2 * atr):
                    bearish_fvg = True
        
        trend_bull = ema20 > ema50
        trend_bear = ema20 < ema50
        price_above_ema = curr_price > ema20
        price_below_ema = curr_price < ema20
        rsi_bull_ok = 40 <= rsi <= 68
        rsi_bear_ok = 32 <= rsi <= 60
        atr_ok = atr >= 1.5
        
        bull_items = [trend_bull, price_above_ema, rsi_bull_ok, bullish_fvg, atr_ok]
        bear_items = [trend_bear, price_below_ema, rsi_bear_ok, bearish_fvg, atr_ok]
        
        bull_score = sum(bull_items)
        bear_score = sum(bear_items)

        direction = "NETRAL"
        score = max(bull_score, bear_score)
        if bull_score >= 4 and bull_score >= bear_score:
            direction = "BUY"
        elif bear_score >= 4 and bear_score >= bull_score:
            direction = "SELL"

        import os
        state_file = os.path.join(os.path.dirname(__file__), "bot_state.txt")
        last_score = 0
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    last_score = int(f.read().strip() or 0)
            except:
                pass
                
        with open(state_file, "w") as f:
            f.write(str(score))

        now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b %Y • %H:%M:%S WIB")

        if score < 4:
            if last_score >= 4:
                msg = f"🚨 <b>SETUP BATAL (MOMENTUM HILANG)</b>\n⏱️ <code>{now_str}</code>\n\nKondisi pasar melemah ke skor <b>{score}/5</b>. Jangan paksakan entry."
                payload = json.dumps({"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode("utf-8")
                req = urllib.request.Request(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=payload, headers={"Content-Type": "application/json"})
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp: pass
                except: pass
            return
            
        status_header = "🔥 <b>EKSEKUSI (5/5)</b>" if score == 5 else f"⚠️ <b>SIAGA ({score}/5)</b>"
        
        # Calculate SL / TP
        if direction == "BUY":
            sl = curr_price - (atr * 1.5)
            tp1 = curr_price + (curr_price - sl) * 3
            tp2 = curr_price + (curr_price - sl) * 4.5
        else:
            sl = curr_price + (atr * 1.5)
            tp1 = curr_price - (sl - curr_price) * 3
            tp2 = curr_price - (sl - curr_price) * 4.5

        active_items = bull_items if direction == "BUY" else bear_items

        msg = f"""🌟 <b>Market Radar (M15)</b>
━━━━━━━━━━━━━━━━━━━━
🪙 <b>Pair:</b> <code>XAUUSD</code>
⏱️ <code>{now_str}</code>
💵 <b>Price:</b> <code>${curr_price:,.2f}</code>

{status_header}
🧭 <b>Bias:</b> <b>{direction}</b>

<b>[ Parameter Checklist ]</b>
{"✅" if active_items[0] else "❌"} Trend (EMA 20/50)
{"✅" if active_items[1] else "❌"} Price vs EMA
{"✅" if active_items[2] else "❌"} RSI: {rsi:.1f}
{"✅" if active_items[3] else "❌"} FVG Retest
{"✅" if active_items[4] else "❌"} Volatilitas

<b>[ Action Plan ]</b>
🎯 <b>Entry:</b> <code>{curr_price:.2f}</code>
🛑 <b>SL:</b> <code>{sl:.2f}</code>
🏆 <b>TP1 (1:3):</b> <code>{tp1:.2f}</code>
🚀 <b>TP2 (1:4.5):</b> <code>{tp2:.2f}</code>
━━━━━━━━━━━━━━━━━━━━"""
        payload = json.dumps({"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode("utf-8")
        req = urllib.request.Request(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            pass

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    send_signal()
