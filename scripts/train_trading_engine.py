#!/usr/bin/env python3
"""
Claudia Quantitative Gold (XAU/USD) & Crypto Trading Knowledge Engine
Pure Standard Library Implementation (Zero External Dependencies).
Fetches institutional market data, computes quant trading invariants (EMA, RSI, ATR, SMC/FVG),
and synthesizes Neuron N021 into the brain network.
"""

import os
import sys
import json
import math
import urllib.request
import datetime
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

def fetch_binance_klines(symbol="BTCUSDT", interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            raw = json.loads(res.read().decode("utf-8"))
            candles = []
            for r in raw:
                candles.append({
                    "open_time": int(r[0]),
                    "open": float(r[1]),
                    "high": float(r[2]),
                    "low": float(r[3]),
                    "close": float(r[4]),
                    "volume": float(r[5]),
                    "close_time": int(r[6])
                })
            return candles
    except Exception as e:
        print(f"[!] Warning: Failed to fetch {symbol} live klines: {e}")
        return []

def calculate_ema(prices, period=20):
    if len(prices) < period:
        return []
    k = 2 / (period + 1)
    ema = [sum(prices[:period]) / period]
    for p in prices[period:]:
        ema.append(p * k + ema[-1] * (1 - k))
    return ema

def calculate_rsi(prices, period=14):
    if len(prices) <= period:
        return 50.0
    gains, losses = [], []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        gains.append(max(0, change))
        losses.append(max(0, -change))
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    if avg_loss == 0:
        return 100.0
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def calculate_atr(candles, period=14):
    if len(candles) <= period:
        return 0.0
    tr_list = []
    for i in range(1, len(candles)):
        h = candles[i]["high"]
        l = candles[i]["low"]
        prev_c = candles[i-1]["close"]
        tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
        tr_list.append(tr)
    return round(sum(tr_list[-period:]) / period, 4)

def detect_smc_fair_value_gaps(candles):
    fvg_list = []
    for i in range(2, len(candles)):
        c1 = candles[i-2]
        c3 = candles[i]
        # Bullish FVG: Low of candle 3 is higher than High of candle 1
        if c3["low"] > c1["high"]:
            fvg_list.append({
                "type": "BULLISH_FVG",
                "gap_top": round(c3["low"], 2),
                "gap_bottom": round(c1["high"], 2),
                "timestamp": candles[i-1]["open_time"]
            })
        # Bearish FVG: High of candle 3 is lower than Low of candle 1
        elif c3["high"] < c1["low"]:
            fvg_list.append({
                "type": "BEARISH_FVG",
                "gap_top": round(c1["low"], 2),
                "gap_bottom": round(c3["high"], 2),
                "timestamp": candles[i-1]["open_time"]
            })
    return fvg_list[-5:]

def train_and_synthesize_neuron():
    print("🚀 [CLAUDIA QUANT TRADING TRAINING ENGINE]")
    print("[*] Mengunduh data pasar real-time & struktur kuantitatif...")
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    market_intelligence = {}
    
    for sym in symbols:
        candles = fetch_binance_klines(sym, interval="1h", limit=100)
        if not candles:
            continue
        closes = [c["close"] for c in candles]
        ema_20 = calculate_ema(closes, 20)
        ema_50 = calculate_ema(closes, 50)
        rsi_14 = calculate_rsi(closes, 14)
        atr_14 = calculate_atr(candles, 14)
        fvg = detect_smc_fair_value_gaps(candles)
        
        current_price = closes[-1]
        trend = "BULLISH" if (ema_20 and ema_50 and ema_20[-1] > ema_50[-1]) else "BEARISH"
        
        market_intelligence[sym] = {
            "current_price": current_price,
            "trend": trend,
            "rsi_14": rsi_14,
            "atr_14": atr_14,
            "recent_fvgs": fvg,
            "volatility_ratio": round((atr_14 / current_price) * 100, 3)
        }
        print(f"  [✓] {sym}: Price=${current_price:,.2f} | Trend={trend} | RSI={rsi_14} | ATR={atr_14}")

    # Synthesize Quantitative Gold & Crypto Invariants
    now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dataset_path = os.path.join(WORKSPACE, "learning", "frontier_datasets", "quant_trading_dataset.json")
    os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
    
    dataset_content = {
        "updated_at": now_iso,
        "asset_classes": ["Gold (XAU/USD)", "Cryptocurrency (BTC/ETH/SOL)"],
        "market_snapshot": market_intelligence,
        "invariants": {
            "risk_management": "Max 1-2% capital risk per trade. Minimum Risk-to-Reward 1:2.5.",
            "gold_macro_drivers": "Gold correlates inversely with US Dollar Index (DXY) and Real 10Y Yields. Breakouts confirmed by ATR expansion.",
            "smc_liquidity": "Trade direction confirmed by FVG retest + Order Block validation on 4H/1H timeframes."
        }
    }
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(dataset_content, f, indent=2)
    print(f"  [✓] Dataset kuantitatif tersimpan di: {dataset_path}")

    # Build Neuron N021
    neuron_path = os.path.join(WORKSPACE, "learning", "neurons", "N021_quantitative_gold_crypto_trading.md")
    neuron_md = f"""# N021: Quantitative Gold (XAU/USD) & Crypto Trading Systems

- **Kategori:** Quantitative Finance & Algorithmic Trading
- **Tanggal Pelatihan:** {now_iso}
- **Status:** Active Operational Invariant

---

## 🎯 Invarian Inti Perdagangan Kuantitatif (Trading Invariants)

### 1. Manajemen Risiko & Position Sizing (The Golden Law)
- **Max Risk per Trade:** Maksimal 1.0% – 2.0% dari total ekuitas portofolio.
- **Minimum Risk-to-Reward (RRR):** $1 : 2.5$ atau $1 : 3$. Posisi dengan RRR $< 1 : 2$ ditolak secara otomatis.
- **Dynamic Stop-Loss (ATR-based):** Stop Loss diset minimal $1.5 \\times \\text{{ATR}}(14)$ di luar level struktur kunci untuk menghindari *wick liquidity hunt*.

### 2. Logika Pasar Emas (XAU/USD Macro & Microstructure)
- **Korelasi Makro:** Emas berbanding terbalik dengan indeks DXY (US Dollar) dan imbal hasil riil US 10-Year Treasury Yield.
- **Volatilitas Sesi:** Likuiditas dan volume tertinggi terjadi saat *overlap* Sesi London & New York (19:00 – 23:00 WIB).
- **Konfirmasi Breakout:** Breakout level psikologis (misal round number 2600, 2700) wajib divalidasi oleh ekspansi volume dan penutupan candle 4H di luar zona supply/demand.

### 3. Logika Pasar Kripto & Smart Money Concepts (SMC)
- **Fair Value Gap (FVG):** Imbalance 3-candle di mana candle kedua menciptakan gap yang belum terisi (*unfilled liquidity*). Entry terbaik saat harga retest 50% zona FVG (*Consequent Encroachment*).
- **Order Block (OB):** Candle berlawanan terakhir sebelum pergerakan impulsif yang memecahkan struktur pasar (*Break of Structure / BOS*).
- **Funding Rate & Open Interest:** Funding rate positif ekstrem (>0.05%) mengindikasikan *overleveraged long* (potensi long squeeze).

---

## 💻 Algoritma Deterministik (Pure Python Implementation)
```python
def check_trade_entry(price, ema20, ema50, rsi, fvg_active):
    # Invariant: Trend Alignment + Momentum Reset + Structure Support
    is_bullish_trend = ema20 > ema50
    is_oversold_pullback = 40 <= rsi <= 52  # Pullback dalam tren naik
    return is_bullish_trend and is_oversold_pullback and fvg_active
```
"""
    with open(neuron_path, "w", encoding="utf-8") as f:
        f.write(neuron_md)
    print(f"  [✓] Neuron N021 tersintesis di: {neuron_path}")

    # Update Index
    index_path = os.path.join(WORKSPACE, "learning", "NEURON_INDEX.json")
    with open(index_path, "r", encoding="utf-8-sig") as f:
        idx_data = json.load(f)
    
    neurons = idx_data.get("neurons", [])
    if not any(n.get("id") == "N021" for n in neurons):
        neurons.append({
            "id": "N021",
            "label": "Neuron N021: Quantitative Gold (XAU/USD) & Crypto Trading Systems",
            "file": "N021_quantitative_gold_crypto_trading.md",
            "connections": ["N001", "N009", "N010", "N016"]
        })
        idx_data["neurons"] = neurons
        idx_data["total_neurons"] = len(neurons)
        idx_data["total_synapses"] = idx_data.get("total_synapses", 61) + 4
        idx_data["updated_at"] = now_iso
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(idx_data, f, indent=2, ensure_ascii=False)
        print(f"  [✓] NEURON_INDEX.json diperbarui ({len(neurons)} neuron aktif).")

    # Update memory.md
    mem_file = os.path.join(WORKSPACE, "memory.md")
    if os.path.exists(mem_file):
        with open(mem_file, "r", encoding="utf-8") as f:
            mem_text = f.read()
        if "N021_quantitative_gold_crypto_trading.md" not in mem_text:
            new_line = "19. **[`N021_quantitative_gold_crypto_trading.md`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N021_quantitative_gold_crypto_trading.md)** — **Quantitative Gold & Crypto Trading**: Invarian manajemen risiko RRR 1:3, ATR stop-loss, korelasi makro emas DXY, dan SMC/FVG liquidity.\n"
            if "## 🧠 Active Memory Neurons" in mem_text:
                parts = mem_text.split("## 🧠 Active Memory Neurons\n")
                with open(mem_file, "w", encoding="utf-8") as f:
                    f.write(parts[0] + "## 🧠 Active Memory Neurons\n" + new_line + parts[1])
                print("  [✓] memory.md disinkronkan.")

    # Run verification check
    print("[*] Menjalankan uji integritas pra-terbang...")
    subprocess.run([sys.executable, os.path.join(WORKSPACE, "scripts", "test_brain.py")])
    print("\n✨ PELATIHAN KUANTITATIF SELESAI & TERSINTESIS KE OTAK CLAUDIA.\n")

if __name__ == "__main__":
    train_and_synthesize_neuron()