import os
import sys
import time
import json
import math
import urllib.request
import subprocess
from datetime import datetime, timezone, timedelta

# Configuration
TELEGRAM_SERVER_BOT_TOKEN = os.environ.get("TELEGRAM_SERVER_BOT_TOKEN", "***TELEGRAM_TOKEN_REMOVED***")
TELEGRAM_GOLD_BOT_TOKEN = os.environ.get("TELEGRAM_GOLD_BOT_TOKEN", "***TELEGRAM_TOKEN_REMOVED***")
TARGET_CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID", "***CHAT_ID_REMOVED***"))
POLL_INTERVAL_SEC = 60

last_alert_time = {}

def send_telegram_msg(text: str) -> bool:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_GOLD_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": TARGET_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram: {e}")
        return False

def send_telegram_server(text: str) -> bool:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_SERVER_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": TARGET_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except:
        return False

# ==========================================
# FETCHERS
# ==========================================
TIINGO_TOKEN = "a1f5ac2a8a2a5917da307ec4035815397fa97fc4"

def fetch_klines_tiingo(ticker: str):
    """Fetch 15m candles from Tiingo FX"""
    url = f"https://api.tiingo.com/tiingo/fx/prices?tickers={ticker}&resampleFreq=15min&token={TIINGO_TOKEN}"
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
        return []

def fetch_klines_yahoo(ticker: str):
    """Fetch 15m candles from Yahoo Finance"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=15m&range=5d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        result = data['chart']['result'][0]
        quote = result['indicators']['quote'][0]
        times = result['timestamp']
        candles = []
        for i in range(len(times)):
            if quote['close'][i] is None: continue
            candles.append({
                "time": times[i],
                "open": float(quote['open'][i]),
                "high": float(quote['high'][i]),
                "low": float(quote['low'][i]),
                "close": float(quote['close'][i])
            })
        return candles # Ascending order
    except Exception as e:
        print(f"[ERROR] fetch_yahoo {ticker}: {e}")
        return []

# ==========================================
# INDICATORS
# ==========================================
def calc_indicators(candles):
    if len(candles) < 50: return None
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    
    def ema(arr, p):
        k = 2 / (p + 1)
        e = [sum(arr[:p]) / p]
        for v in arr[p:]:
            e.append((v * k) + (e[-1] * (1 - k)))
        return e[-1]
    
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(diff if diff > 0 else 0)
        losses.append(abs(diff) if diff < 0 else 0)
    
    avg_gain = sum(gains[-14:]) / 14 if len(gains) >= 14 else 0
    avg_loss = sum(losses[-14:]) / 14 if len(losses) >= 14 else 0.0001
    rs = avg_gain / avg_loss if avg_loss > 0 else 100
    rsi = 100 - (100 / (1 + rs))
    
    trs = []
    for i in range(1, len(candles)):
        tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
        trs.append(tr)
    atr = sum(trs[-14:]) / 14
    
    curr = closes[-1]
    bull_fvg = bear_fvg = False
    for i in range(len(candles)-10, len(candles)-1):
        if candles[i]["low"] > candles[i-2]["high"] and (candles[i]["low"] - candles[i-2]["high"] > 0.2 * atr):
            if curr <= candles[i]["low"] + (0.2 * atr): bull_fvg = True
        if candles[i]["high"] < candles[i-2]["low"] and (candles[i-2]["low"] - candles[i]["high"] > 0.2 * atr):
            if curr >= candles[i]["high"] - (0.2 * atr): bear_fvg = True
            
    return {
        "price": curr,
        "ema20": ema20,
        "ema50": ema50,
        "rsi": rsi,
        "atr": atr,
        "bullish_fvg": bull_fvg,
        "bearish_fvg": bear_fvg
    }

# ==========================================
# SCAN LOGIC
# ==========================================
ASSETS = [
    {"id": "GOLD", "pair": "XAUUSD", "source": "tiingo", "ticker": "xauusd"}
]

def scan_asset(asset):
    if asset["source"] == "tiingo":
        candles = fetch_klines_tiingo(asset["ticker"])
    else:
        candles = fetch_klines_yahoo(asset["ticker"])
        
    if not candles: return
    ind = calc_indicators(candles)
    if not ind: return
    
    price = ind["price"]
    atr = ind["atr"]
    rsi = ind["rsi"]
    ema20 = ind["ema20"]
    ema50 = ind["ema50"]
    now_ts = time.time()
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b %Y • %H:%M:%S WIB")

    trend_bull = ema20 > ema50
    trend_bear = ema20 < ema50
    price_above_ema = price > ema20
    price_below_ema = price < ema20
    rsi_bull_ok = 40 <= rsi <= 68
    rsi_bear_ok = 32 <= rsi <= 60
    fvg_bull = ind["bullish_fvg"]
    fvg_bear = ind["bearish_fvg"]
    atr_ok = atr >= 1.5 if asset["id"] == "GOLD" else True # Allow lower ATR for Silver/Oil

    bull_score = sum([trend_bull, price_above_ema, rsi_bull_ok, fvg_bull, atr_ok])
    bear_score = sum([trend_bear, price_below_ema, rsi_bear_ok, fvg_bear, atr_ok])

    if bull_score >= bear_score:
        direction = "BUY (LONG)"
        score = bull_score
        is_bull = True
    else:
        direction = "SELL (SHORT)"
        score = bear_score
        is_bull = False
        
    last_signal_t = last_alert_time.get(f"{asset['id']}_signal", 0)
    last_radar_score = last_alert_time.get(f"{asset['id']}_radar_score", 0)
    
    status_header = f"🔥 <b>EKSEKUSI ({score}/5)</b>" if score == 5 else f"⚠️ <b>SIAGA ({score}/5)</b>"
    
    if is_bull:
        check_txt = f"""{"✅" if trend_bull else "❌"} Trend Bullish
{"✅" if price_above_ema else "❌"} Price vs EMA20
{"✅" if rsi_bull_ok else "❌"} RSI: {rsi:.1f}
{"✅" if fvg_bull else "❌"} FVG Retest
{"✅" if atr_ok else "❌"} Volatilitas"""
        sl = round(price - (1.5 * atr), 2)
        tp1 = round(price + (3.0 * atr), 2)
        tp2 = round(price + (4.5 * atr), 2)
    else:
        check_txt = f"""{"✅" if trend_bear else "❌"} Trend Bearish
{"✅" if price_below_ema else "❌"} Price vs EMA20
{"✅" if rsi_bear_ok else "❌"} RSI: {rsi:.1f}
{"✅" if fvg_bear else "❌"} FVG Retest
{"✅" if atr_ok else "❌"} Volatilitas"""
        sl = round(price + (1.5 * atr), 2)
        tp1 = round(price - (3.0 * atr), 2)
        tp2 = round(price - (4.5 * atr), 2)

    msg_template = f"""🌟 <b>Market Radar {asset['id']} (M15)</b>
