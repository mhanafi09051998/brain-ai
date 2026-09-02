# 🌊 Solana Second-Wave (Gunung Kedua) Trading Engine
> **Sistem Kuantitatif, Forensik On-Chain, & Studi Kasus Riil `$Boomer` (+75.8% Peak Gain)**

---

## 📌 1. Eksekutif Ringkasan (Executive Summary)

Pasar token dan memecoin di blockchain Solana bergerak dengan kecepatan ekstrem dalam hitungan menit. Mayoritas trader retail kehilangan modal karena terjebak di **Fase 1 (Sarang Sniper & MEV Bot)** atau membeli di **Fase 3 (Pucuk FOMO Retail)**.

Repository ini mendokumentasikan arsitektur, parameter matematis, dan studi kasus riil dari strategi **"Gunung Kedua" (*Second Wave Expansion*)** yang berhasil mengeksekusi perdagangan riil on-chain pada token **`$Boomer`** dengan lonjakan keuntungan puncak **`+75.8%`** dan realisasi *profit lock* menggunakan **Dynamic Trailing Stop**.

---

## 🏔️ 2. Filosofi & Anatomi Pola "Gunung Kedua" (*Wave 2 Anatomy*)

```
      [GUNUNG 1: BOT SNIPER & MEV]
              /\
             /  \
            /    \   ◄── (Sniper Jito & Bundler buang barang / DUMP)
           /      \       [KITA TIDAK PERNAH MASUK DI SINI]
          /        \
  ───────┘          \
                     \      [LEMBAH SUPPORT / TITIK PEMBERSIHAN]
                      \ ──► • Sniper sudah 100% habis buang barang
                             • Dev terverifikasi 0% & LP 100% Burned
                             • 40+ Smart Degen mulai akumulasi di lantai
                             ═════════════════════════════════════════════
                             🎯 TITIK MASUK BOT KITA (AWAL GUNUNG KEDUA)
                             ═════════════════════════════════════════════
                                      /  \
                                     /    \
                                    /      \   ◄── 🚀 [GUNUNG KEDUA: KITA TAKE PROFIT +80%]
                                   /        \         (Retail FOMO masuk menjadi Exit Liquidity kita)
                                  /          \
```

---

## 📊 3. Perbandingan 3 Fase Siklus Token Solana

```
═════════════════════════════════════════════════════════════════════════════════════════════════════
  [FASE 1: SNIPER / BOT MEV]   ➔   [FASE 2: KITA (SMART MONEY)]   ➔   [FASE 3: RETAIL FOMO]
       (Menit 0 - 3)                    (Menit 5 - 30)                    (Menit 30 - 2 Jam+)
    Market Cap: $5k - $60k            Market Cap: $70k - $220k           Market Cap: $300k - $1M+
─────────────────────────────────────────────────────────────────────────────────────────────────────
  • Bot Jito Bundle berebut        • Sniper sudah buang barang (dump)  • Masuk DexScreener Trending #1
  • 70% berisiko rugpull/scam      • Dev terverifikasi 0% & LP Burn    • Grup Telegram/Twitter FOMO
  • KITA MENONTON & FILTER         • KITA MASUK BERSAMA SMART DEGEN    • RETAIL JADI EXIT LIQUIDITY
                                   • Kunci Trailing Stop Dinamis       • KITA TAKE PROFIT & AMBIL SOL!
═════════════════════════════════════════════════════════════════════════════════════════════════════
```

---

## 🛡️ 4. Matriks 10 Parameter Masuk Berprobabilitas Tinggi (*High-Winrate Matrix*)

Setiap token yang ditembak oleh mesin otonom wajib lolos **10 Parameter Forensik & Kuantitatif**:

### A. Keamanan Kontrak (100% Anti-Rugpull)
1. **`Mint Authority`:** **`REVOKED (NULL)`** — Dev tidak bisa mencetak suplai token baru.
2. **`Freeze Authority`:** **`REVOKED (NULL)`** — Dompet bebas menjual kapan saja tanpa risiko dibekukan.
3. **`LP Burn Status`:** **`100% BURNED`** — Uang kolam likuiditas terkunci permanen di blockchain.
4. **`Honeypot Check`:** **`0 (CLEAN)`** — Tidak ada pajak tersembunyi (*tax fee*) saat swap.
5. **`Dev Team Holding`:** **`0.00%`** — Dev tidak memiliki alokasi token gratisan untuk melakukan dump.

