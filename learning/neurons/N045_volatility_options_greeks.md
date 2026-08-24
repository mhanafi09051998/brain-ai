# Neuron N045: Volatility Modeling & Options Greeks (GARCH, Black-Scholes, Greeks, IV Surface, 0-DTE GEX)

Prinsip arsitektur pemodelan volatilitas kuantitatif, estimasi volatilitas dinamis GARCH(1,1), penetapan harga opsi Black-Scholes-Merton analitis, sensitivitas risiko Greeks (Delta, Gamma, Vega, Theta, Rho, Vanna, Volga), rekonstruksi permukaan volatilitas implisit (IV Surface), dan mesin kalkulasi Net Gamma Exposure (GEX) untuk opsi 0-DTE:

- **Kategori**: Quantitative Derivatives, Volatility Modeling, Financial Engineering & Risk Microstructure
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Mengestimasi dinamika volatilitas stokastik dan clustering via GARCH(1,1), menghitung harga opsi Eropa dan Greeks analitis orde 1-2 via BSM tanpa library eksternal, mengekstraksi implied volatility surface yang bebas arbitrase via root solver Newton-Raphson/Bisection hybrid, serta menganalisis eksposur gamma dealer (0-DTE GEX) untuk memprediksi regime mean reversion vs volatility expansion.
- **Synaptic Links**: [`N021`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N021_quantitative_gold_crypto_trading.md), [`N025`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N025_hft_orderbook_microstructure.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N011`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N011_mechanical_sympathy_perf.md), [`N027`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N027_tensor_simd_vectorization.md), [`N001`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N001_executive_decisions.md)
- **Status**: Active Operational Invariant

---

## 1. GARCH(1,1) Volatility Forecasting & Term Structure Engine

```
                             [ Historical Returns εₜ ]
                                        │
                                        ▼
                   ┌─────────────────────────────────────────┐
                   │  GARCH(1,1) Variance Recursion Engine   │
                   │  σₜ² = ω + α·εₜ₋₁² + β·σₜ₋₁²            │
                   └────────────────────┬────────────────────┘
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 ▼                                             ▼
    ┌───────────────────────────┐                ┌───────────────────────────┐
    │ Unconditional Long-Run    │                │ Forward Term Structure    │
    │ V_L = ω / (1 - α - β)     │                │ Eₜ[σₜ₊ₖ²] = V_L +         │
    │ (Stationarity: α + β < 1) │                │ (α+β)ᵏ⁻¹ · (σₜ₊₁² - V_L)  │
    └───────────────────────────┘                └───────────────────────────┘
```

### A. Dynamic Heteroskedasticity & Clustering Mechanics
1. **Fenomena Volatility Clustering**:
   - Pergerakan harga di pasar keuangan menunjukkan autokorelasi rendah pada tingkat return, namun autokorelasi tinggi pada kuadrat return (*squared returns* / volatilitas). Periode volatilitas tinggi cenderung diikuti oleh volatilitas tinggi, dan sebaliknya.
2. **Spesifikasi Bollerslev (1986) GARCH(1,1)**:
   $$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$
   - $\omega > 0$: Bobot baseline (*constant variance component*).
   - $\alpha \ge 0$: *ARCH parameter* (sensitivitas terhadap shock/kejutan return kemarin $\epsilon_{t-1}^2$).
   - $\beta \ge 0$: *GARCH parameter* (persistensi memori variansi masa lalu $\sigma_{t-1}^2$).
3. **Kondisi Stasioneritas Kovariansi (*Covariance Stationarity Invariant*)**:
   $$\gamma = \alpha + \beta < 1.0$$
   - Jika $\alpha + \beta \ge 1.0$, proses menjadi non-stasioner (*Integrated GARCH / IGARCH*), di mana shock return memiliki dampak permanen tak hingga pada variansi masa depan.

### B. Unconditional Long-Run Variance & Term Structure Forecasting
1. **Unconditional Long-Run Variance ($V_L$)**:
   $$V_L = \mathbb{E}[\sigma_t^2] = \frac{\omega}{1 - (\alpha + \beta)}$$
2. **Multi-Step Ahead Forward Variance Expectation**:
   $$\mathbb{E}_t[\sigma_{t+k}^2] = V_L + (\alpha + \beta)^{k-1} (\sigma_{t+1}^2 - V_L)$$
   - Ketika $k \to \infty$, estimasi variansi secara asimtotik meluruh kembali ke $V_L$ dengan laju peluruhan eksponensial $(\alpha + \beta)$.
3. **Annualized Realized Volatility Conversion**:
   $$\sigma_{\text{ann}} = \sqrt{\sigma_{\text{daily}}^2 \times N_{\text{trading\_days}}} \quad (N_{\text{trading\_days}} = 252)$$

---

## 2. Black-Scholes-Merton (BSM) Analytical Pricing & Put-Call Parity

```
                 ┌──────────────────────────────────────────────┐
                 │ Inputs: Spot S, Strike K, Tau T, r, q, σ     │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │ Calculate d₁ & d₂ Normalized Moneyness       │
                 │ d₁ = [ln(S/K) + (r - q + ½σ²)T] / [σ√T]      │
                 │ d₂ = d₁ - σ√T                                │
                 └──────────────────────┬───────────────────────┘
                                        │
                     ┌──────────────────┴──────────────────┐
                     ▼                                     ▼
        ┌─────────────────────────┐           ┌─────────────────────────┐
        │   European Call Price   │           │   European Put Price    │
        │ C = Se⁻ᑫᵀΦ(d₁) - Ke⁻ʳᵀΦ(d₂)│         │ P = Ke⁻ʳᵀΦ(-d₂) - Se⁻ᑫᵀΦ(-d₁)│
        └────────────┬────────────┘           └────────────┬────────────┘
                     │                                     │
                     └──────────────────┬──────────────────┘
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │   Put-Call Parity Verification Invariant     │
                 │        C - P = S·e⁻ᑫᵀ - K·e⁻ʳᵀ               │
                 └──────────────────────────────────────────────┘
```

### A. Continuous Risk-Neutral Valuation Framework
1. **Dinamika Geometric Brownian Motion (GBM)**:
   $$dS_t = (r - q) S_t dt + \sigma S_t dW_t$$
   - $S_t$: Harga underlying asset.
   - $r$: Risk-free interest rate kontinyu.
   - $q$: Continuous dividend yield / foreign risk-free rate / token staking yield.
   - $\sigma$: Volatilitas konstan underlying.
   - $W_t$: Standard Wiener process under risk-neutral measure $\mathbb{Q}$.
2. **Formula Analitis Penetapan Harga Opsi Eropa**:
   $$d_1 = \frac{\ln(S_0 / K) + (r - q + \frac{1}{2}\sigma^2)T}{\sigma \sqrt{T}}, \quad d_2 = d_1 - \sigma \sqrt{T}$$
   $$C(S, K, T, r, q, \sigma) = S_0 e^{-q T} \Phi(d_1) - K e^{-r T} \Phi(d_2)$$
   $$P(S, K, T, r, q, \sigma) = K e^{-r T} \Phi(-d_2) - S_0 e^{-q T} \Phi(-d_1)$$
   di mana $\Phi(x) = \frac{1}{2}\left[1 + \text{erf}\left(\frac{x}{\sqrt{2}}\right)\right]$ adalah fungsi kumulatif distribusi normal standar (*CDF*).

### B. Arbitrage-Free Put-Call Parity Invariant
1. **Persamaan Paritas Put-Call**:
   $$C - P = S_0 e^{-q T} - K e^{-r T}$$
2. **Batas Arbitrase Bebas (*No-Arbitrage Bounds*)**:
   $$\max(0, S_0 e^{-q T} - K e^{-r T}) \le C \le S_0 e^{-q T}$$
   $$\max(0, K e^{-r T} - S_0 e^{-q T}) \le P \le K e^{-r T}$$
   - Setiap deviasi harga pasar dari batas ini menciptakan peluang arbitrase instan tanpa risiko (*cash-and-carry / reverse cash-and-carry*).

---

## 3. Complete Analytical Greeks & Risk Sensitivities

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            THE GREEKS RISK CODEX                             │
├──────────────┬──────────────────────────────────────┬────────────────────────┤
│ Greek        │ Formula                              │ Interpretasi Risiko    │
├──────────────┼──────────────────────────────────────┼────────────────────────┤
│ Delta (Call) │ Δ_c = e⁻ᑫᵀ Φ(d₁)                     │ Directional exposure   │
│ Delta (Put)  │ Δ_p = -e⁻ᑫᵀ Φ(-d₁) = Δ_c - e⁻ᑫᵀ       │ Directional exposure   │
│ Gamma        │ Γ = [e⁻ᑫᵀ ϕ(d₁)] / [S σ √T]          │ Curvature / Convexity  │
│ Vega         │ 𝒱 = S e⁻ᑫᵀ ϕ(d₁) √T                  │ Volatility sensitivity │
│ Theta (Call) │ Θ_c = -[S e⁻ᑫᵀ ϕ(d₁) σ]/[2√T]        │ Time decay             │
│              │       + q S e⁻ᑫᵀ Φ(d₁) - r K e⁻ʳᵀ Φ(d₂) │                        │
│ Theta (Put)  │ Θ_p = -[S e⁻ᑫᵀ ϕ(d₁) σ]/[2√T]        │ Time decay             │
│              │       - q S e⁻ᑫᵀ Φ(-d₁) + r K e⁻ʳᵀ Φ(-d₂)│                     │
│ Rho (Call)   │ ρ_c = K T e⁻ʳᵀ Φ(d₂)                 │ Interest rate risk     │
│ Rho (Put)    │ ρ_p = -K T e⁻ʳᵀ Φ(-d₂)                │ Interest rate risk     │
│ Vanna        │ ∂Δ/∂σ = -[e⁻ᑫᵀ ϕ(d₁) d₂] / σ         │ Cross Spot-Vol risk    │
│ Volga (Vomma)│ ∂𝒱/∂σ = [𝒱 d₁ d₂] / σ                │ Vol convexity          │
└──────────────┴──────────────────────────────────────┴────────────────────────┘
```

### A. Karakteristik & Dinamika Greeks
1. **Delta ($\Delta \in [-1, 1]$)**:
   - Merepresentasikan jumlah lembar underlying yang dibutuhkan untuk melakukan *delta hedging*.
   - Probabilitas risk-neutral opsi berakhir In-The-Money (ITM) mendekati $\Phi(d_2)$, sementara hedge ratio ditentukan oleh $\Phi(d_1)$.
2. **Gamma ($\Gamma > 0$)**:
   - Selalu positif untuk pembeli opsi (long options) dan identik untuk Call dan Put.
   - Puncak gamma berada tepat pada level At-The-Money (ATM, $S \approx K$). Menjelang kedaluwarsa ($T \to 0$), Gamma ATM meledak menuju tak hingga ($\Gamma \propto \frac{1}{\sqrt{T}} \to \infty$).
3. **Vega ($\mathcal{V} > 0$)**:
   - Sensitivitas nilai opsi terhadap perubahan 1.0 unit volatilitas implisit. Opsi dengan tenor panjang memiliki Vega jauh lebih besar dibandingkan opsi jangka pendek.
4. **Theta ($\Theta < 0$)**:
   - Biaya membawa posisi (*carry cost*) atau peluruhan waktu. Opsi long mengalami pendarahan modal setiap hari (*theta bleed*), yang terakselerasi secara non-linear pada minggu terakhir masa berlaku.

---

## 4. Implied Volatility Surface & Robust Hybrid Inversion

```
                          [ Market Option Price Cₘ ]
                                      │
                                      ▼
                  ┌───────────────────────────────────────┐
                  │ Check Arbitrage Bounds (Intrinsic/Max)│
                  └───────────────────┬───────────────────┘
                                      │
                                      ▼
                  ┌───────────────────────────────────────┐
                  │ Phase 1: Newton-Raphson Fast Solver   │
                  │ σₙ₊₁ = σₙ - [BSM(σₙ) - Cₘ] / 𝒱(σₙ)    │
                  └───────────────────┬───────────────────┘
                                      │
                         ┌────────────┴────────────┐
             (Converged) │                         │ (Vega < 1e-12 or Out-of-Bounds)
                         ▼                         ▼
            ┌─────────────────────────┐ ┌─────────────────────────┐
            │ Target Implied Vol (σ*) │ │ Phase 2: Bisection Fall-│
            │ Guaranteed Tolerance    │ │ back Search in [0, 10]  │
            └─────────────────────────┘ └────────────┬────────────┘
                                                     │ (Converged)
                                                     ▼
                                        ┌─────────────────────────┐
                                        │ Exact Implied Vol (σ*)  │
                                        └─────────────────────────┘
```

### A. Algoritma Root-Finding Inversion (Hybrid NR-Bisection)
1. **Formulasi Masalah**:
   - Diberikan harga pasar $C_{\text{market}}$, cari $\sigma_{\text{IV}}$ sedemikian sehingga:
     $$f(\sigma) = \text{BSM}(S, K, T, r, q, \sigma) - C_{\text{market}} = 0$$
2. **Langkah Newton-Raphson**:
   $$\sigma_{n+1} = \sigma_n - \frac{f(\sigma_n)}{\mathcal{V}(\sigma_n)}$$
3. **Kegagalan Newton-Raphson & Fallback Invariant**:
   - Untuk opsi yang berada sangat jauh dari uang (Deep OTM/ITM) atau saat $T \to 0$, Vega mendekati nol ($\mathcal{V} < 10^{-12}$). Pembagian dengan bilangan mendekati nol menyebabkan ledakan nilai float (*overflow / numerical divergence*).
   - **Solusi Invarian**: Jika $\mathcal{V} < 10^{-12}$ atau $\sigma_{n+1} \notin [10^{-4}, 10.0]$, langsung alihkan pencarian ke metode **Bisection** yang memiliki jaminan konvergensi mutlak $100\%$.

### B. Parametrik Volatility Skew & Smile
1. **Log-Moneyness Representation**:
   $$k = \ln\left(\frac{K}{S_0}\right)$$
2. **Kuadratik Volatility Skew Parametrization**:
   $$\sigma_{\text{IV}}(k) = \sigma_0 + \rho_{\text{skew}} k + \beta_{\text{smile}} k^2$$
   - $\sigma_0$: ATM implied volatility.
   - $\rho_{\text{skew}} < 0$: Kemiringan skew (umum pada indeks saham akibat permintaan *downside put protection* / *crashophobia*).
   - $\beta_{\text{smile}} > 0$: Kurvatur smile (efek ekor gemuk / *fat tails* pada distribusi log-return).

---

## 5. 0-DTE Options Mechanics & Net Gamma Exposure (GEX) Engine

```
                             [ Open Interest Matrix ]
                         Calls (OI_c)        Puts (OI_p)
                              │                   │
                              ▼                   ▼
                      ┌───────────────────────────────────┐
                      │  Per-Strike Dollar GEX Calculator │
                      │  GEX_c = +OI_c · Γ · S² · 0.01    │
                      │  GEX_p = -OI_p · Γ · S² · 0.01    │
                      └─────────────────┬─────────────────┘
                                        │
                                        ▼
                      ┌───────────────────────────────────┐
                      │ Aggregate Net GEX = Σ (GEX_c + GEX_p)
                      └─────────────────┬─────────────────┘
                                        │
                  ┌─────────────────────┴─────────────────────┐
                  ▼                                           ▼
    ┌───────────────────────────┐               ┌───────────────────────────┐
    │ Positive Net GEX (> 0)    │               │ Negative Net GEX (< 0)    │
    │ Market Makers LONG Gamma  │               │ Market Makers SHORT Gamma │
    │ ──► Dynamic Delta Hedge:  │               │ ──► Dynamic Delta Hedge:  │
    │     Sell Rallies, Buy Dips│               │     Buy Rallies, Sell Dips│
    │ ──► Volatility Suppression│               │ ──► Volatility Expansion  │
    │     & Pinning to Strikes  │               │     & Momentum Cascade    │
    └───────────────────────────┘               └───────────────────────────┘
```

### A. Mekanika 0-DTE (Zero Days-To-Expiration)
1. **Hiper-Sensitivitas Gamma Intra-Day**:
   - Pada hari kedaluwarsa ($T \to 0$), probabilitas moneyness bergeser secara biner (0 atau 1). Hal ini menciptakan konsentrasi Gamma ekstrem pada strike di sekitar spot ($S \approx K$).
2. **Asumsi Posisi Dealer / Market Maker (MM)**:
   - Partisipan ritel secara agregat adalah pembeli netto opsi (*net long calls & puts*).
   - Market Maker bertindak sebagai penyedia likuiditas dan mengambil posisi sebaliknya: **Net Short Options**.
   - Untuk menjaga posisi delta-neutral, Market Maker harus melakukan rebalancing delta secara dinamis terhadap underlying:
     $$\Delta_{\text{MM\_hedge}} = -\Delta_{\text{options}}$$
     $$\frac{\partial \Delta_{\text{MM\_hedge}}}{\partial S} = -\text{Net GEX}$$

### B. Formulasi Dollar GEX & Deteksi Gamma Flip
1. **Dollar GEX Per-Strike Formula**:
   $$\text{GEX}_{\text{call}}(K_i) = +\text{OI}_{\text{call}}(K_i) \times \Gamma_i \times S^2 \times 0.01 \times \text{ContractSize}$$
   $$\text{GEX}_{\text{put}}(K_i) = -\text{OI}_{\text{put}}(K_i) \times \Gamma_i \times S^2 \times 0.01 \times \text{ContractSize}$$
   $$\text{Net GEX}(S) = \sum_{i=1}^M \left(\text{GEX}_{\text{call}}(K_i) + \text{GEX}_{\text{put}}(K_i)\right)$$
2. **Karakteristik Dua Rezim Pasar**:
   - **Rezim Long Gamma ($\text{Net GEX} > 0$)**:
     - Ketika harga naik ($S \uparrow$), delta MM bertambah positif $\implies$ MM harus **menjual** underlying untuk tetap netral.
     - Ketika harga turun ($S \downarrow$), delta MM berkurang $\implies$ MM harus **membeli** underlying.
     - **Dampak**: Menekan volatilitas (*volatility dampening*), menciptakan *mean reversion*, dan memicu *gamma pinning* pada strike dengan Open Interest terbesar.
   - **Rezim Short Gamma ($\text{Net GEX} < 0$)**:
     - Ketika harga turun ($S \downarrow$), MM harus **menjual** underlying $\implies$ mempercepat penurunan (*liquidity cascade / flash crash*).
     - Ketika harga naik ($S \uparrow$), MM harus **membeli** underlying $\implies$ memicu *short squeeze*.
     - **Dampak**: Mempercepat momentum dan meledakkan volatilitas (*volatility explosion*).
3. **Gamma Flip Point ($S^*$ / Zero-Crossing)**:
   - Titik harga $S^*$ di mana $\text{Net GEX}(S^*) = 0$. Menembus ke bawah Gamma Flip adalah sinyal peringatan dini transisi pasar dari rezim tenang ke rezim turbulen.

---

## 6. Pure Python 3.12+ Executable Implementation & Self-Check

```python
"""
Neuron N045: Volatility Modeling & Options Greeks Suite.
Pure Python 3.12+ Standard Library (Zero External Dependencies).
"""

import sys
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

@dataclass
class OptionGreeks:
    delta: float
    gamma: float
    vega: float      # Per 1.0 unit vol (0.01 = 1% vol shift)
    theta: float     # Annualized time decay (divide by 365 or 252 for daily)
    rho: float       # Per 1.0 unit rate change
    vanna: float     # dDelta / dVol
    volga: float     # dVega / dVol (Vomma)


class GARCHModel:
    """
    GARCH(1,1) Volatility Engine.
    sigma_t^2 = omega + alpha * eps_{t-1}^2 + beta * sigma_{t-1}^2
    """
    def __init__(self, omega: float, alpha: float, beta: float):
        if omega <= 0.0:
            raise ValueError(f"Omega must be strictly positive, got {omega}")
        if alpha < 0.0 or beta < 0.0:
            raise ValueError("Alpha and Beta must be non-negative")
        if alpha + beta >= 1.0:
            raise ValueError(f"Stationarity condition violated: alpha + beta = {alpha + beta:.4f} >= 1.0")
        self.omega = omega
        self.alpha = alpha
        self.beta = beta
        self.persistence = alpha + beta

    @property
    def long_run_variance(self) -> float:
        """Unconditional long-run variance V_L = omega / (1 - alpha - beta)."""
        return self.omega / (1.0 - self.persistence)

    def compute_variance_series(self, returns: List[float], init_var: Optional[float] = None) -> List[float]:
        """Calculates conditional variance path across historical return series."""
        if not returns:
            return []
        v_0 = init_var if init_var is not None else self.long_run_variance
        var_series = [v_0]
        for r in returns[:-1]:
            var_next = self.omega + self.alpha * (r ** 2) + self.beta * var_series[-1]
            var_series.append(var_next)
        return var_series

    def forecast_term_structure(self, current_var: float, last_return: float, steps: int = 10) -> List[float]:
        """Calculates multi-step forward conditional variance expectation."""
        if steps <= 0:
            return []
        v_next = self.omega + self.alpha * (last_return ** 2) + self.beta * current_var
        forecasts = [v_next]
        v_L = self.long_run_variance
        for k in range(2, steps + 1):
            v_k = v_L + (self.persistence ** (k - 1)) * (v_next - v_L)
            forecasts.append(v_k)
        return forecasts

    @staticmethod
    def annualized_volatility(daily_variance: float, trading_days: int = 252) -> float:
        """Converts daily variance to annualized volatility decimal."""
        return math.sqrt(daily_variance * trading_days)


class BSMOptionEngine:
    """
    Black-Scholes-Merton European Options Analytical Pricing & Greeks Engine.
    Standard library only.
    """

    @staticmethod
    def norm_cdf(x: float) -> float:
        """Standard normal cumulative distribution function Phi(x)."""
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    @staticmethod
    def norm_pdf(x: float) -> float:
        """Standard normal probability density function phi(x)."""
        return (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * x * x)

    @classmethod
    def d1_d2(cls, s: float, k: float, t: float, r: float, q: float, sigma: float) -> Tuple[float, float]:
        """Calculates d1 and d2 parameters."""
        if s <= 0.0 or k <= 0.0:
            raise ValueError(f"Spot and Strike must be strictly positive: S={s}, K={k}")
        if t <= 0.0 or sigma <= 0.0:
            raise ValueError(f"Time to expiry and Volatility must be positive: T={t}, sigma={sigma}")
        
        sqrt_t = math.sqrt(t)
        d1 = (math.log(s / k) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t)
        d2 = d1 - sigma * sqrt_t
        return d1, d2

    @classmethod
    def price(cls, option_type: str, s: float, k: float, t: float, r: float, q: float, sigma: float) -> float:
        """Computes European option analytical price under BSM."""
        opt_type = option_type.lower()
        if opt_type not in ("call", "put"):
            raise ValueError(f"Invalid option_type '{option_type}', expected 'call' or 'put'")
        
        if t <= 1e-9:  # Payoff at expiration
            return max(0.0, (s - k) if opt_type == "call" else (k - s))
        
        d1, d2 = cls.d1_d2(s, k, t, r, q, sigma)
        df_r = math.exp(-r * t)
        df_q = math.exp(-q * t)
        
        if opt_type == "call":
            return s * df_q * cls.norm_cdf(d1) - k * df_r * cls.norm_cdf(d2)
        else:
            return k * df_r * cls.norm_cdf(-d2) - s * df_q * cls.norm_cdf(-d1)

    @classmethod
    def greeks(cls, option_type: str, s: float, k: float, t: float, r: float, q: float, sigma: float) -> OptionGreeks:
        """Calculates exact analytical 1st & 2nd order Greeks."""
        opt_type = option_type.lower()
        if opt_type not in ("call", "put"):
            raise ValueError(f"Invalid option_type '{option_type}'")
        
        d1, d2 = cls.d1_d2(s, k, t, r, q, sigma)
        sqrt_t = math.sqrt(t)
        df_r = math.exp(-r * t)
        df_q = math.exp(-q * t)
        pdf_d1 = cls.norm_pdf(d1)
        cdf_d1 = cls.norm_cdf(d1)
        cdf_d2 = cls.norm_cdf(d2)

        # Delta
        delta = df_q * cdf_d1 if opt_type == "call" else -df_q * cls.norm_cdf(-d1)

        # Gamma (identical for Call & Put)
        gamma = (df_q * pdf_d1) / (s * sigma * sqrt_t)

        # Vega (identical for Call & Put)
        vega = s * df_q * pdf_d1 * sqrt_t

        # Theta (annualized)
        decay_term = -(s * df_q * pdf_d1 * sigma) / (2.0 * sqrt_t)
        if opt_type == "call":
            theta = decay_term + q * s * df_q * cdf_d1 - r * k * df_r * cdf_d2
        else:
            theta = decay_term - q * s * df_q * cls.norm_cdf(-d1) + r * k * df_r * cls.norm_cdf(-d2)

        # Rho
        rho = k * t * df_r * cdf_d2 if opt_type == "call" else -k * t * df_r * cls.norm_cdf(-d2)

        # Higher-Order Cross Greeks: Vanna & Volga
        vanna = -df_q * pdf_d1 * d2 / sigma
        volga = vega * d1 * d2 / sigma

        return OptionGreeks(
            delta=delta,
            gamma=gamma,
            vega=vega,
            theta=theta,
            rho=rho,
            vanna=vanna,
            volga=volga
        )

    @classmethod
    def implied_volatility(
        cls,
        option_type: str,
        target_price: float,
        s: float,
        k: float,
        t: float,
        r: float,
        q: float,
        tol: float = 1e-8,
        max_iter: int = 100
    ) -> float:
        """
        Robust Implied Volatility root solver.
        Uses Newton-Raphson with guaranteed fallback to Bisection on numerical singularities.
        """
        opt_type = option_type.lower()
        df_r = math.exp(-r * t)
        df_q = math.exp(-q * t)
        
        # Arbitrage boundary checks
        if opt_type == "call":
            intrinsic = max(0.0, s * df_q - k * df_r)
            upper_bound = s * df_q
        else:
            intrinsic = max(0.0, k * df_r - s * df_q)
            upper_bound = k * df_r

        if target_price < intrinsic - 1e-7:
            raise ValueError(f"Target price {target_price:.6f} below intrinsic arbitrage floor {intrinsic:.6f}")
        if target_price > upper_bound + 1e-7:
            raise ValueError(f"Target price {target_price:.6f} above theoretical ceiling {upper_bound:.6f}")

        # Initial Volatility Seed
        sigma = math.sqrt(2.0 * math.pi / t) * (target_price / s) if abs(s - k) < 1e-3 else 0.25
        sigma = max(0.01, min(5.0, sigma))

        # Phase 1: Newton-Raphson Iteration
        for _ in range(max_iter):
            price_est = cls.price(opt_type, s, k, t, r, q, sigma)
            diff = price_est - target_price
            if abs(diff) < tol:
                return sigma
            
            g = cls.greeks(opt_type, s, k, t, r, q, sigma)
            vega = g.vega
            if vega < 1e-12:
                break  # Flat slope: jump to bisection
            
            step = diff / vega
            sigma_new = sigma - step
            if sigma_new <= 0.0001 or sigma_new > 10.0:
                break  # Outside stable domain: switch to bisection
            if abs(sigma_new - sigma) < tol:
                return sigma_new
            sigma = sigma_new

        # Phase 2: Guaranteed Bisection Search
        low, high = 1e-4, 10.0
        for _ in range(max_iter * 2):
            mid = 0.5 * (low + high)
            price_mid = cls.price(opt_type, s, k, t, r, q, mid)
            diff = price_mid - target_price
            if abs(diff) < tol or (high - low) < tol:
                return mid
            if diff > 0:
                high = mid
            else:
                low = mid
        return 0.5 * (low + high)

    @classmethod
    def verify_put_call_parity(cls, s: float, k: float, t: float, r: float, q: float, sigma: float) -> Tuple[float, float, float]:
        """Calculates (C - P), (S*e^{-qT} - K*e^{-rT}), and absolute parity error."""
        c = cls.price("call", s, k, t, r, q, sigma)
        p = cls.price("put", s, k, t, r, q, sigma)
        left = c - p
        right = s * math.exp(-q * t) - k * math.exp(-r * t)
        return left, right, abs(left - right)


class ZeroDTEGEXEngine:
    """
    0-DTE & Options Gamma Exposure (GEX) Microstructure Risk Engine.
    Quantifies market maker hedging pressure and volatility regime shift.
    """

    @staticmethod
    def calculate_strike_gex(
        spot: float,
        strike: float,
        call_oi: float,
        put_oi: float,
        tau: float,
        r: float,
        q: float,
        iv: float,
        contract_size: int = 100
    ) -> Tuple[float, float, float]:
        """
        Calculates Dollar Gamma Exposure per 1% spot move.
        GEX_call = +OI_c * Gamma * Spot^2 * 0.01 * ContractSize
        GEX_put  = -OI_p * Gamma * Spot^2 * 0.01 * ContractSize
        """
        greeks = BSMOptionEngine.greeks("call", spot, strike, tau, r, q, iv)
        gamma = greeks.gamma
        spot_sq_1pct = (spot ** 2) * 0.01 * contract_size
        
        call_gex = call_oi * gamma * spot_sq_1pct
        put_gex = -put_oi * gamma * spot_sq_1pct
        net_gex = call_gex + put_gex
        return call_gex, put_gex, net_gex

    @classmethod
    def aggregate_gex_profile(
        cls,
        spot: float,
        strikes: List[float],
        call_ois: List[float],
        put_ois: List[float],
        tau: float,
        r: float,
        q: float,
        ivs: List[float],
        contract_size: int = 100
    ) -> Dict[str, Any]:
        """Aggregates total market maker Net GEX profile across strike ladder."""
        total_call_gex = 0.0
        total_put_gex = 0.0
        strike_breakdown = []

        for k, c_oi, p_oi, iv in zip(strikes, call_ois, put_ois, ivs):
            cg, pg, ng = cls.calculate_strike_gex(spot, k, c_oi, p_oi, tau, r, q, iv, contract_size)
            total_call_gex += cg
            total_put_gex += pg
            strike_breakdown.append({
                "strike": k,
                "call_gex": cg,
                "put_gex": pg,
                "net_gex": ng
            })

        net_gex = total_call_gex + total_put_gex
        regime = "Long Gamma (Mean-Reverting / Vol Suppression)" if net_gex > 0 else "Short Gamma (Trend-Accelerating / Vol Expansion)"
        
        return {
            "spot": spot,
            "net_gex": net_gex,
            "call_gex": total_call_gex,
            "put_gex": total_put_gex,
            "regime": regime,
            "profile": strike_breakdown
        }

    @classmethod
    def find_gamma_flip(
        cls,
        strikes: List[float],
        call_ois: List[float],
        put_ois: List[float],
        tau: float,
        r: float,
        q: float,
        ivs: List[float],
        price_range: Tuple[float, float],
        steps: int = 200,
        contract_size: int = 100
    ) -> Optional[float]:
        """Locates the precise price level where aggregate Net GEX transitions across zero."""
        p_min, p_max = price_range
        step_size = (p_max - p_min) / float(steps)
        
        prev_price = p_min
        prev_gex = cls.aggregate_gex_profile(
            p_min, strikes, call_ois, put_ois, tau, r, q, ivs, contract_size
        )["net_gex"]

        for i in range(1, steps + 1):
            curr_price = p_min + i * step_size
            curr_gex = cls.aggregate_gex_profile(
                curr_price, strikes, call_ois, put_ois, tau, r, q, ivs, contract_size
            )["net_gex"]

            if prev_gex * curr_gex <= 0:
                if abs(curr_gex - prev_gex) < 1e-12:
                    return curr_price
                alpha = abs(prev_gex) / (abs(prev_gex) + abs(curr_gex))
                flip_price = prev_price + alpha * (curr_price - prev_price)
                return flip_price
            
            prev_price = curr_price
            prev_gex = curr_gex

        return None


# Self-Check Verification Suite
def run_neuron_tests():
    # 1. Test GARCH(1,1) Invariants
    garch = GARCHModel(omega=1.0e-6, alpha=0.08, beta=0.90)
    assert garch.persistence == 0.98, f"Expected 0.98 persistence, got {garch.persistence}"
    assert abs(garch.long_run_variance - 5.0e-5) < 1e-8, f"Expected 5e-5 long-run var, got {garch.long_run_variance}"

    # Stationarity violation assertion
    try:
        GARCHModel(omega=1.0e-6, alpha=0.5, beta=0.6)
        assert False, "Non-stationary GARCH must raise ValueError"
    except ValueError:
        pass

    # Variance forward forecast term structure
    forecasts = garch.forecast_term_structure(current_var=1.0e-4, last_return=0.02, steps=5)
    assert len(forecasts) == 5
    assert forecasts[0] > 5.0e-5, "High return shock must elevate immediate variance"
    for i in range(1, len(forecasts)):
        assert abs(forecasts[i] - garch.long_run_variance) < abs(forecasts[i-1] - garch.long_run_variance), "Variance must decay to long-run mean"

    # 2. Test BSM Option Pricing & Put-Call Parity
    s, k, t, r, q, sigma = 100.0, 100.0, 1.0, 0.05, 0.02, 0.20
    call_p = BSMOptionEngine.price("call", s, k, t, r, q, sigma)
    put_p = BSMOptionEngine.price("put", s, k, t, r, q, sigma)
    assert call_p > 0.0 and put_p > 0.0
    
    # Exact Put-Call Parity validation
    left, right, parity_err = BSMOptionEngine.verify_put_call_parity(s, k, t, r, q, sigma)
    assert parity_err < 1e-10, f"Put-Call parity violation: error={parity_err}"

    # 3. Test Greeks Analytical vs Finite Difference Approximations
    greeks = BSMOptionEngine.greeks("call", s, k, t, r, q, sigma)
    assert 0.0 < greeks.delta < 1.0, f"Call delta must be bounded in (0, 1), got {greeks.delta}"
    assert greeks.gamma > 0.0, "Gamma must be positive"
    assert greeks.vega > 0.0, "Vega must be positive"

    # Numerical Delta check
    eps = 1e-4
    p_up = BSMOptionEngine.price("call", s + eps, k, t, r, q, sigma)
    p_dn = BSMOptionEngine.price("call", s - eps, k, t, r, q, sigma)
    num_delta = (p_up - p_dn) / (2.0 * eps)
    assert abs(greeks.delta - num_delta) < 1e-4, f"Delta mismatch: analytical {greeks.delta} vs num {num_delta}"

    # Numerical Gamma check
    num_gamma = (p_up - 2.0 * call_p + p_dn) / (eps * eps)
    assert abs(greeks.gamma - num_gamma) < 1e-4, f"Gamma mismatch: analytical {greeks.gamma} vs num {num_gamma}"

    # 4. Test Implied Volatility Solver & Convergence
    target_iv = 0.285
    synthetic_price = BSMOptionEngine.price("call", s, k, t, r, q, target_iv)
    recovered_iv = BSMOptionEngine.implied_volatility("call", synthetic_price, s, k, t, r, q)
    assert abs(recovered_iv - target_iv) < 1e-6, f"IV solver error: expected {target_iv}, got {recovered_iv}"

    # Test deep OTM Put IV inversion
    otm_put_price = BSMOptionEngine.price("put", 100.0, 80.0, 0.5, 0.03, 0.0, 0.35)
    recovered_put_iv = BSMOptionEngine.implied_volatility("put", otm_put_price, 100.0, 80.0, 0.5, 0.03, 0.0)
    assert abs(recovered_put_iv - 0.35) < 1e-6, f"OTM Put IV mismatch: {recovered_put_iv}"

    # 5. Test 0-DTE & GEX Engine
    strikes = [90.0, 95.0, 100.0, 105.0, 110.0]
    call_ois = [100.0, 500.0, 2000.0, 1200.0, 300.0]
    put_ois = [500.0, 1500.0, 1800.0, 400.0, 100.0]
    ivs = [0.22, 0.20, 0.18, 0.19, 0.21]
    tau_0dte = 1.0 / 252.0  # 1 day / 0-DTE

    res = ZeroDTEGEXEngine.aggregate_gex_profile(100.0, strikes, call_ois, put_ois, tau_0dte, 0.05, 0.0, ivs)
    assert "net_gex" in res and "regime" in res
    assert res["call_gex"] > 0.0
    assert res["put_gex"] < 0.0

    # Test Gamma Flip Search
    flip_spot = ZeroDTEGEXEngine.find_gamma_flip(strikes, call_ois, put_ois, tau_0dte, 0.05, 0.0, ivs, price_range=(90.0, 110.0))
    if flip_spot is not None:
        assert 90.0 <= flip_spot <= 110.0
        flip_res = ZeroDTEGEXEngine.aggregate_gex_profile(flip_spot, strikes, call_ois, put_ois, tau_0dte, 0.05, 0.0, ivs)
        assert abs(flip_res["net_gex"]) < 500.0, f"Net GEX at flip must be near zero: got {flip_res['net_gex']}"

    print("  [✓] Neuron N045 Invariants Verified: GARCH(1,1), BSM Pricing, Greeks, IV Solver, & 0-DTE GEX.")

if __name__ == "__main__":
    run_neuron_tests()
```

---

## 7. Invariant Ringkas & Disiplin Eksekusi
1. **Covariance Stationarity Guard**: Selalu validasi $\alpha + \beta < 1.0$ sebelum melakukan peramalan term structure variansi GARCH.
2. **Exact Put-Call Parity**: Jangan gunakan harga opsi pasar yang melanggar paritas tanpa mengeksploitasi atau membuang outlier arbitrase.
3. **Hybrid IV Fallback**: Wajib sediakan pencarian Bisection ketika $\mathcal{V} < 10^{-12}$ untuk mencegah divergensi numerik Newton-Raphson pada opsi Deep OTM/0-DTE.
4. **Net GEX Regime Awareness**:
   - Jika $\text{Net GEX} > 0$ (Long Gamma): Gunakan strategi *mean-reversion / range trading* dan antisipasi pinning pada strike Open Interest tertinggi.
   - Jika $\text{Net GEX} < 0$ (Short Gamma): Bersiap menghadapi *momentum breakout* agresif dan lonjakan volatilitas terealisasi (*realized volatility explosion*).