━━━━━━━━━━━━━━━━━━━━
🪙 <b>Pair:</b> <code>{asset['pair']}</code>
⏱️ <code>{now_str}</code>
💵 <b>Price:</b> <code>${price:,.2f}</code>

{status_header}
🧭 <b>Bias:</b> <b>{direction}</b>

<b>[ Parameter Checklist ]</b>
{check_txt}

<b>[ Action Plan ]</b>
🎯 <b>Entry:</b> <code>{price:.2f}</code>
🛑 <b>SL:</b> <code>{sl:.2f}</code>
🏆 <b>TP1 (1:3):</b> <code>{tp1:.2f}</code>
🚀 <b>TP2 (1:4.5):</b> <code>{tp2:.2f}</code>
━━━━━━━━━━━━━━━━━━━━"""

    if score < 4:
        if last_radar_score >= 4:
            cancel_msg = f"🚨 <b>SETUP BATAL (MOMENTUM HILANG)</b>\n⏱️ <code>{now_str}</code>\n\nKondisi pasar <b>{asset['pair']}</b> melemah ke skor <b>{score}/5</b>. Jangan paksakan entry."
            send_telegram_msg(cancel_msg)
            last_alert_time[f"{asset['id']}_radar_score"] = score
        return
        
    if score == 5 and (now_ts - last_signal_t) >= 1800:
        if send_telegram_msg(msg_template):
            last_alert_time[f"{asset['id']}_signal"] = now_ts
            last_alert_time[f"{asset['id']}_radar_score"] = score
    elif score == 4 and score > last_radar_score:
        if send_telegram_msg(msg_template):
            last_alert_time[f"{asset['id']}_radar_score"] = score

def check_memory_and_restart():
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        total = free = buffers = cached = 0
        for line in lines:
            if line.startswith('MemTotal:'): total = int(line.split()[1])
            elif line.startswith('MemFree:'): free = int(line.split()[1])
            elif line.startswith('Buffers:'): buffers = int(line.split()[1])
            elif line.startswith('Cached:'): cached = int(line.split()[1])
        used_mb = (total - free - buffers - cached) / 1024.0
        if used_mb > MEMORY_LIMIT_MB:
            send_telegram_server(f"🔥 <b>AUTO-HEALING TRIGGERED</b>\nRAM Usage: {used_mb:.1f}MB\nRestarting PM2...")
            subprocess.run(["pm2", "reload", "all"], stdout=subprocess.DEVNULL)
    except: pass

def run_watchdog():
    msg = (
        f"🟡 <b>CLAUDIA 5.0 MULTI-ASSET QUANT AKTIF</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>Fokus:</b> Emas (XAU), Perak (XAG), Minyak (WTI)\n"
        f"📊 <b>Strategi:</b> SMC FVG + EMA 20/50 + ATR\n"
        f"🛡️ <b>Engine:</b> Tiingo FX + Yahoo Finance\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ <i>Multi-Asset Watchdog is Live.</i>"
    )
    send_telegram_msg(msg)
    
    while True:
        for asset in ASSETS:
            scan_asset(asset)
        check_memory_and_restart()
        time.sleep(POLL_INTERVAL_SEC)

if __name__ == "__main__":
    run_watchdog()
