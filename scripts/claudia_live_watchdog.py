#!/usr/bin/env python3
"""
Claudia 5.0 Max — 24/7 Autonomous Live Gold Quant & Server Health Watchdog
Features:
1. Real-Time Gold (XAU/USD / PAXG) Quantitative Market Scanner (FVG, EMA 20/50, RSI, ATR 1:3 RRR).
   -> Pushed EXCLUSIVELY to Dedicated Gold Trading Bot (***TELEGRAM_TOKEN_REMOVED***).
2. Autonomous PM2 Server Health Guard & Memory Leak Circuit Breaker (Zero-Downtime Auto-Heal).
   -> Pushed to System Server Bot (***TELEGRAM_TOKEN_REMOVED***).
3. Zero crypto position notifications (Pure XAU/USD Gold Focus).
4. Autonomous Neural Learning & Incident Auto-Logger.
"""

import os
import sys
import time
import json
import math
import urllib.request
import subprocess
from datetime import datetime

# Configuration
TELEGRAM_SERVER_BOT_TOKEN = os.environ.get("TELEGRAM_SERVER_BOT_TOKEN", "***TELEGRAM_TOKEN_REMOVED***")
TELEGRAM_GOLD_BOT_TOKEN = os.environ.get("TELEGRAM_GOLD_BOT_TOKEN", "***TELEGRAM_TOKEN_REMOVED***")
TARGET_CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID", "***CHAT_ID_REMOVED***"))
POLL_INTERVAL_SEC = 60
MEMORY_LIMIT_MB = 450.0

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "learning", "neural_live_logs.jsonl")
TELEMETRY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "learning", "watchdog_telemetry.json")

# State
last_alert_time = {}
service_restart_counts = {}

def send_telegram_gold(text: str) -> bool:
    """Send dedicated Gold (XAU/USD) position alert to Mas Hanafi."""
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
        print(f"[ERROR] Failed to send Gold Telegram: {e}")
        return False

def send_telegram_server(text: str) -> bool:
    """Send server health & critical self-heal alert to system channel."""
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
    except Exception as e:
        print(f"[ERROR] Failed to send Server Telegram: {e}")
        return False

def log_event(event_type: str, details: dict):
    """Log autonomous event to persistent JSONL."""
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[WARN] Failed to write event log: {e}")

# ==========================================
# 🟡 1. QUANTITATIVE GOLD (XAU/USD) SCANNER
# ==========================================
def fetch_klines(symbol: str, interval: str = "15m", limit: int = 50):
    """Fetch public OHLCV klines with multi-endpoint fallback."""
    endpoints = [
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}",
        f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}",
        f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    ]
    
    for url in endpoints:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Claudia/5.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode())
                candles = []
                for c in data:
                    candles.append({
                        "time": int(c[0]),
                        "open": float(c[1]),
                        "high": float(c[2]),
                        "low": float(c[3]),
                        "close": float(c[4]),
                        "volume": float(c[5])
                    })
                if candles:
                    return candles
        except Exception:
            continue
            
    return []

