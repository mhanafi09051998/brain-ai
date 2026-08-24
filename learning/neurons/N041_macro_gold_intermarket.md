# Neuron N041: Macroeconomic Regime & Gold Intermarket Dynamics

Prinsip kuantitatif intermarket komprehensif untuk XAU/USD (Gold) berbasis imbal hasil riil TIPS 10-Year, regresi multivariat DXY Index, jalur suku bunga FOMC/CPI (Taylor Rule & SOFR Futures), metrik *crowding* CFTC Commitments of Traders (COT), dan dinamika arus cadangan emas fisik Bank Sentral (*Sovereign De-Dollarization*):

- **Kategori**: Quantitative Macroeconomics, Intermarket Analysis, Sovereign Flow Modeling & Precious Metals Asset Pricing
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Menegakkan invarian kuantitatif penetapan harga emas global lintas rezim makroekonomi; mengisolasi elastisitas suku bunga riil (*TIPS 10Y*) dan mata uang (*DXY*); merekonstruksi probabilitas kebijakan FOMC dan ekspektasi inflasi (*Breakeven Inflation*); melacak titik jenuh posisi spekulatif (*CFTC COT Z-score*); memodelkan *structural price floor* dari akumulasi bank sentral global (*unreported OTC & PBOC flows*); dan menyediakan mesin sintetis penentuan rezim makro (*Regime-Switching Macro Engine*) yang sepenuhnya deterministik.
- **Synaptic Links**: [`N001`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N001_executive_decisions.md), [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N017`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N017_program_aided_math.md), [`N021`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N021_quantitative_gold_crypto_trading.md), [`N025`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N025_hft_orderbook_microstructure.md), [`N033`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N033_python_high_performance.md), [`N040`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N040_meta_cognitive_self_reflection.md)
- **Status**: Active Operational Invariant

---

## 1. TIPS 10-Year Real Yields & The Fisher Opportunity Cost Engine

```
                             [ Nominal 10Y UST Yield (i) ]
                                          │
                        ┌─────────────────┴─────────────────┐
                        ▼                                   ▼
             [ TIPS 10Y Real Yield (r) ]        [ 10Y Breakeven Inflation (π_e) ]
             (Opportunity Cost of Bullion)      (Market Inflation Expectation)
                        │
                        ▼
             ┌──────────────────────────────────────────────┐
             │ Inverse Relationship Engine:                 │
             │ r ↓ (< 0.5%)  ──► Gold Convex Expansion (▲▲) │
             │ r ↑ (> 2.0%)  ──► Gold Valuation Drag   (▼)  │
             │ *Fiscal Dominance Exception: Both r ↑ & XAU ↑│
             └──────────────────────────────────────────────┘
```

### A. Fisher Equation & Breakeven Inflation (BEI)
1. **Dekomposisi Imbal Hasil Nominal**:
   $$i_{10Y} = r_{\text{TIPS}, 10Y} + \pi_e + \rho_{\text{liq}}$$
   di mana:
   - $i_{10Y}$: Nominal 10-Year US Treasury yield.
   - $r_{\text{TIPS}, 10Y}$: 10-Year Treasury Inflation-Protected Securities (TIPS) yield (proksi suku bunga riil bebas risiko).
   - $\pi_e = \text{BEI}_{10Y}$: 10-Year Breakeven Inflation Rate ($i_{10Y} - r_{\text{TIPS}}$).
   - $\rho_{\text{liq}}$: TIPS Liquidity Premium term (biasanya $5 - 15\text{ bps}$).

2. **Opportunity Cost Invariant**:
   - Emas fisik adalah aset nir-kupon (*zero-yielding asset*) dengan *carrying cost* (penyimpanan & asuransi $\approx 10 - 25\text{ bps/tahun}$).
   - Ketika suku bunga riil $r_{\text{TIPS}} > 0$, memegang emas menimbulkan *opportunity cost* sebesar $r_{\text{TIPS}} - (-\text{carry})$.
   - Korelasi standar historis: $\text{Corr}(\Delta \ln(P_{\text{XAU}}), \Delta r_{\text{TIPS}}) \in [-0.75, -0.92]$.
   - *Durasi Emas*: Emas memiliki durasi kuasi-abadi (*perpetual duration* $\approx 30 - 50$ tahun terhadap suku bunga riil).

3. **Non-Linear Convexity & Negative Real Yield Supercycle**:
   - Saat $r_{\text{TIPS}} < 0\%$, aset obligasi memberikan imbal hasil riil negatif (destruksi daya beli modal).
   - Permintaan emas mengalami akselerasi non-linear (*convexity shift*): sensitivitas harga terhadap penurunan yield meningkat tajam ($\frac{\partial^2 P}{\partial r^2} > 0$).

---

## 2. Multi-Asset DXY Regression & Purchasing Power Numeraire

```
                 [ DXY Currency Basket (EUR 57.6%, JPY 13.6%, GBP 11.9%, CAD 9.1%, SEK 4.2%, CHF 3.6%) ]
                                                        │
                                                        ▼
                        ┌───────────────────────────────────────────────────────────┐
                        │ Multi-Factor OLS Calibration:                             │
                        │ Δ ln(P_XAU) = α + β_TIPS · Δr_real + β_DXY · Δ ln(DXY) + ε│
                        └─────────────────────────────┬─────────────────────────────┘
                                                      │
                         ┌────────────────────────────┴────────────────────────────┐
                         ▼                                                         ▼
           [ Beta Residual: Pure USD FX Effect ]                     [ Unexplained Alpha: α_structural ]
           (Numeraire mechanical adjustment)                        (Geopolitical & Central Bank Demand)
```

### A. DXY Index Composition & FX Numeraire Effect
1. **Formulasi Geometris DXY**:
   $$\text{DXY} = 50.14348112 \times \text{EURUSD}^{-0.576} \times \text{USDJPY}^{0.136} \times \text{GBPUSD}^{-0.119} \times \text{USDCAD}^{0.091} \times \text{USDSEK}^{0.042} \times \text{USDCHF}^{0.036}$$
2. **Numeraire vs Fundamental Demand**:
   - Karena XAU dihargai dalam USD per troy ounce, penurunan $1\%$ pada DXY secara mekanis meningkatkan harga XAU/USD sebesar $+1\%$ (*ceteris paribus*), mempertahankan nilai konstan dalam EUR/JPY/GBP.
   - Jika $\Delta \ln(P_{\text{XAU}}) > -\beta_{\text{DXY}} \cdot \Delta \ln(\text{DXY})$, terjadi *Global Bullion Expansion* di mana emas terapresiasi terhadap *seluruh* mata uang fiat utama secara simultan (*broad-based currency debasement*).

### B. Ordinary Least Squares (OLS) Calibration & Structural Alpha
1. **Regresi Multi-Faktor Makro**:
   $$R_{t}^{\text{XAU}} = \alpha + \beta_{\text{TIPS}} \Delta r_{t}^{\text{TIPS}} + \beta_{\text{DXY}} R_{t}^{\text{DXY}} + \epsilon_t$$
   di mana:
   - $\beta_{\text{TIPS}} \in [-15.0, -35.0]$ (perubahan return $100\text{ bps}$ real yield $\implies 15\% - 35\%$ perubahan harga).
   - $\beta_{\text{DXY}} \in [-0.8, -1.3]$ (elastisitas mata uang).
   - $\alpha > 0$ mengindikasikan premi moneter struktural (*Sovereign Accumulation & Geopolitical Hedge*).
2. **Kondisi Normal Equations Tanpa Dependensi**:
   $$\mathbf{\beta} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{Y}$$
   Diselesaikan melalui eliminasi Gauss-Jordan dengan *partial pivoting* untuk stabilitas numerik floating-point $O(K^3)$.

---

## 3. FOMC Interest Rate Path, Taylor Rule & Inflation Dynamics

```
[ CPI YoY / Core PCE (π) ]  ──┐
                              ├─► [ Taylor Rule Benchmark i* ] ──┐
[ Output Gap / Labor (y-y*) ] ──┘                                 │
                                                                 ▼
[ 30-Day Fed Funds Futures / SOFR ] ──► [ Implied Policy Rate ] ──► [ Policy Surprise S_FOMC ]
                                                                             │
                                   ┌─────────────────────────────────────────┴────────┐
                                   ▼                                                  ▼
                        [ Hawkish Shock: S > 0 ]                           [ Dovish Shock: S < 0 ]
                        (TIPS ↑, DXY ↑, XAU Drag)                          (TIPS ↓, DXY ↓, XAU Surge)
```

### A. Taylor Rule Specification & Policy Gap
1. **Klasik Taylor Rule (1993)**:
   $$i^* = r^* + \pi_t + 0.5(\pi_t - \pi^*) + 0.5(y_t - y^*)$$
   di mana:
   - $r^*$: Neutral real interest rate ($\approx 0.5\% - 1.25\%$).
   - $\pi^*$: Fed inflation target ($2.0\%$).
   - $\pi_t$: Headline CPI / Core PCE YoY.
   - $y_t - y^*$: GDP Output Gap / Unemployment Gap proksi via Okun's Law: $-(u_t - u_n) \times 2.0$.
2. **Policy Restriction Ratio**:
   $$\text{Gap}_{\text{policy}} = i_{\text{FedFunds}} - i^*$$
   - $\text{Gap}_{\text{policy}} > +100\text{ bps} \implies$ Kebijakan moneter restriktif ekstrem (tekanan disinflasi $\implies$ batas atas yield riil tercapai $\implies$ pivot akumulasi emas).
   - $\text{Gap}_{\text{policy}} < -100\text{ bps} \implies$ Kebijakan moneter berada di belakang kurva (*behind the curve* / *financial repression* $\implies$ katalis *bullish* agresif bagi emas).

### B. SOFR / Fed Funds Futures Implied Probabilities
1. **Harga Kontrak Berjangka 30-Hari**:
   $$P_{\text{FFF}} = 100 - \bar{r}_{\text{implied}}$$
2. **Policy Surprise Score**:
   $$S_{\text{FOMC}} = i_{\text{actual}} - i_{\text{implied}}$$

---

## 4. CFTC Commitments of Traders (COT) Positioning & Sentiment Squeeze

```
[ Commercial Hedgers (Producers/Refiners) ] ◄── Smart Money (Value Floor)
                     ▲
                     │ Market Balance
                     ▼
[ Managed Money (CTAs, Macro Funds) ]       ◄── Trend Followers (Sentiment Extremes)
                     │
                     ▼
       ┌───────────────────────────┐
       │ 52-Week Rolling Z-Score:  │
       │ Z_COT > +2.0 ──► Overcrowded Long (Exhaustion Risk)
       │ Z_COT < -2.0 ──► Washed-Out Short (Squeeze Setup)
       └───────────────────────────┘
```

### A. Dekomposisi Kategori Laporan Disaggregated COT (COMEX Gold)
1. **Managed Money (Spekulan Terbuka / CTAs)**:
   - Posisi Net: $\text{Net}_{\text{MM}} = \text{Long}_{\text{MM}} - \text{Short}_{\text{MM}}$.
   - Menunjukkan momentum spekulatif institusional. Rentan terhadap *stop-cascade liquidations*.
2. **Commercial Producers & Merchants (Smart Money)**:
   - Posisi Net: $\text{Net}_{\text{Comm}} = \text{Long}_{\text{Comm}} - \text{Short}_{\text{Comm}}$ (umumnya net short untuk *hedging* tambang).
   - Ketika $\text{Net}_{\text{Comm}}$ bergerak mendekati net positive atau ekstrem berkurang, mengindikasikan produsen fisik menolak melakukan *forward selling* pada harga rendah (*structural bottom*).

### B. 52-Week Percentile Rank & Standardized Z-Score
1. **Rolling Z-Score**:
   $$Z_{\text{COT}} = \frac{\text{Net}_{\text{MM}, t} - \mu_{52}(\text{Net}_{\text{MM}})}{\sigma_{52}(\text{Net}_{\text{MM}})}$$
2. **Speculative Crowding Index (SCI)**:
   $$\text{SCI} = \frac{\text{Long}_{\text{MM}}}{\text{Long}_{\text{MM}} + \text{Short}_{\text{MM}}} \in [0.0, 1.0]$$
   - $\text{SCI} > 0.85$ dan $Z_{\text{COT}} > +2.0 \implies$ *Extreme Bullish Crowding* (asimetri risiko negatif untuk long baru).
   - $\text{SCI} < 0.25$ dan $Z_{\text{COT}} < -2.0 \implies$ *Extreme Bearish Capitulation* (asimetri risiko sangat positif untuk *long reversal*).

---

## 5. Central Bank Physical Reserve Flows & Sovereign De-Dollarization

```
[ Sovereign Reserve Diversification Demand ]
(PBoC, CBR, RBI, NBG, Central Banks Worldwide)
                     │
                     ├─────────────────────────────────────────────────┐
                     ▼                                                 ▼
      [ Reported Official Purchases (IMF IFS / WGC) ]    [ Unreported OTC Bullion Outflows ]
      (Transparent Monthly Gold Accumulation)             (LBMA/Swiss Physical Refineries)
                     │                                                 │
                     └────────────────────────┬────────────────────────┘
                                              │
                                              ▼
                         [ Structural Gold Floor Invariant ]
           (Price-Inelastic Sovereign Bid decoupled from TIPS Yields)
```

### A. Sovereign Reserve Share & De-Dollarization Index
1. **Pangsa Emas dalam Cadangan Devisa**:
   $$\text{Gold Share} = \frac{P_{\text{XAU}} \times Q_{\text{Gold}}}{P_{\text{XAU}} \times Q_{\text{Gold}} + \sum \text{FX}_{\text{reserves}}}$$
2. **Inelasticity Invariant (TIPS Decoupling)**:
   - Bank sentral (terutama negara-negara BRICS+) mengakumulasi emas fisik bukan untuk mencari yield kupon jangka pendek, melainkan sebagai aset cadangan moneter bebas risiko penyitaan sanksi (*Sanction-Proof Tier-1 Sovereign Asset*).
   - Akumulasi ini menciptakan *price-inelastic demand floor*: bahkan saat $r_{\text{TIPS}}$ naik, harga emas tidak jatuh sebanding model historis karena aliran pembelian fisik langsung menyerap pasokan tambang tahunan ($\approx 3,600\text{ ton/tahun}$).

---

## 6. Macroeconomic Regime Classification Matrix

| Rezim Makroekonomi | Real Yield ($r_{\text{TIPS}}$) | DXY Index | Inflasi ($\pi_e$) | Aliran Bank Sentral | Dampak XAU/USD | Strategi Posisi Claudia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Stagflation** | Jatuh / Negatif | Netral / Melemah | Meningkat Tajam | Agresif | **Ultra Bullish (🚀🚀)** | Max Leveraged Long / Long Calls |
| **2. Fiat Debasement / Fiscal Dominance** | Meningkat lambat | Melemah | Tinggi / Persisten | Ekstrem | **Strong Bullish (📈📈)** | Core Long Spot / Dip Buying |
| **3. Disinflationary Boom** | Naik Tinggi | Menguat | Rendah ($< 2\%$) | Moderat | **Bearish Drag (📉)** | Delta Neutral / Short Hedge |
| **4. Liquidity Crisis / Deflationary Shock** | Volatil / Spike | Melonjak Tajam | Runtuh | Pasif | **Initial Drop -> V-Reversal** | Cash Waiting -> Aggressive Dip Buy |

---

## 7. Zero-Dependency Python 3.12+ Macro & Gold Intermarket Engine

Implementasi deterministik lengkap mencakup pemodelan Fisher TIPS, solver regresi multivariat OLS murni, simulasi Taylor Rule FOMC, penganalisis CFTC COT, pelacak cadangan Bank Sentral, dan sintesis rezim makro:

```python
"""
Neuron N041: Macroeconomic Regime & Gold Intermarket Dynamics Engine
Standard Library Only (Zero External Dependencies, Pure Math & Linear Algebra).
"""

import math
import sys
from typing import Dict, List, Tuple, Optional, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ============================================================================
# 1. Pure Python Linear Algebra (Matrix Inversion & OLS Multi-Factor Solver)
# ============================================================================

class MatrixMath:
    """Zero-dependency matrix operations and Gauss-Jordan linear solver."""

    @staticmethod
    def transpose(matrix: List[List[float]]) -> List[List[float]]:
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0
        return [[matrix[r][c] for r in range(rows)] for c in range(cols)]

    @staticmethod
    def matmul(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        rows_a = len(a)
        cols_a = len(a[0])
        rows_b = len(b)
        cols_b = len(b[0])
        if cols_a != rows_b:
            raise ValueError(f"Matrix dimension mismatch: ({rows_a}x{cols_a}) * ({rows_b}x{cols_b})")
        
        result = [[0.0] * cols_b for _ in range(rows_a)]
        for i in range(rows_a):
            for k in range(cols_a):
                elem_a = a[i][k]
                for j in range(cols_b):
                    result[i][j] += elem_a * b[k][j]
        return result

    @staticmethod
    def invert(matrix: List[List[float]]) -> List[List[float]]:
        """Inverts an NxN matrix using Gauss-Jordan elimination with partial pivoting."""
        n = len(matrix)
        for row in matrix:
            if len(row) != n:
                raise ValueError("Matrix must be square for inversion")

        # Augment matrix with identity matrix: [A | I]
        aug = [matrix[i][:] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        for col in range(n):
            # Pivot selection
            max_row = col
            max_val = abs(aug[col][col])
            for r in range(col + 1, n):
                if abs(aug[r][col]) > max_val:
                    max_val = abs(aug[r][col])
                    max_row = r

            if max_val < 1e-12:
                raise ValueError("Singular matrix cannot be inverted")

            aug[col], aug[max_row] = aug[max_row], aug[col]

            # Scale pivot row to 1.0
            pivot = aug[col][col]
            for c in range(2 * n):
                aug[col][c] /= pivot

            # Eliminate column values in other rows
            for r in range(n):
                if r != col:
                    factor = aug[r][col]
                    for c in range(2 * n):
                        aug[r][c] -= factor * aug[col][c]

        return [[aug[i][j + n] for j in range(n)] for i in range(n)]


class OLSMacroRegression:
    """
    Ordinary Least Squares Multi-Factor Regression Engine.
    Solves beta = (X^T * X)^(-1) * X^T * Y.
    """
    def __init__(self, feature_names: List[str]):
        self.feature_names = ["Intercept"] + feature_names
        self.coefficients: List[float] = []
        self.r_squared: float = 0.0
        self.std_err: float = 0.0

    def fit(self, x_data: List[List[float]], y_data: List[float]) -> "OLSMacroRegression":
        n_samples = len(y_data)
        if n_samples < len(self.feature_names):
            raise ValueError("Insufficient data points for regression degrees of freedom")

        # Add intercept column (1.0)
        x_design = [[1.0] + row for row in x_data]
        y_col = [[y] for y in y_data]

        x_t = MatrixMath.transpose(x_design)
        xt_x = MatrixMath.matmul(x_t, x_design)
        xt_x_inv = MatrixMath.invert(xt_x)
        xt_y = MatrixMath.matmul(x_t, y_col)
        beta_col = MatrixMath.matmul(xt_x_inv, xt_y)

        self.coefficients = [beta_col[i][0] for i in range(len(beta_col))]

        # Calculate R-squared and error residuals
        y_mean = sum(y_data) / n_samples
        ss_tot = sum((y - y_mean) ** 2 for y in y_data)
        ss_res = 0.0
        for i in range(n_samples):
            pred = self.predict_single(x_data[i])
            ss_res += (y_data[i] - pred) ** 2

        self.r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-12 else 0.0
        self.std_err = math.sqrt(ss_res / max(1, n_samples - len(self.coefficients)))
        return self

    def predict_single(self, x_row: List[float]) -> float:
        val = self.coefficients[0]  # Intercept
        for j in range(len(x_row)):
            val += self.coefficients[j + 1] * x_row[j]
        return val


# ============================================================================
# 2. TIPS Real Yield & Fisher Opportunity Cost Model
# ============================================================================

class FisherTIPSModel:
    """Analyzes real interest rates, breakeven inflation, and gold yield elasticity."""

    @staticmethod
    def calculate_real_yield(nominal_10y: float, tips_10y: float) -> Dict[str, float]:
        """
        nominal_10y: nominal 10-year Treasury yield in percentage (e.g. 4.25 for 4.25%)
        tips_10y: 10-year TIPS yield in percentage (e.g. 1.85 for 1.85%)
        """
        breakeven_inflation = nominal_10y - tips_10y
        return {
            "nominal_10y": nominal_10y,
            "tips_10y_real": tips_10y,
            "breakeven_inflation": breakeven_inflation,
            "is_negative_real_rate": tips_10y < 0.0,
            "financial_repression_risk": breakeven_inflation > nominal_10y
        }

    @staticmethod
    def estimate_gold_yield_impact(delta_real_yield_bps: float, base_beta: float = -0.22) -> float:
        """
        Estimates expected gold price percentage shift from TIPS yield change in basis points.
        base_beta: approx -0.22% gold return per +10 bps real yield shift (-22x duration).
        """
        pct_yield_shift = delta_real_yield_bps / 10.0
        return pct_yield_shift * base_beta


# ============================================================================
# 3. FOMC Taylor Rule & Fed Policy Stance Engine
# ============================================================================

class FOMCPolicyOracle:
    """Evaluates Federal Reserve monetary stance, Taylor Rule benchmark, and rate surprises."""

    @staticmethod
    def taylor_rule_rate(
        cpi_inflation: float,
        output_gap: float,
        r_star: float = 1.0,
        target_inflation: float = 2.0
    ) -> float:
        """
        Taylor Rule (1993): i* = r* + pi + 0.5*(pi - pi*) + 0.5*output_gap
        """
        inflation_gap = cpi_inflation - target_inflation
        return r_star + cpi_inflation + 0.5 * inflation_gap + 0.5 * output_gap

    @staticmethod
    def evaluate_policy_stance(
        current_fed_funds: float,
        taylor_rate: float,
        market_implied_rate: float
    ) -> Dict[str, Any]:
        policy_gap = current_fed_funds - taylor_rate
        market_surprise = current_fed_funds - market_implied_rate

        if policy_gap >= 0.50:
            stance = "OVERLY_RESTRICTIVE"
            macro_bias = "PIVOT_ACCUMULATION"
        elif policy_gap <= -0.50:
            stance = "BEHIND_THE_CURVE"
            macro_bias = "DEBASEMENT_ACCELERATION"
        else:
            stance = "NEUTRAL_BALANCED"
            macro_bias = "RANGEBOUND"

        return {
            "current_fed_funds": current_fed_funds,
            "taylor_benchmark": round(taylor_rate, 3),
            "policy_gap": round(policy_gap, 3),
            "market_surprise": round(market_surprise, 3),
            "stance": stance,
            "macro_bias": macro_bias
        }


# ============================================================================
# 4. CFTC Commitments of Traders (COT) Positioning Analyzer
# ============================================================================

class CFTCCOTAnalyzer:
    """Analyzes speculative crowding and smart-money positioning from CFTC reports."""

    @staticmethod
    def analyze_positioning(
        managed_money_long: int,
        managed_money_short: int,
        commercial_long: int,
        commercial_short: int,
        historical_net_spec_52w: List[int]
    ) -> Dict[str, Any]:
        net_spec = managed_money_long - managed_money_short
        net_comm = commercial_long - commercial_short
        total_spec = managed_money_long + managed_money_short

        spec_crowding_idx = managed_money_long / total_spec if total_spec > 0 else 0.5

        # Calculate 52-week Z-Score
        if historical_net_spec_52w:
            n = len(historical_net_spec_52w)
            mean_net = sum(historical_net_spec_52w) / n
            variance = sum((x - mean_net) ** 2 for x in historical_net_spec_52w) / n
            std_dev = math.sqrt(variance) if variance > 0 else 1.0
            z_score = (net_spec - mean_net) / std_dev

            # Percentile rank
            lower_count = sum(1 for x in historical_net_spec_52w if x <= net_spec)
            percentile = (lower_count / n) * 100.0
        else:
            z_score = 0.0
            percentile = 50.0

        # Sentiment exhaustion classification
        if z_score > 2.0 or spec_crowding_idx > 0.85:
            sentiment_regime = "OVERHEATED_LONG_CROWDING"
            position_action = "TRIM_OR_HEDGE_LONGS"
        elif z_score < -2.0 or spec_crowding_idx < 0.25:
            sentiment_regime = "EXTREME_BEARISH_CAPITULATION"
            position_action = "AGGRESSIVE_LONG_REVERSAL"
        else:
            sentiment_regime = "NORMAL_POSITIONING"
            position_action = "FOLLOW_MACRO_TREND"

        return {
            "net_speculative": net_spec,
            "net_commercial": net_comm,
            "spec_crowding_idx": round(spec_crowding_idx, 3),
            "z_score_52w": round(z_score, 2),
            "percentile_52w": round(percentile, 1),
            "sentiment_regime": sentiment_regime,
            "recommended_action": position_action
        }


# ============================================================================
# 5. Central Bank Physical Flow & De-Dollarization Tracker
# ============================================================================

class CentralBankFlowTracker:
    """Tracks official sovereign gold accumulation and de-dollarization price floor."""

    @staticmethod
    def calculate_reserve_metrics(
        gold_tonnes: float,
        gold_price_usd_oz: float,
        total_fx_reserves_usd_billions: float
    ) -> Dict[str, Any]:
        # 1 metric tonne = 32,150.7465 troy ounces
        total_ounces = gold_tonnes * 32150.7465
        gold_valuation_billions = (total_ounces * gold_price_usd_oz) / 1e9
        total_reserves = gold_valuation_billions + total_fx_reserves_usd_billions
        gold_reserve_share_pct = (gold_valuation_billions / total_reserves) * 100.0 if total_reserves > 0 else 0.0

        return {
            "gold_tonnes": gold_tonnes,
            "gold_valuation_billions": round(gold_valuation_billions, 2),
            "total_reserves_billions": round(total_reserves, 2),
            "gold_reserve_share_pct": round(gold_reserve_share_pct, 2),
            "is_strategic_accumulator": gold_reserve_share_pct < 20.0  # Room for high sovereign buying
        }


# ============================================================================
# 6. Integrated Macro Regime & Gold Directional Engine
# ============================================================================

class MacroGoldRegimeSynthesizer:
    """
    Synthesizes real yields, DXY momentum, FOMC policy, COT sentiment, and CB flows
    into a unified quantitative macroeconomic regime classification and trading bias.
    """

    @classmethod
    def evaluate_regime(
        cls,
        nominal_10y: float,
        tips_10y: float,
        dxy_index: float,
        dxy_mom_20d_pct: float,
        cpi_yoy: float,
        fed_funds_rate: float,
        cot_zscore: float,
        central_bank_net_flow_tonnes_quarter: float
    ) -> Dict[str, Any]:
        fisher = FisherTIPSModel.calculate_real_yield(nominal_10y, tips_10y)
        taylor = FOMCPolicyOracle.taylor_rule_rate(cpi_yoy, output_gap=-0.5)
        fomc = FOMCPolicyOracle.evaluate_policy_stance(fed_funds_rate, taylor, market_implied_rate=fed_funds_rate - 0.25)

        # Multi-factor score normalization [-1.0 to +1.0]
        # 1. TIPS Yield score: lower yield -> positive for gold
        score_yield = -1.0 if tips_10y > 2.2 else (+1.0 if tips_10y < 0.5 else (1.35 - tips_10y))
        
        # 2. DXY Momentum score: falling dollar -> positive for gold
        score_dxy = -1.0 if dxy_mom_20d_pct > 2.0 else (+1.0 if dxy_mom_20d_pct < -2.0 else -dxy_mom_20d_pct / 2.0)
        
        # 3. Inflation & Debasement score
        score_inflation = +1.0 if cpi_yoy > 4.0 else (0.5 if cpi_yoy > 2.5 else -0.5)
        
        # 4. COT Contrarian score: extreme long -> negative bias, extreme short -> positive
        score_cot = -0.8 if cot_zscore > 2.0 else (+0.8 if cot_zscore < -2.0 else 0.0)
        
        # 5. Central Bank Sovereign bid
        score_cb = +1.0 if central_bank_net_flow_tonnes_quarter > 200 else (+0.5 if central_bank_net_flow_tonnes_quarter > 100 else 0.0)

        # Composite weighted score
        composite_score = (
            0.30 * score_yield +
            0.25 * score_dxy +
            0.20 * score_cb +
            0.15 * score_inflation +
            0.10 * score_cot
        )
        composite_score = max(-1.0, min(1.0, composite_score))

        # Regime classification
        if cpi_yoy >= 3.5 and tips_10y <= 1.2:
            regime = "STAGFLATION_SUPER_EXPANSION"
            bias = "MAX_LONG_AGGRESSIVE"
            target_allocation_pct = 25.0
        elif score_cb > 0.5 and composite_score > 0.3:
            regime = "FIAT_DEBASEMENT_SOVEREIGN_BID"
            bias = "BULLISH_DIP_BUYING"
            target_allocation_pct = 20.0
        elif tips_10y > 2.0 and dxy_mom_20d_pct > 1.5:
            regime = "DISINFLATIONARY_RATE_SQUEEZE"
            bias = "BEARISH_DRAG_HEDGE"
            target_allocation_pct = 5.0
        else:
            regime = "CONSOLIDATION_EQUILIBRIUM"
            bias = "TACTICAL_RANGEBOUND"
            target_allocation_pct = 12.0

        return {
            "composite_macro_score": round(composite_score, 3),
            "macro_regime": regime,
            "directional_bias": bias,
            "suggested_gold_allocation_pct": target_allocation_pct,
            "fisher_metrics": fisher,
            "fomc_stance": fomc["stance"],
            "sovereign_demand_level": "ACCELERATING" if central_bank_net_flow_tonnes_quarter > 150 else "MODERATE"
        }


# ============================================================================
# 7. Self-Contained Runnable Test Suite & Verification Invariants
# ============================================================================

def run_self_checks():
    """Validates all mathematical and economic models in Neuron N041."""
    print("Executing Neuron N041 Invariant Verification...")

    # --- Test 1: Matrix Inversion & OLS Regression ---
    # Model: Y = 2.0 + (-18.0 * TIPS) + (-1.1 * DXY_ret)
    # Generate synthetic observations with small noise
    synthetic_x = [
        [0.05, -0.02],  # delta TIPS +5bps, DXY -2%
        [-0.10, 0.01], # delta TIPS -10bps, DXY +1%
        [0.02, 0.03],  # delta TIPS +2bps, DXY +3%
        [-0.08, -0.01],# delta TIPS -8bps, DXY -1%
        [0.12, 0.02],  # delta TIPS +12bps, DXY +2%
        [-0.04, -0.03],# delta TIPS -4bps, DXY -3%
    ]
    synthetic_y = []
    for row in synthetic_x:
        y_val = 0.01 + (-18.5 * row[0]) + (-1.15 * row[1])
        synthetic_y.append(y_val)

    ols = OLSMacroRegression(feature_names=["Delta_TIPS", "Delta_DXY"])
    ols.fit(synthetic_x, synthetic_y)

    assert abs(ols.coefficients[0] - 0.01) < 1e-4, f"Intercept mismatch: {ols.coefficients[0]}"
    assert abs(ols.coefficients[1] - (-18.5)) < 1e-4, f"TIPS Beta mismatch: {ols.coefficients[1]}"
    assert abs(ols.coefficients[2] - (-1.15)) < 1e-4, f"DXY Beta mismatch: {ols.coefficients[2]}"
    assert ols.r_squared > 0.99, f"R^2 must be near 1.0, got {ols.r_squared}"
    print("  [✓] Matrix Math & OLS Multi-Factor Regression passed.")

    # --- Test 2: Fisher TIPS & Opportunity Cost ---
    fisher_res = FisherTIPSModel.calculate_real_yield(nominal_10y=4.30, tips_10y=1.90)
    assert abs(fisher_res["breakeven_inflation"] - 2.40) < 1e-6
    assert not fisher_res["is_negative_real_rate"]
    
    yield_impact = FisherTIPSModel.estimate_gold_yield_impact(delta_real_yield_bps=+25.0)
    assert yield_impact < 0.0, "Yield increase must exert negative price drag on gold"
    print("  [✓] Fisher TIPS & Breakeven Inflation invariants passed.")

    # --- Test 3: FOMC Taylor Rule & Stance ---
    # CPI 3.5%, Gap 0.0, r* 1.0 -> i* = 1.0 + 3.5 + 0.5(1.5) = 5.25%
    taylor_rate = FOMCPolicyOracle.taylor_rule_rate(cpi_inflation=3.5, output_gap=0.0, r_star=1.0, target_inflation=2.0)
    assert abs(taylor_rate - 5.25) < 1e-6
    
    policy_eval = FOMCPolicyOracle.evaluate_policy_stance(
        current_fed_funds=4.50,
        taylor_rate=taylor_rate,
        market_implied_rate=4.25
    )
    assert policy_eval["stance"] == "BEHIND_THE_CURVE"
    assert policy_eval["macro_bias"] == "DEBASEMENT_ACCELERATION"
    print("  [✓] FOMC Taylor Rule & Policy Oracle invariants passed.")

    # --- Test 4: CFTC COT Squeeze Detection ---
    hist_52w = [150000 + i * 2000 for i in range(52)] # mean ~201,000
    cot_res = CFTCCOTAnalyzer.analyze_positioning(
        managed_money_long=310000,
        managed_money_short=20000,
        commercial_long=50000,
        commercial_short=340000,
        historical_net_spec_52w=hist_52w
    )
    assert cot_res["net_speculative"] == 290000
    assert cot_res["z_score_52w"] > 2.0
    assert cot_res["sentiment_regime"] == "OVERHEATED_LONG_CROWDING"
    assert cot_res["recommended_action"] == "TRIM_OR_HEDGE_LONGS"
    print("  [✓] CFTC COT Positioning & Squeeze Engine passed.")

    # --- Test 5: Central Bank Flow Tracker ---
    cb_metrics = CentralBankFlowTracker.calculate_reserve_metrics(
        gold_tonnes=2250.0,
        gold_price_usd_oz=2650.0,
        total_fx_reserves_usd_billions=3150.0
    )
    assert cb_metrics["gold_valuation_billions"] > 180.0
    assert cb_metrics["gold_reserve_share_pct"] < 10.0
    assert cb_metrics["is_strategic_accumulator"] is True
    print("  [✓] Central Bank Sovereign Reserve Tracker passed.")

    # --- Test 6: Macro Gold Regime Synthesizer ---
    # Scenario A: Stagflation / High debasement
    regime_stagflation = MacroGoldRegimeSynthesizer.evaluate_regime(
        nominal_10y=3.80,
        tips_10y=0.40,
        dxy_index=101.5,
        dxy_mom_20d_pct=-2.5,
        cpi_yoy=4.2,
        fed_funds_rate=4.50,
        cot_zscore=0.5,
        central_bank_net_flow_tonnes_quarter=280.0
    )
    assert regime_stagflation["macro_regime"] == "STAGFLATION_SUPER_EXPANSION"
    assert regime_stagflation["directional_bias"] == "MAX_LONG_AGGRESSIVE"
    assert regime_stagflation["composite_macro_score"] > 0.60

    # Scenario B: Disinflationary rate squeeze
    regime_squeeze = MacroGoldRegimeSynthesizer.evaluate_regime(
        nominal_10y=4.90,
        tips_10y=2.45,
        dxy_index=106.8,
        dxy_mom_20d_pct=2.8,
        cpi_yoy=1.8,
        fed_funds_rate=5.50,
        cot_zscore=1.2,
        central_bank_net_flow_tonnes_quarter=60.0
    )
    assert regime_squeeze["macro_regime"] == "DISINFLATIONARY_RATE_SQUEEZE"
    assert regime_squeeze["directional_bias"] == "BEARISH_DRAG_HEDGE"
    assert regime_squeeze["composite_macro_score"] < 0.0

    print("  [✓] Integrated Macro Regime Classification Suite passed.")
    print("All Neuron N041 Invariants Verified Successfully (100% Deterministic Stdlib).")


if __name__ == "__main__":
    run_self_checks()
```
