# N021: Quantitative Gold (XAU/USD) & Crypto Trading Systems

- **Kategori:** Quantitative Finance & Algorithmic Trading
- **Tanggal Pelatihan:** 2026-08-24 18:28:54
- **Status:** Active Operational Invariant

---

## 🎯 Invarian Inti Perdagangan Kuantitatif (Trading Invariants)

### 1. Manajemen Risiko & Position Sizing (The Golden Law)
- **Max Risk per Trade:** Maksimal 1.0% – 2.0% dari total ekuitas portofolio.
- **Minimum Risk-to-Reward (RRR):** $1 : 2.5$ atau $1 : 3$. Posisi dengan RRR $< 1 : 2$ ditolak secara otomatis.
- **Dynamic Stop-Loss (ATR-based):** Stop Loss diset minimal $1.5 \times \text{ATR}(14)$ di luar level struktur kunci untuk menghindari *wick liquidity hunt*.

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