### B. Struktur Pasar & Kecepatan Volume (*Sweet Spot*)
6. **`Zona Market Cap`:** **`$70.000 s.d. $220.000 MC`** — Zona ringan dan lincah (*Sweet Spot*).
7. **`Kedalaman Likuiditas Pool`:** **`≥ $15.000 s.d. $35.000+`** — Menjamin *slippage* rendah.
8. **`Kecepatan Volume (Volume Velocity)`:** **`≥ $60.000 per jam`** — Menghindari token lambat.

### C. Smart Money & Timing Eksekusi
9. **`Bundler Sniper Rate`:** **`≤ 18.0%`** — Pasokan bersih dari komplotan sniper bundler.
10. **`Akumulasi Smart Money`:** **`≥ 3 s.d. 50+ Dompet Smart Degen`** — Masuk bersama trader pro.
* **Bonus Timing (*Pullback Dip*):** **`-10% s.d. -55% dari ATH`** — Wajib masuk di kaki pantulan *support*.

---

## 🏆 5. Studi Kasus Riil: `$Boomer` (+75.8% Peak / +51.8% Realized)

### 📈 Fakta On-Chain Transaksi Riil:
* **Token:** **`Boomer ($Boomer)`**
* **Mint Address:** `99XjLY8VUSuwHcLcbTnqXvhwC3nWShMqqffamanAytMA`
* **Modal Masuk:** **`0.9997 SOL` (~$100.00 USD)**
* **Titik Entri:** **`$86.5k Market Cap`** *(Di kaki awal Gunung Kedua)*
* **Bukti On-Chain Pembelian:** [`Solscan Tx 2tU27kty8...81u`](https://solscan.io/tx/2tU27kty8SbkfR8ar3nRojxTUhuRxNZSmn3ysZYqWJeT1CCV5iXcMMVtqQDVbhCyCGLp2cExLuu5uV8aBkZDygro)

### 🚀 Perkembangan Pergerakan Harga:
1. **Menit Awal:** Sempat terkoreksi tipis ke `-5.27%` *(normal noise)* dan ditahan oleh support \$85k.
2. **Ledakan Volume Gunung Kedua:** Dalam 18 menit, harga melesat terbang ke **\$148.5k+ Market Cap (+75.8% PnL Peak)**.
3. **Eksekusi Trailing Stop:** Saat harga mencapai puncak dan terkoreksi 8%, sistem **Trailing Stop** otomatis memicu penjualan instan ke SOL di **`+51.8% Gain`**.
4. **Bukti On-Chain Penjualan:** [`Solscan Tx EJDNqCga...foc81u`](https://solscan.io/tx/EJDNqCgaZ3aYH1yUBs3Kg7dHCYgo25h21wPifhYqHsdscvB5WtpJ1qWnmjmv2q6jyrL3Xy4afE91MDfucfoc81u)
5. **Hasil Bersih:** Saldo modal bertambah menjadi **`1.5177 SOL` (~$152.00 USD)**.

---

## ⚙️ 6. Arsitektur Mesin Pengawalan Otomatis (Trailing Stop Math)

```javascript
// Algoritma Pengawalan Trailing Stop & Hard Targets
const currentPnlPct = (livePrice - entryPrice) / entryPrice;
const peakPnlPct = (highWatermark - entryPrice) / entryPrice;
const drawdownFromPeak = (highWatermark - livePrice) / highWatermark;

if (currentPnlPct <= -0.15) {
  // Hard Stop Loss: Memutus kerugian maksimal di -15% (<1 detik)
  executeExit('HARD_STOP_LOSS (-15%)');
} else if (peakPnlPct >= 0.12 && drawdownFromPeak >= 0.08) {
  // Trailing Stop: Aktif saat profit >= +12% dan mengunci jika turun 8% dari puncak
  executeExit(`TRAILING_STOP (Puncak: +${(peakPnlPct * 100).toFixed(2)}%, Retrace 8%)`);
} else if (currentPnlPct >= 0.80) {
  // Hard Take Profit: Auto-Exit 100% saat menyentuh target puncak +80%
  executeExit('HARD_TAKE_PROFIT (+80%)');
}
```

---

## 🔒 7. Proteksi Posisi Tunggal (*Single-Position Concurrency Guard*)

Mesin otonom menerapkan aturan ketat:
* **Maksimal 1 Posisi Terbuka:** Tidak ada *over-trading* atau membuka posisi kedua saat satu posisi sedang berjalan.
* **Cooldown 2 Jam per Token:** Mencegah pembelian ulang pada token yang baru saja keluar (*Anti-Churn*).
* **Notifikasi Telegram Otomatis:** Terhubung langsung ke Telegram untuk setiap aksi *Entry, Peak Milestone (+20%/+40%), dan Exit*.

---

*Dokumentasi ini dibuat sebagai referensi standar baku sistem kuantitatif trading Solana.*