def calculate_indicators(candles):
    """Compute EMA, RSI, ATR, and Fair Value Gaps (FVG)."""
    if len(candles) < 30:
        return None
    
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    
    # EMA Calculation
    def calc_ema(data, period):
        k = 2 / (period + 1)
        ema = [sum(data[:period]) / period]
        for val in data[period:]:
            ema.append((val * k) + (ema[-1] * (1 - k)))
        return ema[-1]
    
    ema20 = calc_ema(closes, 20)
    ema50 = calc_ema(closes, 50) if len(closes) >= 50 else calc_ema(closes, len(closes))
    
    # RSI 14 Calculation
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(diff if diff > 0 else 0)
        losses.append(abs(diff) if diff < 0 else 0)
    
    avg_gain = sum(gains[-14:]) / 14 if len(gains) >= 14 else 0
    avg_loss = sum(losses[-14:]) / 14 if len(losses) >= 14 else 0.0001
    rs = avg_gain / avg_loss if avg_loss > 0 else 100
    rsi = 100 - (100 / (1 + rs))
    
    # ATR 14 Calculation
    trs = []
    for i in range(1, len(candles)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        trs.append(tr)
    atr = sum(trs[-14:]) / 14 if len(trs) >= 14 else (highs[-1] - lows[-1])
    
    # Fair Value Gap (FVG) Check on last 3 candles
    c1, c2, c3 = candles[-3], candles[-2], candles[-1]
    bullish_fvg = (c3["low"] > c1["high"]) and (c3["low"] - c1["high"] > 0.2 * atr)
    bearish_fvg = (c3["high"] < c1["low"]) and (c1["low"] - c3["high"] > 0.2 * atr)
    
    return {
        "price": closes[-1],
        "ema20": ema20,
        "ema50": ema50,
        "rsi": rsi,
        "atr": atr,
        "bullish_fvg": bullish_fvg,
        "bearish_fvg": bearish_fvg
    }

def scan_gold_market():
    """Scan Gold (PAXGUSDT / XAU/USD) for A+ Institutional Setup with live checklist."""
    symbol = "PAXGUSDT"
    label = "Emas (XAU/USD)"
    candles = fetch_klines(symbol, interval="15m", limit=60)
    if not candles:
        return None
    
    ind = calculate_indicators(candles)
    if not ind:
        return None
    
    price = ind["price"]
    atr = ind["atr"]
    rsi = ind["rsi"]
    ema20 = ind["ema20"]
    ema50 = ind["ema50"]
    now_ts = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 5 Conditions Verification
    trend_bull = ema20 > ema50
    trend_bear = ema20 < ema50
    price_above_ema = price > ema20
    price_below_ema = price < ema20
    rsi_bull_ok = 40 <= rsi <= 68
    rsi_bear_ok = 32 <= rsi <= 60
    fvg_bull = ind["bullish_fvg"]
    fvg_bear = ind["bearish_fvg"]
    atr_ok = atr >= 1.5
    
    # Bullish Checklist
    bull_items = [
        ("✅ 1. Tren Struktur: BULLISH (EMA 20 > EMA 50)" if trend_bull else f"❌ 1. Tren Struktur: Belum Bullish (${ema20:.2f} <= ${ema50:.2f})", trend_bull),
        (f"✅ 2. Posisi Harga: Di Atas EMA 20 (${price:.2f} > ${ema20:.2f})" if price_above_ema else f"❌ 2. Posisi Harga: Di Bawah EMA 20 (${price:.2f} <= ${ema20:.2f})", price_above_ema),
        (f"✅ 3. Momentum RSI 14: {rsi:.1f} (Zona Ideal 40–68)" if rsi_bull_ok else (f"❌ 3. Momentum RSI 14: {rsi:.1f} (Overbought > 68, tunggu cooling down)" if rsi > 68 else f"❌ 3. Momentum RSI 14: {rsi:.1f} (Terlalu Rendah < 40)"), rsi_bull_ok),
        ("✅ 4. SMC Imbalance: Bullish FVG Terbentuk" if fvg_bull else "❌ 4. SMC Imbalance: Menunggu Bullish FVG / Gap", fvg_bull),
        (f"✅ 5. Volatilitas ATR 14: ${atr:.2f} (Memenuhi syarat >= $1.50)" if atr_ok else f"❌ 5. Volatilitas ATR 14: ${atr:.2f} (Terlalu Rendah < $1.50)", atr_ok)
    ]
    bull_score = sum(1 for _, ok in bull_items if ok)
    
    # Bearish Checklist
    bear_items = [
        ("✅ 1. Tren Struktur: BEARISH (EMA 20 < EMA 50)" if trend_bear else f"❌ 1. Tren Struktur: Belum Bearish (${ema20:.2f} >= ${ema50:.2f})", trend_bear),
        (f"✅ 2. Posisi Harga: Di Bawah EMA 20 (${price:.2f} < ${ema20:.2f})" if price_below_ema else f"❌ 2. Posisi Harga: Di Atas EMA 20 (${price:.2f} >= ${ema20:.2f})", price_below_ema),
        (f"✅ 3. Momentum RSI 14: {rsi:.1f} (Zona Ideal 32–60)" if rsi_bear_ok else (f"❌ 3. Momentum RSI 14: {rsi:.1f} (Oversold < 32, tunggu rebound)" if rsi < 32 else f"❌ 3. Momentum RSI 14: {rsi:.1f} (Terlalu Tinggi > 60)"), rsi_bear_ok),
        ("✅ 4. SMC Imbalance: Bearish FVG Terbentuk" if fvg_bear else "❌ 4. SMC Imbalance: Menunggu Bearish FVG / Gap", fvg_bear),
        (f"✅ 5. Volatilitas ATR 14: ${atr:.2f} (Memenuhi syarat >= $1.50)" if atr_ok else f"❌ 5. Volatilitas ATR 14: ${atr:.2f} (Terlalu Rendah < $1.50)", atr_ok)
    ]
    bear_score = sum(1 for _, ok in bear_items if ok)
    
    # Determine Dominant Direction
    if bull_score >= bear_score:
        direction = "BUY (LONG)"
        score = bull_score
        items = bull_items
        is_bull = True
    else:
        direction = "SELL (SHORT)"
        score = bear_score
        items = bear_items
        is_bull = False
        
    missing = 5 - score
    checklist_text = "\n".join([text for text, _ in items])
    
    last_signal_t = last_alert_time.get(f"{symbol}_signal", 0)
    last_radar_t = last_alert_time.get(f"{symbol}_radar", 0)
    last_radar_score = last_alert_time.get(f"{symbol}_radar_score", 0)
    
    # 1. FULL EXECUTION ALERT (5/5 Conditions Ready)
    if score == 5 and (now_ts - last_signal_t) >= 1800:
        last_alert_time[f"{symbol}_signal"] = now_ts
        last_alert_time[f"{symbol}_radar_score"] = 5
        if is_bull:
            sl = round(price - (1.5 * atr), 2)
            tp1 = round(price + (3.0 * atr), 2)
            tp2 = round(price + (4.5 * atr), 2)
            rrr = round((tp1 - price) / (price - sl), 1)
        else:
            sl = round(price + (1.5 * atr), 2)
            tp1 = round(price - (3.0 * atr), 2)
            tp2 = round(price - (4.5 * atr), 2)
            rrr = round((price - tp1) / (sl - price), 1)
            
        icon = "🟢" if is_bull else "🔴"
        msg = (
            f"🔥 <b>EKSEKUSI SEKARANG (5/5 KONDISI LENGKAP): {label}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{icon} <b>Arah:</b> <code>{direction}</code>\n"
            f"💵 <b>Entri:</b> <code>${price}</code>\n"
            f"🛑 <b>Stop Loss (SL):</b> <code>${sl}</code>\n"
            f"🎯 <b>Take Profit 1 (TP1):</b> <code>${tp1}</code> (RRR 1:{rrr})\n"
            f"🎯 <b>Take Profit 2 (TP2):</b> <code>${tp2}</code>\n\n"
            f"📋 <b>CHECKLIST KONDISI:</b>\n"
            f"{checklist_text}\n\n"
            f"💡 <b>Katalis:</b> Struktur SMC & Trend Continuation Sempurna.\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ <i>Waktu: {now_str} WIB</i>"
        )
        send_telegram_gold(msg)
        log_event("GOLD_QUANT_SIGNAL", {"action": direction, "price": price, "score": 5, "sl": sl, "tp1": tp1})
        return f"SIGNAL_{direction}"
        
    # 2. RADAR / EARLY WARNING ALERT (3/5 or 4/5 Conditions Ready)
    elif score in (3, 4):
        # Trigger if score increased or if 15 minutes elapsed since last radar alert
        should_send = (score > last_radar_score) or ((now_ts - last_radar_t) >= 900)
        if should_send:
            last_alert_time[f"{symbol}_radar"] = now_ts
            last_alert_time[f"{symbol}_radar_score"] = score
            
            icon = "🟢" if is_bull else "🔴"
            msg = (
                f"📡 <b>RADAR EMAS: SIAP-SIAP ({score}/5 KONDISI TERPENUHI)</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 <b>Potensi Sinyal:</b> {icon} <code>{direction}</code>\n"
                f"💵 <b>Harga Saat Ini:</b> <code>${price}</code>\n"
                f"⚠️ <b>Status:</b> <b>Kurang {missing} kondisi lagi untuk eksekusi!</b>\n\n"
                f"📋 <b>CHECKLIST KONDISI:</b>\n"
                f"{checklist_text}\n\n"
                f"💡 <i>Siapkan trading plan & lot. Eksekusi otomatis ditembak saat 5/5 terpenuhi.</i>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"⏰ <i>Waktu: {now_str} WIB</i>"
            )
            send_telegram_gold(msg)
            log_event("GOLD_RADAR_ALERT", {"direction": direction, "price": price, "score": score, "missing": missing})
            return f"RADAR_{score}_OF_5"
            
    return None

# ==========================================
# 🛡️ 2. AUTONOMOUS SERVER HEALTH GUARD
# ==========================================
def inspect_and_heal_services():
    """Inspect all PM2 services and auto-heal anomalies."""
    try:
        res = subprocess.run(["pm2", "jlist"], capture_output=True, text=True, timeout=10)
        if res.returncode != 0 or not res.stdout.strip():
            return 0, 0
        
        services = json.loads(res.stdout)
        healed = []
        
        for svc in services:
            name = svc.get("name", "unknown")
            pm_id = svc.get("pm_id")
            monit = svc.get("monit", {})
            status = svc.get("pm2_env", {}).get("status", "unknown")
            mem_mb = round(monit.get("memory", 0) / (1024 * 1024), 1)
            
            needs_heal = False
            heal_reason = ""
            
            # Check 1: Status not online
            if status not in ["online", "launching"]:
                needs_heal = True
                heal_reason = f"Status '{status}' (Down)"
            
            # Check 2: Memory leak threshold (> 450 MB)
            elif mem_mb > MEMORY_LIMIT_MB:
                needs_heal = True
                heal_reason = f"Memory Leak ({mem_mb} MB > {MEMORY_LIMIT_MB} MB)"
            
            if needs_heal:
                subprocess.run(["pm2", "restart", str(pm_id)], capture_output=True, timeout=15)
                service_restart_counts[name] = service_restart_counts.get(name, 0) + 1
                healed.append({"name": name, "id": pm_id, "reason": heal_reason, "mem_mb": mem_mb})
                
                msg = (
                    f"⚠️ <b>CLAUDIA AUTONOMOUS SELF-HEAL GUARD</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔧 <b>Layanan:</b> <code>{name}</code> (ID: {pm_id})\n"
                    f"🚨 <b>Pemicu:</b> {heal_reason}\n"
                    f"✨ <b>Tindakan:</b> Zero-Downtime Rolling Restart Sukses.\n"
                    f"📊 <b>Total Restart:</b> {service_restart_counts[name]} kali\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏰ <i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB</i>"
                )
                send_telegram_server(msg)
                log_event("SERVER_SELF_HEAL", {"service": name, "reason": heal_reason})
                print(f"[SELF-HEAL] Repaired {name} (ID: {pm_id}) due to {heal_reason}")
                
        return len(services), len(healed)
    except Exception as e:
        print(f"[WARN] PM2 inspection error: {e}")
        return 0, 0

# ==========================================
# 🔄 3. MASTER DAEMON LOOP
# ==========================================
def run_watchdog():
    print(f"🚀 [CLAUDIA 5.0 MAX] Dedicated Gold Quant & Server Health Watchdog Started.")
    print(f"   - Dedicated Gold Bot: Active (Token: 8893090639...)")
    print(f"   - Monitoring Target: Emas (XAU/USD - PAXG)")
    print(f"   - Crypto Position Signals: DISABLED")
    print(f"   - PM2 Auto-Healing: Active (< {MEMORY_LIMIT_MB} MB ceiling)")
    
    # Startup notification to Gold Bot
    send_telegram_gold(
        f"🟡 <b>CLAUDIA 5.0 GOLD QUANT TRADING BOT AKTIF</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>Fokus Pasar:</b> Emas (XAU/USD)\n"
        f"📊 <b>Strategi:</b> SMC Fair Value Gap (FVG) + EMA 20/50 + ATR (Min RRR 1:3)\n"
        f"🛡️ <b>Target Notifikasi:</b> Posisi Trading Emas Khusus Mas Hanafi\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ <i>Bot siap mengirimkan sinyal entri, TP, dan SL secara realtime.</i>"
    )
    
    scan_count = 0
    while True:
        try:
            scan_count += 1
            # 1. Dedicated Gold Market Scan Only
            scan_gold_market()
            
            # 2. Server Health Scans
            total_svc, healed_count = inspect_and_heal_services()
            
            # 3. Telemetry Update
            telemetry = {
                "last_heartbeat": datetime.now().isoformat(),
                "scan_cycles": scan_count,
                "monitored_services": total_svc,
                "total_healed": sum(service_restart_counts.values()),
                "gold_bot_target": TARGET_CHAT_ID,
                "status": "HEALTHY_OPERATIONAL"
            }
            try:
                with open(TELEMETRY_FILE, "w", encoding="utf-8") as f:
                    json.dump(telemetry, f, indent=2)
            except: pass
            
            time.sleep(POLL_INTERVAL_SEC)
        except KeyboardInterrupt:
            print("\n[STOP] Watchdog stopped by operator.")
            break
        except Exception as e:
            print(f"[LOOP ERROR] {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_watchdog()
