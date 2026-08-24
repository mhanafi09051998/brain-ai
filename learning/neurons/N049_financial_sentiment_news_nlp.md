# Neuron N049: Financial Sentiment NLP & High-Impact Economic News Parsing

Prinsip arsitektur sub-second NLP & parsing kalender ekonomi makro (FOMC, CPI, NFP, GDP, PCE), klasifikasi polaritas Hawkish/Dovish kebijakan moneter bank sentral (Fed/ECB/BOJ/BOE), ekstraksi sinyal regulasi SEC/CFTC (Form 8-K, Form 4, Form 13F, CFTC COT), kuantifikasi sentimen sosial kripto (Twitter/Telegram velocity & volume-price divergence), serta engine alpha generation berlatensi rendah (<50ms) dengan dynamic risk guardrails:

- **Kategori**: Quantitative NLP, Macroeconomic News Engine, Financial Sentiment Mining & Event-Driven Trading Systems
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Membangun pipeline parsing berita ekonomi deterministik berlatensi sub-milidetik, menghitung Economic Surprise Index ($Z$-score), mengekstrak delta statemen moneter bank sentral berbasis N-gram & valence weighting, menganalisis filings regulator (SEC/CFTC COT) untuk institutional order flow, serta mendeteksi divergensi volume sentimen sosial kripto untuk menangkap alpha sebelum price discovery pasar selesai.
- **Synaptic Links**: [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N011`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N011_mechanical_sympathy_perf.md), [`N012`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N012_deep_search_and_graph_rag.md), [`N021`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N021_quantitative_gold_crypto_trading.md), [`N025`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N025_hft_orderbook_microstructure.md), [`N033`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N033_python_high_performance.md), [`N035`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N035_event_driven_streaming_cqrs.md)
- **Status**: Active Operational Invariant

---

## 🌐 1. High-Speed Macroeconomic Calendar Parsing & Economic Surprise Index

```
[ Raw News Stream / WebSocket Feed ] (Bloomberg / Reuters / RSS / API)
                │ (Wire Latency: 5-20ms)
                ▼
[ Zero-Alloc Regex & Tokenizer ] ────► [ Fast Indicator Matcher ] (CPI / NFP / FOMC / GDP)
                │ (Tokenization: < 0.5ms)
                ▼
[ Standardized Surprise Calculator ($Z$-Score) ]
      $Z = (\text{Actual} - \text{Consensus}) / \sigma_{\text{hist}}$
                │
                ├──────────────────────────────┬──────────────────────────────┐
                ▼                              ▼                              ▼
      [ FX / Rates Alpha ]             [ Gold (XAU/USD) ]             [ Crypto (BTC/ETH) ]
      DXY Spike / Yield Shift          Real Yield Transmission        Risk-On / Risk-Off Flow
                │                              │                              │
                └──────────────────────────────┴──────────────────────────────┘
                                               ▼
                              [ Spread & Liquidity Circuit Breaker ]
                                               ▼
                             [ Order Routing & Sub-50ms Execution ]
```

### 1.1. Invarian Kalender Ekonomi Berdampak Tinggi (High-Impact Macro Triggers)
Dalam pasar global, 90% pergerakan volatilitas ekstrem dalam 5 menit pertama rilis data makro dikendalikan oleh deviasi data terhadap konsensus pasar (*Consensus Expectation*):

1. **Federal Open Market Committee (FOMC)**:
   - **Federal Funds Rate Decision**: Target range (bps), perubahan suku bunga acuan.
   - **Summary of Economic Projections (SEP / Dot Plot)**: Proyeksi suku bunga terminal median anggota komite.
   - **Quantitative Tightening (QT) Pace**: Batas bulanan pengurangan neraca obligasi US Treasury & Mortgage-Backed Securities (MBS).
2. **Consumer Price Index (CPI) & Personal Consumption Expenditures (PCE)**:
   - **Headline YoY/MoM & Core YoY/MoM** (mengecualikan makanan dan energi yang volatil).
   - Invarian: *Core Inflation* yang lebih tinggi dari konsensus ($Z > +1.5$) memicu kenaikan yields obligasi 10-Tahun, memperkuat DXY, dan menekan harga Emas (XAU/USD) serta Aset Kripto (Risk-Off).
3. **Non-Farm Payrolls (NFP) & Labor Market**:
   - **Headline Net Job Additions** (ribuan tenaga kerja baru).
   - **Unemployment Rate (U3)** & **Average Hourly Earnings (MoM/YoY)** (tekanan inflasi upah).
   - Invarian: Laporan ketenagakerjaan yang *overheated* mengindikasikan suku bunga akan bertahan tinggi lebih lama (*higher for longer*).
4. **Gross Domestic Product (GDP) & Purchasing Managers Index (PMI)**:
   - ISM Manufacturing PMI & ISM Services PMI (>50 = Ekspansi, <50 = Kontraksi).

---

### 1.2. Standardized Economic Surprise Formula ($Z$-Score)
Setiap indikator memiliki skala dan volatilitas historis yang berbeda. Deviasi mentah ($\text{Actual} - \text{Consensus}$) wajib dinormalisasi terhadap standar deviasi deviasi historis ($\sigma_{\text{diff}}$) selama $N=24$ periode rilis sebelumnya:

$$\Delta_{\text{raw}} = \text{Actual} - \text{Consensus}$$

$$Z_{\text{surprise}} = \frac{\text{Actual} - \text{Consensus}}{\sigma_{\text{historical}}}$$

$$\text{Impact Factor } (\mathcal{I}) = w_{\text{indicator}} \cdot Z_{\text{surprise}}$$

Di mana $w_{\text{indicator}}$ merepresentasikan bobot sensitivitas aset:
- $w_{\text{CPI, Gold}} = -0.85$ (Kenaikan inflasi yang memicu kenaikan suku bunga riil menekan harga emas).
- $w_{\text{CPI, DXY}} = +0.90$ (Kenaikan inflasi memperkuat dolar AS).
- $w_{\text{NFP, BTC}} = -0.65$ (Pasar tenaga kerja yang terlalu kuat menunda pemotongan suku bunga).

---

## 🦅 2. Central Bank Hawkish / Dovish Token Classification & Statement Delta Diffing

Analisis pernyataan kebijakan moneter (*Monetary Policy Statements*) dan risalah rapat (*Meeting Minutes*) memerlukan pemahaman nuansa semantik finansial, pergeseran valensi kata (*valence shifters*), serta deteksi penyangkalan (*negation contexts*).

```
[ FOMC Statement $T$ ] ────┐
                           ├──► [ Clause-Level Syntactic Diff ] ──► [ Delta Stance Vector $\Delta \Theta$ ]
[ FOMC Statement $T-1$ ] ──┘                 │
                                             ▼
                             [ Valence & Negation Modifier ]
                             • "not ruling out rate hikes" ──► Hawkish (+0.8)
                             • "moderation in wage growth"  ──► Dovish  (-0.6)
                             • "remains highly attentive"   ──► Hawkish (+0.5)
```

### 2.1. Taksonomi Leksikon & Bobot Sentimen Moneter (Hawkish vs Dovish)

| Kategori Stance | Arah Kebijakan | Bobot ($V_i$) | Kata Kunci & Token Moneter | Dampak Pasar |
| :--- | :--- | :--- | :--- | :--- |
| **Hawkish Primer** | Pengetatan / Suku Bunga Naik | $+1.0 \text{ s/d } +2.0$ | `rate hike`, `tightening`, `restrictive stance`, `upside inflation risk`, `persistent price pressures`, `overheated labor`, `curb inflation`, `balance sheet reduction` | DXY Naik, Yields Naik, Emas Turun, Kripto Turun |
| **Hawkish Moderat** | Menahan Suku Bunga Tinggi | $+0.4 \text{ s/d } +0.9$ | `patient`, `higher for longer`, `vigilant`, `resilient economy`, `firmly committed`, `sufficiently restrictive` | DXY Menguat, Likuiditas Ketat |
| **Netral / Seimbang** | Data-Dependent | $0.0$ | `balanced risks`, `two-sided risks`, `data dependent`, `incoming information`, `carefully assess` | Volatilitas Menurun, Range Bound |
| **Dovish Moderat** | Perlambatan / Pause | $-0.4 \text{ s/d } -0.9$ | `cooling labor market`, `easing pressures`, `progress on inflation`, `modest pace`, `gradual adjustment`, `downside risks to growth` | Yields Turun, Gold/Equity Rebound |
| **Dovish Primer** | Pelonggaran / Suku Bunga Turun | $-1.0 \text{ s/d } -2.0$ | `rate cut`, `policy easing`, `accommodative stance`, `economic slowdown`, `recessionary risks`, `liquidity injection`, `emergency facility`, `target reduction` | DXY Anjlok, Emas Rally, Kripto Bullish |

---

### 2.2. Algoritma Pergeseran Valensi & Penyangkalan (Contextual Valence Shifting)
Model berbasis leksikon naif (*bag-of-words*) gagal jika bertemu kalimat majemuk dengan kata sanggahan:
- *"The Committee does **not** see evidence of persistent inflation"* $\implies$ Berubah dari Hawkish menjadi **Dovish**.
- *"We are **not ruling out** additional rate hikes"* $\implies$ Double negative menghasilkan **Hawkish**.

Aturan Penilaian Kalimat:
$$\text{Score}(S) = \sum_{k=1}^M \left( \prod_{j \in \text{Modifiers}(k)} \mu_j \right) \cdot \text{Polarity}(T_k)$$

Di mana:
- $\mu = -1.0$ untuk kata negasi (`not`, `never`, `hardly`, `scarcely`, `no`, `fails to`, `without`).
- $\mu = +1.5$ untuk kata penguat (*intensifiers*: `extremely`, `firmly`, `exceptionally`, `substantially`).
- $\mu = +0.5$ untuk kata pereda (*diminishers*: `somewhat`, `marginally`, `slightly`, `gradually`).

---

### 2.3. Differential Statement Parsing ($\Delta \Theta$)
Setiap pertemuan FOMC menghasilkan teks pengumuman yang 95% identik dengan teks bulan sebelumnya. Alpha berada pada klausa baru yang ditambahkan (*insertions*) dan klausa lama yang dihapus (*deletions*):

$$\Delta \Theta = \sum_{c \in \text{Additions}} \text{Score}(c) - \sum_{c \in \text{Deletions}} \text{Score}(c)$$

Jika $\Delta \Theta > +0.75 \implies$ **Hawkish Shift** instan; jika $\Delta \Theta < -0.75 \implies$ **Dovish Pivot**.

---

## 📑 3. Regulatory Filings & Institutional Positioning Signals (SEC & CFTC)

Informasi struktural dari institusi besar dan *insiders* diatur dalam laporan regulasi wajib yang memberikan sinyal sebelum tren makro jangka menengah terkonfirmasi.

```
                  ┌───► [ SEC Form 8-K ]  ──► Material Corporate Catalyst / Restatement
                  │
[ Filing Streams ]├───► [ SEC Form 4 ]    ──► Insider Cluster Buying vs Scheduled 10b5-1
                  │
                  ├───► [ SEC Form 13F ]  ──► Tier-1 Institutional Asset Rebalancing
                  │
                  └───► [ CFTC COT Report]──► Commercial vs Speculator Extremes ($Z > 2.0$)
```

### 3.1. SEC EDGAR Feed: Form 8-K, Form 4, Form 13F
1. **Form 8-K (Material Corporate Events)**:
   - **Item 1.01**: *Entry into a Material Definitive Agreement* (M&A, kemitraan strategis bernilai besar).
   - **Item 2.02**: *Results of Operations and Financial Condition* (Pengumuman laba tak terjadwal).
   - **Item 4.02**: *Non-Reliance on Previously Issued Financial Statements* (Restatement akuntansi - *Sinyal Short Keras / Fraud Alert*).
   - **Item 5.02**: *Departure of Directors or Principal Officers* (Pengunduran diri CEO/CFO mendadak).
2. **Form 4 (Insider Transactions)**:
   - **Cluster Buying Invariant**: Jika $\ge 3$ eksekutif level C (CEO, CFO, CTO, Direktur) membeli saham biasa di pasar terbuka (*Open Market Purchase, Transaction Code `P`*) dalam jendela waktu 7 hari kerja tanpa adanya *Rule 10b5-1 pre-planned trading plan*, probabilitas alpha positif 30-hari mencapai $>72\%$.
   - Formulasi Rasio Insider Cluster:
     $$\text{CBR} = \frac{\sum V_{\text{Open Market Buy}}}{\sum V_{\text{Open Market Sell}} + \epsilon}$$
3. **Form 13F (Institutional Investment Managers)**:
   - Melacak portofolio pengelola dana $\ge \$100\text{M}$ secara triwulanan. Ekstraksi rotasi sektor dari aset berisiko tinggi ke obligasi/komoditas emas.

---

### 3.2. CFTC Commitments of Traders (COT) Positioning Imbalance
Setiap hari Jumat, Commodity Futures Trading Commission (CFTC) merilis data posisi terbuka kontrak berjangka (Emas COMEX, Minyak WTI, S&P500 e-mini, Bitcoin CME):

1. **Komponen Pelaku Pasar**:
   - **Commercial Hedgers (Smart Money Producers/Merchants)**: Menggunakan derivatif untuk hedging bisnis nyata.
   - **Non-Commercial Speculators (Managed Money / Hedge Funds)**: Trend-following quants dan spekulan arah harga.
2. **COT Sentiment Index (52-Week Percentile)**:
   $$\text{COT Index}_t = \frac{\text{Net Pos}_t - \min_{52w}(\text{Net Pos})}{\max_{52w}(\text{Net Pos}) - \min_{52w}(\text{Net Pos})} \times 100$$
   Di mana $\text{Net Pos} = \text{Long Contracts} - \text{Short Contracts}$.
3. **Invarian Reversal Sinyal Ekstrem**:
   - Jika $\text{COT Index}_{\text{Speculators}} > 92\%$ (Extreme Long Crowding) dan $\text{COT Index}_{\text{Commercials}} < 8\% \implies$ **Pasar Jenuh Beli / Rentan Terhadap Long Squeeze**.
   - Jika $\text{COT Index}_{\text{Speculators}} < 8\%$ (Extreme Short) $\implies$ **Potensi Short Squeeze / Titik Balik Akumulasi**.

---

## ⚡ 4. Crypto Social Sentiment Alpha, Velocity & Narrative Mining

Pasar aset digital didorong oleh likuiditas ritel dan pergeseran narasi (*narrative velocity*) yang tercermin dalam media sosial (Twitter/X, Telegram, Discord, Reddit, Farcaster).

```
[ Social Firehose Stream ] ────► [ Cashtag & Token Entity Extraction ] ($BTC, $SOL, etc.)
                                                 │
                                 ┌───────────────┴───────────────┐
                                 ▼                               ▼
                      [ Social Velocity $V_{\text{soc}}$ ]   [ Sentiment Polarity $\mathcal{P}$ ]
                                 │                               │
                                 └───────────────┬───────────────┘
                                                 ▼
                               [ Volume-Price Divergence Detector ]
                                                 ▼
                     [ Sinyal: Bullish Accumulation vs Blow-Off Top ]
```

### 4.1. Metrik Kecepatan Sosial (Social Velocity & Burst Detection)
Lonjakan volume sosial mendadak menandakan masuknya perhatian massa (*attention capture*):

$$V_{\text{social}}(t) = \frac{N(t, t-\Delta t) - \mu_N(7d)}{\sigma_N(7d)}$$

Di mana $N(t, t-\Delta t)$ adalah jumlah posting unik dalam jendela 15 menit, dan $\mu_N, \sigma_N$ adalah rata-rata serta deviasi standar 7 hari.

---

### 4.2. Santiment & LunarCrush Volume-Price Divergence Invariant
1. **Bullish Social Accumulation**:
   - Harga bergerak datar (*sideways consolidation*) atau turun tipis, tetapi kecepatan sentimen positif dan jumlah kreator unik meningkat drastis ($V_{\text{social}} > +2.0$, Sentimen Positif $> 70\%$).
   - Sinyal: *Organic narrative formation sebelum harga terpompa*.
2. **FOMO Blow-Off Top & Liquidation Warning**:
   - Harga mengalami apresiasi vertikal ($> +15\%$ dalam 24 jam) disertai $V_{\text{social}} > +4.0$, sentimen euforia ekstrem ($>90\%$ Bullish), dan Open Interest berjangka meningkat dengan Funding Rate $> +0.05\%$.
   - Sinyal: *Retail exit liquidity trap $\implies$ Antisipasi Long Squeeze*.
3. **FUD & Regulatory Black Swan Filtering**:
   - Kata kunci kritis: `insolvency`, `hack`, `exploit`, `sec subpoena`, `freeze withdrawals`, `exploit vector`.
   - Deteksi darurat dalam $<50\text{ms}$ untuk mengeksekusi *Emergency Delta Hedge* atau de-leveraging posisi spot/perpetual.

---

## 🛡️ 5. Algorithmic Trading Signal Generation & Execution Guardrails

```
[ Macro Surprise ] ──┐
[ Hawkish/Dovish ] ──┼──► [ Alpha Factor Synthesizer ] ──► [ Volatility Filter & Circuit Breaker ]
[ SEC / COT Flow ] ──┤                  │                                 │
[ Social Alpha   ] ──┘                  ▼                                 ▼
                              [ Net Alpha Score $\alpha \in [-1, 1]$ ]   [ Order Routing Execution ]
```

### 5.1. Komposisi Skor Alpha Multi-Faktor
$$\alpha_{\text{total}} = w_1 \cdot Z_{\text{macro}} + w_2 \cdot \Delta \Theta_{\text{central\_bank}} + w_3 \cdot \mathcal{S}_{\text{institutional}} + w_4 \cdot \mathcal{S}_{\text{crypto\_social}}$$

Di mana $\sum w_i = 1.0$ dan $\alpha_{\text{total}} \in [-1.0, +1.0]$.

### 5.2. Guardrail Eksekusi Saat Berita Berdampak Tinggi (Shock Circuit Breakers)
1. **Spread Widening Protection**:
   - Saat rilis data NFP atau CPI, spread Bid-Ask broker/CEX dapat melebar $5\text{--}20\times$.
   - Invarian: Jika $\text{Spread}_{\text{current}} > 3.0 \times \text{Spread}_{\text{median}(5m)}$, **larang eksekusi Market Order**; gunakan Limit Order dengan Stoikov Micro-Price offset untuk mencegah *instant negative slippage*.
2. **Dynamic Volatility Position Sizing**:
   - Ukuran posisi di-scale berbanding terbalik terhadap volatilitas implisit saat berita:
     $$\text{Size}_{\text{news}} = \text{Size}_{\text{base}} \times \min\left(1.0, \frac{\text{ATR}_{\text{normal}}}{\text{ATR}_{\text{event}}}\right)$$
3. **Execution Latency Budget**:
   - Total waktu dari paket jaringan masuk $\to$ NLP Tokenizer $\to$ Sinyal $\to$ Order Gateway wajib $< 50\text{ms}$.

---

## 💻 6. Zero-Dependency Stdlib Python Implementation & Self-Check

Modul produksi murni Python stdlib berikut mengintegrasikan:
1. **`EconomicCalendarParser`**: Fast regex parser untuk rilis data makro dengan normalisasi $Z$-Score.
2. **`HawkishDovishNLPClassifier`**: Tokenizer klausa moneter dengan valence shifters, modifier context, dan differential statement scoring.
3. **`SECFilingAndCOTAnalyzer`**: Parser Form 8-K material events, Form 4 insider cluster buys, dan 52-week CFTC COT Index percentile.
4. **`CryptoSocialSentimentEngine`**: Detektor lonjakan kecepatan sosial ($Z$-Score velocity) dan volume-price divergence.
5. **`EventDrivenAlphaPipeline`**: Mesin sintetis pengambil keputusan multi-aset dengan proteksi spread widening.
6. **`main()` Test Suite**: Validasi deterministik 100% lulus untuk semua kasus uji.

```python
"""
Neuron N049: Financial Sentiment NLP & High-Impact Economic News Parsing Engine.
Zero external dependencies. Pure Python stdlib test suite.
"""

from typing import Dict, List, Tuple, Optional, Any
import math
import re
import json


class EconomicCalendarParser:
    """
    Sub-second Macroeconomic Calendar & Surprise Index Engine.
    Computes standardized Z-score deviations across major economic indicators.
    """
    def __init__(self):
        # Historical standard deviations of surprise (Actual - Consensus) over rolling 24 releases
        self.historical_std: Dict[str, float] = {
            "CPI_HEADLINE_YOY": 0.20,  # in percentage points
            "CPI_CORE_MOM": 0.10,
            "NFP_HEADLINE": 65.0,      # in thousands (e.g. 65k standard deviation)
            "UNEMPLOYMENT_RATE": 0.15,
            "FOMC_RATE_DECISION": 12.5, # in basis points
            "GDP_QOQ": 0.40,
            "ISM_MANUFACTURING": 1.20
        }

    def compute_surprise(self, indicator: str, actual: float, consensus: float) -> Tuple[float, float]:
        """
        Returns (raw_surprise, standardized_z_score).
        Z = (Actual - Consensus) / sigma_historical
        """
        raw_surprise = actual - consensus
        sigma = self.historical_std.get(indicator, 1.0)
        if sigma <= 0:
            sigma = 1.0
        z_score = raw_surprise / sigma
        return round(raw_surprise, 4), round(z_score, 4)

    def parse_fast_wire(self, raw_wire_text: str) -> Optional[Dict[str, Any]]:
        """
        Zero-allocation regex extraction of economic wire releases.
        Example: "US CPI (YoY) Actual: 3.2% vs Consensus: 2.9% Prev: 3.0%"
        """
        cpi_match = re.search(r"US CPI \(YoY\)\s+Actual:\s*([\d\.]+)%?\s+vs\s+Consensus:\s*([\d\.]+)%", raw_wire_text, re.IGNORECASE)
        if cpi_match:
            actual = float(cpi_match.group(1))
            consensus = float(cpi_match.group(2))
            raw_s, z = self.compute_surprise("CPI_HEADLINE_YOY", actual, consensus)
            return {
                "indicator": "CPI_HEADLINE_YOY",
                "actual": actual,
                "consensus": consensus,
                "raw_surprise": raw_s,
                "z_score": z,
                "macro_bias": "HAWKISH_INFLATION" if z > 0.5 else ("DOVISH_INFLATION" if z < -0.5 else "IN_LINE")
            }

        nfp_match = re.search(r"US Non-Farm Payrolls\s+Actual:\s*(\-?[\d\.]+)k?\s+vs\s+Consensus:\s*(\-?[\d\.]+)k?", raw_wire_text, re.IGNORECASE)
        if nfp_match:
            actual = float(nfp_match.group(1))
            consensus = float(nfp_match.group(2))
            raw_s, z = self.compute_surprise("NFP_HEADLINE", actual, consensus)
            return {
                "indicator": "NFP_HEADLINE",
                "actual": actual,
                "consensus": consensus,
                "raw_surprise": raw_s,
                "z_score": z,
                "macro_bias": "STRONG_LABOR" if z > 0.5 else ("WEAK_LABOR" if z < -0.5 else "IN_LINE")
            }
        return None


class HawkishDovishNLPClassifier:
    """
    Central Bank Monetary Policy Stance & Statement Delta NLP Classifier.
    Handles n-grams, contextual negation modifiers, and differential statement diffing.
    """
    def __init__(self):
        # Lexicon with base polarity scores [-2.0 to +2.0]
        self.lexicon: Dict[str, float] = {
            "rate hike": 1.5,
            "hike": 1.2,
            "tightening": 1.4,
            "restrictive": 1.3,
            "persistent inflation": 1.5,
            "overheated": 1.2,
            "curb inflation": 1.3,
            "balance sheet reduction": 1.4,
            "higher for longer": 1.6,
            "vigilant": 0.8,
            "firmly committed": 1.0,
            
            "rate cut": -1.5,
            "cut": -1.2,
            "easing": -1.4,
            "accommodative": -1.3,
            "cooling labor": -1.1,
            "progress on inflation": -1.2,
            "moderation in wage": -1.3,
            "downside risks": -1.2,
            "recessionary": -1.4,
            "economic slowdown": -1.3,
            "gradual adjustment": -0.8
        }
        
        self.negations = {"not", "never", "hardly", "scarcely", "no", "fails to", "without"}
        self.intensifiers = {"extremely": 1.5, "firmly": 1.4, "substantially": 1.3, "highly": 1.3}
        self.diminishers = {"somewhat": 0.6, "slightly": 0.5, "marginally": 0.5, "gradually": 0.7}

    def score_sentence(self, sentence: str) -> float:
        """
        Scores sentence stance with valence shifters and sliding window context.
        Positive = Hawkish, Negative = Dovish.
        """
        clean_text = sentence.lower().strip()
        tokens = re.findall(r"\b[\w\-]+\b", clean_text)
        if not tokens:
            return 0.0

        total_score = 0.0
        n = len(tokens)
        i = 0
        while i < n:
            matched = False
            # Check 3-gram, 2-gram, 1-gram in lexicon
            for gram_len in (3, 2, 1):
                if i + gram_len <= n:
                    gram = " ".join(tokens[i:i+gram_len])
                    if gram in self.lexicon:
                        base_val = self.lexicon[gram]
                        
                        # Lookback 3 tokens for negation or intensifier
                        lookback_start = max(0, i - 3)
                        prefix_tokens = tokens[lookback_start:i]
                        
                        multiplier = 1.0
                        for p in prefix_tokens:
                            if p in self.negations:
                                multiplier *= -1.0
                            elif p in self.intensifiers:
                                multiplier *= self.intensifiers[p]
                            elif p in self.diminishers:
                                multiplier *= self.diminishers[p]
                        
                        total_score += base_val * multiplier
                        i += gram_len
                        matched = True
                        break
            if not matched:
                i += 1

        return round(total_score, 4)

    def diff_statements(self, old_stmt: str, new_stmt: str) -> Dict[str, Any]:
        """
        Performs clause-level statement diffing between successive FOMC releases.
        Returns net stance delta: Stance(Additions) - Stance(Deletions).
        """
        old_clauses = set([s.strip().lower() for s in re.split(r"[\.\n;]", old_stmt) if len(s.strip()) > 5])
        new_clauses = set([s.strip().lower() for s in re.split(r"[\.\n;]", new_stmt) if len(s.strip()) > 5])

        added = new_clauses - old_clauses
        deleted = old_clauses - new_clauses

        score_added = sum(self.score_sentence(c) for c in added)
        score_deleted = sum(self.score_sentence(c) for c in deleted)
        
        # Delta Stance = Additions - Deletions
        net_delta = score_added - score_deleted
        
        stance = "NEUTRAL"
        if net_delta >= 0.75:
            stance = "HAWKISH_PIVOT"
        elif net_delta <= -0.75:
            stance = "DOVISH_PIVOT"

        return {
            "net_stance_delta": round(net_delta, 4),
            "stance": stance,
            "added_count": len(added),
            "deleted_count": len(deleted),
            "added_score": round(score_added, 4),
            "deleted_score": round(score_deleted, 4)
        }


class SECFilingAndCOTAnalyzer:
    """
    Regulatory Filings (SEC Form 8-K / Form 4) & CFTC Commitments of Traders (COT) Analyzer.
    """
    def __init__(self):
        self.item_8k_risk_map = {
            "1.01": ("MATERIAL_AGREEMENT", 0.6),
            "2.02": ("EARNINGS_ANNOUNCEMENT", 0.0), # Needs metric parsing
            "4.02": ("ACCOUNTING_RESTATEMENT", -1.8), # Severe Red Flag
            "5.02": ("C_SUITE_DEPARTURE", -0.9)
        }

    def analyze_form_8k(self, item_code: str, summary_text: str) -> Dict[str, Any]:
        """Classifies Form 8-K material corporate event risk."""
        label, base_sentiment = self.item_8k_risk_map.get(item_code, ("OTHER_MATERIAL", 0.0))
        # Check text qualifiers
        if "resigned immediately" in summary_text.lower() or "investigation" in summary_text.lower():
            base_sentiment -= 0.5
        if "transformational merger" in summary_text.lower() or "accretive" in summary_text.lower():
            base_sentiment += 0.5
            
        return {
            "item_code": item_code,
            "event_type": label,
            "event_sentiment": round(base_sentiment, 2),
            "action_bias": "STRONG_SELL" if base_sentiment <= -1.0 else ("BUY" if base_sentiment >= 1.0 else "NEUTRAL")
        }

    def analyze_form_4_insider_cluster(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes insider open-market transactions for cluster buying alpha.
        Transaction Code 'P' = Open Market Purchase, 'S' = Open Market Sale.
        """
        total_buy_vol = 0.0
        total_sell_vol = 0.0
        distinct_buyers = set()
        c_suite_titles = {"CEO", "CFO", "CTO", "COO", "PRESIDENT", "DIRECTOR"}

        for tx in transactions:
            role = tx.get("role", "").upper()
            code = tx.get("code", "")
            shares = float(tx.get("shares", 0))
            price = float(tx.get("price", 0))
            value = shares * price

            is_c_suite = any(t in role for t in c_suite_titles)
            if code == "P" and is_c_suite:
                total_buy_vol += value
                distinct_buyers.add(tx.get("insider_name", "unknown"))
            elif code == "S":
                total_sell_vol += value

        # Cluster Buying Ratio
        cbr = total_buy_vol / (total_sell_vol + 1.0)
        is_cluster_buy = (len(distinct_buyers) >= 3 and total_buy_vol > 500_000.0)

        return {
            "cluster_buying_detected": is_cluster_buy,
            "distinct_c_suite_buyers": len(distinct_buyers),
            "total_buy_usd": round(total_buy_vol, 2),
            "total_sell_usd": round(total_sell_vol, 2),
            "cbr_ratio": round(cbr, 2),
            "alpha_signal": "INSIDER_ACCUMULATION_BULLISH" if is_cluster_buy else "NORMAL_INSIDER_FLOW"
        }

    def calculate_cftc_cot_index(self, net_positions_52w: List[float], current_net_position: float) -> Dict[str, Any]:
        """
        Calculates 52-week percentile COT Index.
        COT Index = (Current - Min) / (Max - Min) * 100
        """
        if not net_positions_52w:
            return {"cot_index": 50.0, "status": "INSUFFICIENT_DATA"}
            
        min_pos = min(net_positions_52w)
        max_pos = max(net_positions_52w)
        if max_pos == min_pos:
            cot_idx = 50.0
        else:
            cot_idx = ((current_net_position - min_pos) / (max_pos - min_pos)) * 100.0

        cot_idx = max(0.0, min(100.0, cot_idx))
        
        status = "NEUTRAL"
        if cot_idx >= 90.0:
            status = "EXTREME_OVERBOUGHT_CROWDED_LONG"
        elif cot_idx <= 10.0:
            status = "EXTREME_OVERSOLD_CROWDED_SHORT"

        return {
            "cot_index": round(cot_idx, 2),
            "current_net": current_net_position,
            "min_52w": min_pos,
            "max_52w": max_pos,
            "reversal_risk": status
        }


class CryptoSocialSentimentEngine:
    """
    Crypto Social Velocity & Volume-Price Divergence Alpha Engine.
    """
    def __init__(self):
        self.crypto_bull_words = {"bull", "moon", "breakout", "gem", "undervalued", "accumulate", "pump", "rally"}
        self.crypto_bear_words = {"scam", "dump", "rug", "bear", "rekt", "crash", "insolvent", "hack", "exploit"}

    def compute_social_velocity(self, current_15m_count: int, hist_7d_mean: float, hist_7d_std: float) -> float:
        """Computes standardized social volume burst Z-score."""
        if hist_7d_std <= 0:
            return 0.0
        z_vel = (current_15m_count - hist_7d_mean) / hist_7d_std
        return round(z_vel, 2)

    def analyze_social_stream(self, messages: List[str]) -> Tuple[float, float]:
        """Returns (sentiment_score [-1 to 1], positive_ratio [0 to 1])."""
        if not messages:
            return 0.0, 0.5

        pos_count = 0
        neg_count = 0
        for msg in messages:
            tokens = set(re.findall(r"\b\w+\b", msg.lower()))
            has_pos = bool(tokens & self.crypto_bull_words)
            has_neg = bool(tokens & self.crypto_bear_words)
            if has_pos and not has_neg:
                pos_count += 1
            elif has_neg and not has_pos:
                neg_count += 1

        total_sentiment_msgs = pos_count + neg_count
        if total_sentiment_msgs == 0:
            return 0.0, 0.5

        polarity = (pos_count - neg_count) / total_sentiment_msgs
        pos_ratio = pos_count / total_sentiment_msgs
        return round(polarity, 2), round(pos_ratio, 2)

    def evaluate_divergence(self, price_change_24h_pct: float, velocity_z: float, pos_ratio: float) -> str:
        """
        Identifies social volume vs price action divergences.
        """
        # Condition 1: Bullish Organic Accumulation (Price Flat/Down, High Social Velocity + Bullish Sentiment)
        if -3.0 <= price_change_24h_pct <= 2.0 and velocity_z >= 2.0 and pos_ratio >= 0.70:
            return "BULLISH_SOCIAL_ACCUMULATION"
        
        # Condition 2: FOMO Blow-Off Top / Liquidation Risk (Price Up Big, Extreme Velocity + Euphoria)
        if price_change_24h_pct >= 15.0 and velocity_z >= 3.5 and pos_ratio >= 0.85:
            return "BLOWOFF_TOP_LONG_SQUEEZE_RISK"
            
        # Condition 3: Panic Capitulation / Bottom Hunt (Price Down Big, High Velocity + Extreme Fear)
        if price_change_24h_pct <= -15.0 and velocity_z >= 3.0 and pos_ratio <= 0.20:
            return "CAPITULATION_BOTTOM_WATCH"

        return "NORMAL_FLOW"


class EventDrivenAlphaPipeline:
    """
    Synthesizes Macro NLP, Sentiment Signals, and Risk Guardrails for Order Execution.
    """
    def __init__(self):
        self.cal_parser = EconomicCalendarParser()
        self.nlp_classifier = HawkishDovishNLPClassifier()
        self.sec_cot = SECFilingAndCOTAnalyzer()
        self.crypto_engine = CryptoSocialSentimentEngine()

    def generate_gold_macro_signal(self, cpi_wire: str, spread_bps: float, max_allowed_spread_bps: float = 8.0) -> Dict[str, Any]:
        """
        Evaluates CPI release for Gold (XAU/USD) algorithmic response with spread widening guardrails.
        """
        parsed = self.cal_parser.parse_fast_wire(cpi_wire)
        if not parsed or parsed.get("indicator") != "CPI_HEADLINE_YOY":
            return {"action": "HOLD", "reason": "NO_VALID_CPI_TRIGGER"}

        z = parsed["z_score"]
        # Gold Invariant: CPI Surprise > +1.0 -> Yields & DXY spike -> Short Gold
        # CPI Surprise < -1.0 -> Yields fall -> Long Gold
        raw_direction = "SHORT_XAU" if z >= 1.0 else ("LONG_XAU" if z <= -1.0 else "NO_TRADE")

        # Circuit Breaker: Spread Check
        if spread_bps > max_allowed_spread_bps:
            return {
                "action": "BLOCKED_CIRCUIT_BREAKER",
                "intended_direction": raw_direction,
                "reason": f"Spread ({spread_bps} bps) exceeded threshold ({max_allowed_spread_bps} bps)",
                "z_score": z
            }

        return {
            "action": "EXECUTE_IMMEDIATE",
            "direction": raw_direction,
            "instrument": "XAU/USD",
            "z_score": z,
            "confidence": min(1.0, abs(z) / 3.0),
            "order_type": "LIMIT_MICROPRICE_CROSS"
        }


# ============================================================================
# DETERMINISTIC INVARIANT TEST SUITE
# ============================================================================

def run_tests():
    print("Executing Neuron N049 Invariant Validation Suite...")

    # --- Test 1: Economic Calendar Surprise Calculation & Wire Parsing ---
    cal = EconomicCalendarParser()
    raw_s, z = cal.compute_surprise("CPI_HEADLINE_YOY", actual=3.4, consensus=3.0)
    assert raw_s == 0.4, f"Expected raw surprise 0.4, got {raw_s}"
    assert z == 2.0, f"Expected Z-score 2.0, got {z}"

    # Wire Regex Parsing
    wire = "BREAKING: US CPI (YoY) Actual: 3.5% vs Consensus: 3.1% Prev: 3.2%"
    parsed = cal.parse_fast_wire(wire)
    assert parsed is not None, "Failed to parse CPI wire"
    assert parsed["indicator"] == "CPI_HEADLINE_YOY"
    assert parsed["actual"] == 3.5
    assert parsed["consensus"] == 3.1
    assert parsed["z_score"] == 2.0
    assert parsed["macro_bias"] == "HAWKISH_INFLATION"
    print("  [PASS] Test 1: Economic Calendar Surprise Z-score & Wire Parser.")

    # --- Test 2: Hawkish / Dovish Token Classification & Negation Handling ---
    nlp = HawkishDovishNLPClassifier()
    # Direct Hawkish
    s1 = "The Committee sees persistent inflation and remains firmly committed to a rate hike."
    score1 = nlp.score_sentence(s1)
    assert score1 > 2.0, f"Expected strong Hawkish score > 2.0, got {score1}"

    # Negation Context (Reverses Hawkish token to Dovish)
    s2 = "The Committee does not see persistent inflation."
    score2 = nlp.score_sentence(s2)
    assert score2 < 0.0, f"Expected negative (dovish) score due to negation, got {score2}"

    # Direct Dovish
    s3 = "We observed progress on inflation and cooling labor conditions, justifying a rate cut."
    score3 = nlp.score_sentence(s3)
    assert score3 < -2.0, f"Expected strong Dovish score < -2.0, got {score3}"

    # Statement Diffing
    old_stmt = "Inflation remains elevated and the Committee is vigilant about upside inflation risks."
    new_stmt = "Inflation has made progress towards target and the Committee notes moderation in wage growth."
    diff_res = nlp.diff_statements(old_stmt, new_stmt)
    assert diff_res["stance"] == "DOVISH_PIVOT", f"Expected DOVISH_PIVOT, got {diff_res['stance']}"
    assert diff_res["net_stance_delta"] < -1.0
    print("  [PASS] Test 2: Hawkish/Dovish Lexicon, Negation Context & Statement Diffing.")

    # --- Test 3: SEC Filings (Form 8-K & Form 4 Insider Clusters) & CFTC COT ---
    sec_cot = SECFilingAndCOTAnalyzer()
    
    # 8-K Red Flag
    f8k = sec_cot.analyze_form_8k("4.02", "Company announces non-reliance on previously issued financial statements due to accounting investigation.")
    assert f8k["action_bias"] == "STRONG_SELL"
    assert f8k["event_sentiment"] < -1.5

    # Form 4 Cluster Buy
    tx_data = [
        {"insider_name": "Alice (CEO)", "role": "CEO", "code": "P", "shares": 50000, "price": 20.0},
        {"insider_name": "Bob (CFO)", "role": "CFO", "code": "P", "shares": 30000, "price": 20.0},
        {"insider_name": "Charlie (Director)", "role": "Director", "code": "P", "shares": 25000, "price": 20.0},
        {"insider_name": "Dave (VP)", "role": "VP", "code": "S", "shares": 1000, "price": 20.0}
    ]
    f4_res = sec_cot.analyze_form_4_insider_cluster(tx_data)
    assert f4_res["cluster_buying_detected"] is True
    assert f4_res["distinct_c_suite_buyers"] == 3
    assert f4_res["alpha_signal"] == "INSIDER_ACCUMULATION_BULLISH"

    # CFTC COT Index
    hist_52w = [10000.0, 20000.0, 50000.0, 80000.0, 100000.0]
    cot_res_high = sec_cot.calculate_cftc_cot_index(hist_52w, current_net_position=95000.0)
    assert cot_res_high["cot_index"] > 90.0
    assert cot_res_high["reversal_risk"] == "EXTREME_OVERBOUGHT_CROWDED_LONG"
    print("  [PASS] Test 3: SEC 8-K, Form 4 Insider Clusters & CFTC COT Percentile.")

    # --- Test 4: Crypto Social Sentiment & Divergence ---
    crypto = CryptoSocialSentimentEngine()
    msgs = [
        "Massive breakout incoming for $BTC gem accumulate now!",
        "$BTC looking bullish and undervalued",
        "Moon soon $BTC"
    ]
    pol, pos_r = crypto.analyze_social_stream(msgs)
    assert pol == 1.0
    assert pos_r == 1.0

    # Bullish Divergence Detection
    div_sig = crypto.evaluate_divergence(price_change_24h_pct=-0.5, velocity_z=2.5, pos_ratio=0.80)
    assert div_sig == "BULLISH_SOCIAL_ACCUMULATION"

    # Blow-Off Top Detection
    blowoff_sig = crypto.evaluate_divergence(price_change_24h_pct=22.0, velocity_z=4.2, pos_ratio=0.92)
    assert blowoff_sig == "BLOWOFF_TOP_LONG_SQUEEZE_RISK"
    print("  [PASS] Test 4: Crypto Social Sentiment Velocity & Divergence Detector.")

    # --- Test 5: End-to-End Event-Driven Pipeline & Risk Guardrails ---
    pipeline = EventDrivenAlphaPipeline()
    hot_cpi = "US CPI (YoY) Actual: 3.6% vs Consensus: 3.0%"
    
    # Normal Spread -> Execution Allowed
    order_exec = pipeline.generate_gold_macro_signal(hot_cpi, spread_bps=3.5, max_allowed_spread_bps=8.0)
    assert order_exec["action"] == "EXECUTE_IMMEDIATE"
    assert order_exec["direction"] == "SHORT_XAU"
    assert order_exec["z_score"] == 3.0

    # Blown Spread -> Circuit Breaker Triggered
    order_blocked = pipeline.generate_gold_macro_signal(hot_cpi, spread_bps=12.5, max_allowed_spread_bps=8.0)
    assert order_blocked["action"] == "BLOCKED_CIRCUIT_BREAKER"
    assert order_blocked["intended_direction"] == "SHORT_XAU"
    print("  [PASS] Test 5: Event-Driven Macro Execution & Spread Guardrails.")

    print("\n[SUCCESS] All Neuron N049 Invariant Tests Completed Deterministically!")

if __name__ == "__main__":
    run_tests()
```
