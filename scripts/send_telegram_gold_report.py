#!/usr/bin/env python3
import urllib.request
import json
from datetime import datetime, timezone, timedelta

def send_live_report():
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

    curr_price = closes[-1]
    
    # SMC Imbalance: Deteksi FVG & Pullback Retest (10 candle terakhir)
    bullish_fvg = False
    bearish_fvg = False
    for i in range(len(candles)-10, len(candles)-1):
        if candles[i]["low"] > candles[i-2]["high"] and (candles[i]["low"] - candles[i-2]["high"] > 0.2 * atr):
            if curr_price <= candles[i]["low"] + (0.2 * atr):  # Harga retest masuk ke area FVG
                bullish_fvg = True
        if candles[i]["high"] < candles[i-2]["low"] and (candles[i-2]["low"] - candles[i]["high"] > 0.2 * atr):
            if curr_price >= candles[i]["high"] - (0.2 * atr): # Harga retest naik ke area FVG
                bearish_fvg = True
    
    # 5 Conditions Check
    trend_bull = ema20 > ema50
    trend_bear = ema20 < ema50
    price_above_ema = curr_price > ema20
    price_below_ema = curr_price < ema20
    rsi_bull_ok = 40 <= rsi <= 68
    rsi_bear_ok = 32 <= rsi <= 60
    atr_ok = atr >= 1.5
    
    bull_items = [
        ("✅ 1. Tren Struktur: BULLISH (EMA 20 > EMA 50)" if trend_bull else f"❌ 1. Tren Struktur: Belum Bullish (${ema20:.2f} <= ${ema50:.2f})", trend_bull),
        (f"✅ 2. Posisi Harga: Di Atas EMA 20 (${curr_price:.2f} > ${ema20:.2f})" if price_above_ema else f"❌ 2. Posisi Harga: Di Bawah EMA 20 (${curr_price:.2f} <= ${ema20:.2f})", price_above_ema),
        (f"✅ 3. Momentum RSI 14: {rsi:.1f} (Zona Ideal 40–68)" if rsi_bull_ok else (f"❌ 3. Momentum RSI 14: {rsi:.1f} (Overbought > 68)" if rsi > 68 else f"❌ 3. Momentum RSI 14: {rsi:.1f} (Terlalu Rendah < 40)"), rsi_bull_ok),
        ("✅ 4. SMC Imbalance: Bullish FVG Terbentuk" if bullish_fvg else "❌ 4. SMC Imbalance: Menunggu Bullish FVG / Gap", bullish_fvg),
        (f"✅ 5. Volatilitas ATR 14: ${atr:.2f} (Memenuhi syarat >= $1.50)" if atr_ok else f"❌ 5. Volatilitas ATR 14: ${atr:.2f} (Terlalu Rendah < $1.50)", atr_ok)
    ]
    bull_score = sum(1 for _, ok in bull_items if ok)
    
    bear_items = [
        ("✅ 1. Tren Struktur: BEARISH (EMA 20 < EMA 50)" if trend_bear else f"❌ 1. Tren Struktur: Belum Bearish (${ema20:.2f} >= ${ema50:.2f})", trend_bear),
        (f"✅ 2. Posisi Harga: Di Bawah EMA 20 (${curr_price:.2f} < ${ema20:.2f})" if price_below_ema else f"❌ 2. Posisi Harga: Di Atas EMA 20 (${curr_price:.2f} >= ${ema20:.2f})", price_below_ema),
        (f"✅ 3. Momentum RSI 14: {rsi:.1f} (Zona Ideal 32–60)" if rsi_bear_ok else (f"❌ 3. Momentum RSI 14: {rsi:.1f} (Oversold < 32)" if rsi < 32 else f"❌ 3. Momentum RSI 14: {rsi:.1f} (Terlalu Tinggi > 60)"), rsi_bear_ok),
        ("✅ 4. SMC Imbalance: Bearish FVG Terbentuk" if bearish_fvg else "❌ 4. SMC Imbalance: Menunggu Bearish FVG / Gap", bearish_fvg),
        (f"✅ 5. Volatilitas ATR 14: ${atr:.2f} (Memenuhi syarat >= $1.50)" if atr_ok else f"❌ 5. Volatilitas ATR 14: ${atr:.2f} (Terlalu Rendah < $1.50)", atr_ok)
    ]
    bear_score = sum(1 for _, ok in bear_items if ok)
    
    if bull_score >= bear_score:
        direction = "BUY (LONG)"
        score = bull_score
        items = bull_items
        is_bull = True
        sl = round(curr_price - (1.5 * atr), 2)
        tp1 = round(curr_price + (3.0 * atr), 2)
        tp2 = round(curr_price + (4.5 * atr), 2)
    else:
        direction = "SELL (SHORT)"
        score = bear_score
        is_bull = False
        sl = round(curr_price + (1.5 * atr), 2)
        tp1 = round(curr_price - (3.0 * atr), 2)
        tp2 = round(curr_price - (4.5 * atr), 2)
        
    status_header = f"🔥 <b>EKSEKUSI ({score}/5)</b>" if score == 5 else f"⚠️ <b>SIAGA ({score}/5)</b>"
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b %Y • %H:%M:%S WIB")

    if is_bull:
        check_txt = f"""{"✅" if trend_bull else "❌"} Trend Bullish
{"✅" if price_above_ema else "❌"} Price > EMA20
{"✅" if rsi_bull_ok else "❌"} RSI: {rsi:.1f}
{"✅" if bullish_fvg else "❌"} FVG Retest
{"✅" if atr_ok else "❌"} Volatilitas"""
    else:
        check_txt = f"""{"✅" if trend_bear else "❌"} Trend Bearish
{"✅" if price_below_ema else "❌"} Price < EMA20
{"✅" if rsi_bear_ok else "❌"} RSI: {rsi:.1f}
{"✅" if bearish_fvg else "❌"} FVG Retest
{"✅" if atr_ok else "❌"} Volatilitas"""

    msg = f"""🌟 <b>Market Radar (M15)</b>
━━━━━━━━━━━━━━━━━━━━
🪙 <b>Pair:</b> <code>XAUUSD</code>
⏱️ <code>{now_str}</code>
💵 <b>Price:</b> <code>${curr_price:,.2f}</code>

{status_header}
🧭 <b>Bias:</b> <b>{direction}</b>

<b>[ Parameter Checklist ]</b>
{check_txt}

<b>[ Action Plan ]</b>
🎯 <b>Entry:</b> <code>${curr_price:,.2f}</code>
🛑 <b>SL:</b> <code>${sl:,.2f}</code>
🏆 <b>TP1 (1:3):</b> <code>${tp1:,.2f}</code>
🚀 <b>TP2 (1:4.5):</b> <code>${tp2:,.2f}</code>
━━━━━━━━━━━━━━━━━━━━"""

    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    CHAT_ID = ***CHAT_ID_REMOVED***

    print(msg)

    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }).encode("utf-8")

    req = urllib.request.Request(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("TELEGRAM_SENT_SUCCESS:", resp.status)

if __name__ == "__main__":
    send_live_report()
