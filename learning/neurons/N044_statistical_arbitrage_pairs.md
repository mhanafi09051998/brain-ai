# Neuron N044: Statistical Arbitrage, Pairs Trading & Cointegration

Prinsip arsitektur perdagangan kuantitatif arbitrase statistik (*Statistical Arbitrage / StatArb*), pengujian kointegrasi ekonometrik (*Engle-Granger Two-Step & Johansen VECM*), pemodelan proses stokastik *mean-reverting* kontinu (*Ornstein-Uhlenbeck SDE*), estimasi rasio lindung nilai dinamis adaptif (*Online 2D Kalman Filter*), serta orkestrasi pita perdagangan *Z-Score* multi-aset (Gold XAU/USD vs Silver XAG/USD) dengan *circuit breaker* co-drift dan pembatas friksi likuiditas.

- **Kategori**: Quantitative Finance, Statistical Arbitrage, Time-Series Econometrics, Stochastic Differential Equations
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Membangun fondasi deterministik untuk arbitrase statistik bebas bias lookahead, membuktikan stasionaritas residual harga melalui uji akar unit Augmented Dickey-Fuller (ADF) dan matriks rank kointegrasi Johansen, mengkalibrasi laju pembalikan nilai tengah (*half-life of mean reversion*) via proses Ornstein-Uhlenbeck analitik, mengestimasi $\beta_t$ secara real-time via Kalman Filter tanpa lag rolling-window, serta mengeksekusi strategi pasangan Gold/Silver dengan band Z-Score adaptif dan guardrail proteksi struktural.
- **Synaptic Links**: [`N021`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N021_quantitative_gold_crypto_trading.md), [`N025`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N025_hft_orderbook_microstructure.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N017`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N017_program_aided_math.md), [`N027`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N027_tensor_simd_vectorization.md), [`N033`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N033_python_high_performance.md), [`N040`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N040_meta_cognitive_self_reflection.md)
- **Status**: Active Operational Invariant

---

## 1. Cointegration vs Correlation & Econometric Stationarity

```
┌────────────────────────────────────────────────────────────────────────┐
│               KORELASI VS KOINTEGRASI (SPURIOUS PITFALL)               │
├────────────────────────────────────────────────────────────────────────┤
│  Korelasi (Pearson r)        │  Kointegrasi (Engle-Granger / Johansen)  │
│  - Mengukur kovariansi return│  - Mengukur keterikatan ekuilibrium      │
│    pada rentang waktu sama.  │    jangka panjang tingkat harga level.   │
│  - Rentan Spurious Regression│  - Kebal drift acak I(1); linear         │
│    pada data non-stasioner.  │    combination ε_t ~ I(0) stasioner.     │
│  - Sering hancur saat crash. │  - Memberikan sinyal Mean-Reverting riil.│
└──────────────────────────────┴──────────────────────────────────────────┘
```

### A. Bahaya Korelasi Palsu (*Spurious Regression*)
Dua deret waktu harga aset $Y_t$ dan $X_t$ yang sama-sama bergerak acak (*Integrated of order 1 / $I(1)$*) dapat menunjukkan koefisien korelasi Pearson $R^2 > 0.90$ semata-mata karena keduanya memiliki tren waktu bersama (*common stochastic drift*), meskipun tidak memiliki hubungan fundamental ekonomi sama sekali. Mengeksekusi *pairs trading* berbasis korelasi naif menyebabkan *infinite divergence drawdown* ketika korelasi terputus (*correlation breakdown*).

### B. Definisi Formal Kointegrasi (*Order of Integration*)
Deret $Y_t \sim I(1)$ dan $X_t \sim I(1)$ dikatakan terkointegrasi $CI(1, 1)$ jika terdapat vektor kointegrasi $[1, -\beta]^T$ dan konstanta $\alpha$ sedemikian rupa sehingga kombinasi linearnya:
$$S_t = Y_t - \beta X_t - \alpha = \epsilon_t$$
menghasilkan residual $\epsilon_t \sim I(0)$ yang memiliki:
1. Ekspektasi rata-rata konstan: $\mathbb{E}[\epsilon_t] = 0$.
2. Variansi terbatas dan konstan (*homoscedastic finite variance*): $\text{Var}(\epsilon_t) = \sigma_\epsilon^2 < \infty$.
3. Autokovariansi hanya bergantung pada lag waktu $k$, bukan waktu absolut $t$: $\text{Cov}(\epsilon_t, \epsilon_{t+k}) = \gamma(k)$.

---

### C. Uji Akar Unit Augmented Dickey-Fuller (ADF)
Untuk menguji apakah suatu deret atau residual kointegrasi adalah $I(0)$ (stasioner) terhadap hipotesis nol unit root $I(1)$:
$$\Delta \epsilon_t = \gamma \epsilon_{t-1} + \sum_{i=1}^p \delta_i \Delta \epsilon_{t-i} + u_t$$
- Hipotesis Nol $H_0: \gamma = 0$ (Deret memiliki Unit Root / Non-Stasioner).
- Hipotesis Alternatif $H_1: \gamma < 0$ (Deret Stasioner / Mean-Reverting).
- Statistik Uji:
  $$\tau = \frac{\hat{\gamma}}{\text{SE}(\hat{\gamma})}$$
- **MacKinnon Critical Values**: Residual OLS memiliki distribusi lebih lebar dari DF standar. Pada taraf signifikansi $\alpha = 0.05$, nilai kritis $\tau_{\text{crit}} \approx -3.34$. Jika $\tau < -3.34$, tolak $H_0 \implies$ residual terbukti stasioner (*cointegrated*).

---

### D. Uji Kointegrasi Multivariat Johansen (VECM Framework)
Untuk portofolio multi-aset $Y_t \in \mathbb{R}^k$, Vector Error Correction Model (VECM) didefinisikan sebagai:
$$\Delta Y_t = \boldsymbol{\mu} + \boldsymbol{\Pi} Y_{t-1} + \sum_{i=1}^{p-1} \boldsymbol{\Gamma}_i \Delta Y_{t-i} + \mathbf{e}_t$$
Matriks koefisien jangka panjang $\boldsymbol{\Pi} = \boldsymbol{\alpha} \boldsymbol{\beta}^T$ di mana:
- $\text{rank}(\boldsymbol{\Pi}) = r$ menunjukkan jumlah vektor kointegrasi linear independen.
- Jika $r = 0$: Tidak ada relasi kointegrasi.
- Jika $0 < r < k$: Terdapat $r$ hubungan ekuilibrium stasioner yang dapat diperdagangkan.
- Nilai eigen $\lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_k$ diperoleh dari dekomposisi nilai eigen umum (*generalized eigenvalue problem*):
  $$|\lambda \mathbf{S}_{11} - \mathbf{S}_{10} \mathbf{S}_{00}^{-1} \mathbf{S}_{01}| = 0$$
- **Trace Statistic**:
  $$\lambda_{\text{trace}}(r) = -T \sum_{i=r+1}^k \ln(1 - \hat{\lambda}_i)$$
- **Max-Eigenvalue Statistic**:
  $$\lambda_{\max}(r, r+1) = -T \ln(1 - \hat{\lambda}_{r+1})$$

---

## 2. Ornstein-Uhlenbeck (OU) Mean Reversion Stochastic Process

```
                          dX_t = θ(μ - X_t)dt + σ dW_t
        ┌────────────────────────────────────────────────────────┐
        │  Spread Level X_t                                      │
  +2σ   ├─────────────────────────────────────── Short Entry ────┤
        │           /\        /\      /\                         │
  μ     ├──────────/──\──────/──\────/──\─────── Equilibrium ───┤
        │         /    \    /    \  /    \                       │
  -2σ   ├────────/──────\──/──────\/──────\───── Long Entry ─────┤
        └────────────────────────────────────────────────────────┘
```

### A. Persamaan Diferensial Stokastik (SDE)
Penyimpangan spread pasangan aset $X_t = S_t - \mu$ dimodelkan sebagai proses Ornstein-Uhlenbeck kontinu:
$$dX_t = \theta (\mu - X_t) dt + \sigma dW_t$$
di mana:
- $\theta > 0$: *Mean reversion rate* (kecepatan gaya tarik menuju ekuilibrium).
- $\mu$: Tingkat ekuilibrium jangka panjang (*long-term mean*).
- $\sigma > 0$: Volatilitas difusi stokastik (*diffusion coefficient*).
- $W_t$: Proses Wiener standar (*Standard Brownian Motion*), $dW_t \sim \mathcal{N}(0, dt)$.

---

### B. Solusi Analitik Integrasi Itô & Distribusi Kondisional
Melalui integrasi menggunakan Lemma Itô pada fungsi pembantu $f(t, X_t) = X_t e^{\theta t}$:
$$X_t = X_0 e^{-\theta t} + \mu (1 - e^{-\theta t}) + \sigma \int_0^t e^{-\theta (t - s)} dW_s$$
Ekspektasi dan variansi kondisional:
$$\mathbb{E}[X_t \mid X_0] = \mu + (X_0 - \mu) e^{-\theta t}$$
$$\text{Var}(X_t \mid X_0) = \frac{\sigma^2}{2\theta} \left(1 - e^{-2\theta t}\right)$$
Distribusi stasioner jangka panjang ($t \to \infty$):
$$X_\infty \sim \mathcal{N}\left(\mu, \frac{\sigma^2}{2\theta}\right)$$

---

### C. Pemetaan AR(1) Diskrit & Kalibrasi Parameter MLE
Dalam data diskrit sampling interval $\Delta t = 1$, proses OU dipetakan secara eksak ke model autoregresif $AR(1)$:
$$X_{t} = a X_{t-1} + b + \eta_t, \quad \eta_t \sim \mathcal{N}(0, \sigma_\eta^2)$$
dengan transformasi koefisien analitik:
$$a = e^{-\theta \Delta t} \implies \theta = -\frac{\ln a}{\Delta t}$$
$$b = \mu (1 - a) \implies \mu = \frac{b}{1 - a}$$
$$\sigma_\eta^2 = \frac{\sigma^2}{2\theta}(1 - a^2) \implies \sigma = \sigma_\eta \sqrt{\frac{-2 \ln a}{\Delta t (1 - a^2)}}$$

---

### D. Half-Life of Mean Reversion ($\tau_{1/2}$) & Quantitative Filter
Waktu paruh yang dibutuhkan spread untuk memangkas setengah dari deviasi ekstremnya menuju nilai tengah:
$$\tau_{1/2} = \frac{\ln 2}{\theta} = -\frac{\Delta t \ln 2}{\ln a}$$

#### Invarian Seleksi Pasangan:
1. **Microstructure Noise Guard**: Jika $\tau_{1/2} < 3$ bars, spread didominasi oleh friksi bid-ask bounce; sinyal tidak dapat dieksekusi secara menguntungkan.
2. **Capital Efficiency Guard**: Jika $\tau_{1/2} > 90$ bars, pembalikan terlalu lambat; modal terkunci terlalu lama dengan risiko *structural divergence*.
3. **Sweet Spot**: Pasangan ideal memiliki $5 \le \tau_{1/2} \le 45$ bars dengan rasio $\frac{\sigma}{\sqrt{2\theta}}$ yang substansial melampaui biaya transaksi ganda.

---

## 3. Dynamic Online Hedge Ratio via 2D Kalman Filter

```
         ┌────────────────────────────────────────────────────────┐
         │              RECURSIVE KALMAN FILTER CYCLE             │
         └──────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
         ┌────────────────────────────────────────────────────────┐
         │ 1. Time Update (Predict)                               │
         │    θ̂_{t|t-1} = θ̂_{t-1|t-1}                             │
         │    P_{t|t-1} = P_{t-1|t-1} + Q                         │
         └──────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
         ┌────────────────────────────────────────────────────────┐
         │ 2. Measurement Update (Correct)                        │
         │    e_t = y_t - H_t θ̂_{t|t-1}   (Innovation Residual)   │
         │    S_t = H_t P_{t|t-1} H_t^T + R                       │
         │    K_t = P_{t|t-1} H_t^T S_t^{-1}                      │
         │    θ̂_{t|t} = θ̂_{t|t-1} + K_t e_t                       │
         │    P_{t|t} = (I - K_t H_t) P_{t|t-1}                   │
         └────────────────────────────────────────────────────────┘
```

### A. Mengapa Static OLS & Rolling Window Gagal
- **Static OLS**: Mengandung *lookahead bias* jika diestimasi pada seluruh dataset, atau tidak responsif terhadap pergeseran rezim ekonomi makro.
- **Rolling Window OLS**: Menimbulkan lag buatan sesuai panjang window $W$, rentan terhadap efek lonjakan keluar (*step-off distortion*) saat data outlier keluar dari window.

---

### B. Formulasi Ruang Keadaan (State-Space Formulation)
Estimasi dinamis intersep $\alpha_t$ dan rasio lindung nilai (*hedge ratio*) $\beta_t$:
- **Persamaan Keadaan (State Equation)**:
  $$\boldsymbol{\theta}_t = \begin{bmatrix} \alpha_t \\ \beta_t \end{bmatrix} = \boldsymbol{\theta}_{t-1} + \mathbf{w}_t, \quad \mathbf{w}_t \sim \mathcal{N}(\mathbf{0}, \mathbf{Q})$$
  dengan kovariansi noise proses $\mathbf{Q} = \begin{bmatrix} q_\alpha & 0 \\ 0 & q_\beta \end{bmatrix}$ (default $q_\alpha = 10^{-5}, q_\beta = 10^{-4}$).
- **Persamaan Pengukuran (Measurement Equation)**:
  $$y_t = \mathbf{H}_t \boldsymbol{\theta}_t + v_t, \quad \mathbf{H}_t = \begin{bmatrix} 1 & x_t \end{bmatrix}, \quad v_t \sim \mathcal{N}(0, R)$$
  dengan variansi noise observasi $R = \sigma_v^2$ (default $R = 10^{-3}$).

---

### C. Ekstraksi Residual Inovasi Real-Time
Residual inovasi $e_t = y_t - (\hat{\alpha}_t + \hat{\beta}_t x_t)$ merepresentasikan penyimpangan harga aktual terhadap nilai ekuilibrium yang diprediksi filter. Secara konstruksi, $e_t$ adalah spread bebas-bias yang siap dinormalisasi menjadi *Z-Score*.

---

## 4. Gold/Silver (XAU vs XAG) Ratio & Z-Score Trading Engine

```
                             GOLD/SILVER TRADING BANDS
      Z-Score
       +3.5 ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── EMERGENCY STOP (Short Co-drift)
       +2.0 ────────────────────────────────────────── ENTER SHORT SPREAD (Short XAU, Long β XAG)
        0.0 ────────────────────────────────────────── EXIT / MEAN-REVERSION FLAT
       -2.0 ────────────────────────────────────────── ENTER LONG SPREAD (Long XAU, Short β XAG)
       -3.5 ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── EMERGENCY STOP (Long Co-drift)
```

### A. Konstruksi Spread & Normalisasi Z-Score Adaptif
1. **Spread Logaritmik**:
   $$S_t = \ln(P_{\text{XAU}, t}) - \beta_t \ln(P_{\text{XAG}, t}) - \alpha_t$$
2. **Rolling Statistics (EMA-based)**:
   $$\mu_{S, t} = \lambda \mu_{S, t-1} + (1 - \lambda) S_t$$
   $$\sigma_{S, t}^2 = \lambda \sigma_{S, t-1}^2 + (1 - \lambda)(S_t - \mu_{S, t})^2$$
   $$Z_t = \frac{S_t - \mu_{S, t}}{\sigma_{S, t}}$$

---

### B. Finite State Machine (FSM) Logika Eksekusi
- **State 0 (FLAT)**:
  - Jika $Z_t \le -Z_{\text{entry}}$ (misal $-2.0$): Masuk **LONG SPREAD** (Beli 1 unit XAU, Jual $\beta_t$ unit XAG).
  - Jika $Z_t \ge +Z_{\text{entry}}$ (misal $+2.0$): Masuk **SHORT SPREAD** (Jual 1 unit XAU, Beli $\beta_t$ unit XAG).
- **State 1 (LONG SPREAD ACTIVE)**:
  - Jika $Z_t \ge -Z_{\text{exit}}$ (misal $0.0$): **CLOSE TAKE-PROFIT** (Tutup seluruh posisi kembali ke FLAT).
  - Jika $Z_t \le -Z_{\text{stop}}$ (misal $-3.5$): **EMERGENCY STOP-LOSS** (Deteksi kerusakan kointegrasi struktural).
- **State -1 (SHORT SPREAD ACTIVE)**:
  - Jika $Z_t \le +Z_{\text{exit}}$ (misal $0.0$): **CLOSE TAKE-PROFIT** (Tutup seluruh posisi kembali ke FLAT).
  - Jika $Z_t \ge +Z_{\text{stop}}$ (misal $+3.5$): **EMERGENCY STOP-LOSS** (Deteksi breakout divergent berbahaya).

---

### C. Pembatas Friksi Likuiditas & Slippage Hurdle
Perdagangan pasangan mengeksekusi 2 leg simultan, sehingga membayar biaya transaksi ganda:
$$\text{Cost}_{\text{total}} = 2 \times \left( \text{Fee}_{\text{XAU}} + \text{Slip}_{\text{XAU}} + \beta_t (\text{Fee}_{\text{XAG}} + \text{Slip}_{\text{XAG}}) \right)$$
**Hurdle Invariant**:
Sinyal hanya diizinkan membuka posisi jika ekspektasi pemulihan spread melampaui minimal $3.0 \times \text{Cost}_{\text{total}}$:
$$\mathbb{E}[\Delta S] = |Z_{\text{entry}} - Z_{\text{exit}}| \cdot \sigma_{S, t} \ge 3.0 \times \text{Cost}_{\text{total}}$$

---

## 5. Pure Python Standard Library Implementation & Self-Check

Implementasi mandiri tanpa dependensi pihak ketiga (*zero external dependencies*, stdlib `math`, `typing`, `dataclasses`, `random`). Seluruh fungsi diverifikasi melalui *assert test-suite* deterministik di bawah 1.0 detik.

```python
"""
Neuron N044: Statistical Arbitrage, Pairs Trading & Cointegration Engine.
Pure Python Standard Library (Zero External Dependencies).
"""

from typing import List, Tuple, Dict, Optional
import math
import random
import sys
from dataclasses import dataclass, field

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# =====================================================================
# 1. LINEAR ALGEBRA & STATISTICAL PRIMITIVES (STDLIB ONLY)
# =====================================================================

def mean(xs: List[float]) -> float:
    """Calculates sample arithmetic mean."""
    assert len(xs) > 0, "Cannot calculate mean of empty list"
    return sum(xs) / len(xs)

def variance(xs: List[float], ddof: int = 1) -> float:
    """Calculates sample variance with degrees of freedom correction."""
    n = len(xs)
    if n <= ddof:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (n - ddof)

def stdev(xs: List[float], ddof: int = 1) -> float:
    """Calculates sample standard deviation."""
    return math.sqrt(max(0.0, variance(xs, ddof)))

def covariance(xs: List[float], ys: List[float], ddof: int = 1) -> float:
    """Calculates sample covariance between two vectors."""
    n = len(xs)
    assert n == len(ys) and n > ddof, "Vectors must be equal length and > ddof"
    mx, my = mean(xs), mean(ys)
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / (n - ddof)

def correlation(xs: List[float], ys: List[float]) -> float:
    """Calculates Pearson correlation coefficient."""
    sx, sy = stdev(xs), stdev(ys)
    if sx == 0.0 or sy == 0.0:
        return 0.0
    return covariance(xs, ys) / (sx * sy)

def ols_1d(x: List[float], y: List[float]) -> Tuple[float, float, List[float]]:
    """
    Solves 1D Ordinary Least Squares: y = alpha + beta * x.
    Returns: (alpha, beta, residuals)
    """
    n = len(x)
    assert n == len(y) and n >= 3, "Insufficient data points for OLS"
    cov_xy = covariance(x, y)
    var_x = variance(x)
    beta = cov_xy / var_x if var_x > 1e-15 else 0.0
    alpha = mean(y) - beta * mean(x)
    residuals = [y[i] - (alpha + beta * x[i]) for i in range(n)]
    return alpha, beta, residuals

def mat_mul_2x2(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    """Multiplies two 2x2 matrices."""
    return [
        [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
        [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]
    ]

def mat_inv_2x2(A: List[List[float]]) -> List[List[float]]:
    """Inverts a 2x2 matrix."""
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    assert abs(det) > 1e-15, "Singular 2x2 matrix cannot be inverted"
    inv_det = 1.0 / det
    return [
        [A[1][1] * inv_det, -A[0][1] * inv_det],
        [-A[1][0] * inv_det, A[0][0] * inv_det]
    ]

def eigenvalues_2x2(A: List[List[float]]) -> Tuple[float, float]:
    """Computes sorted eigenvalues (lambda_1 >= lambda_2) of a 2x2 matrix."""
    tr = A[0][0] + A[1][1]
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    disc = tr * tr - 4.0 * det
    disc = max(0.0, disc)
    sqrt_d = math.sqrt(disc)
    l1 = (tr + sqrt_d) / 2.0
    l2 = (tr - sqrt_d) / 2.0
    return (l1, l2) if l1 >= l2 else (l2, l1)


# =====================================================================
# 2. AUGMENTED DICKEY-FULLER (ADF) & ENGLE-GRANGER TEST
# =====================================================================

class EconometricTests:
    """Stationarity and Cointegration testing suite."""

    @staticmethod
    def adf_test_residuals(residuals: List[float], max_lags: int = 1) -> Tuple[float, bool]:
        """
        Augmented Dickey-Fuller unit-root test on cointegrating regression residuals.
        Model: delta e_t = gamma * e_{t-1} + sum(delta_i * delta e_{t-i})
        Without drift constant (since residuals have zero mean).
        Returns: (t_statistic, is_stationary_at_5pct)
        """
        n = len(residuals)
        assert n > max_lags + 10, "Time series too short for ADF test"
        
        de = [residuals[i] - residuals[i-1] for i in range(1, n)]
        
        X: List[List[float]] = []
        Y: List[float] = []
        for t in range(max_lags, len(de)):
            row = [residuals[t]]  # e_{t-1} in continuous time indexing
            for lag in range(1, max_lags + 1):
                row.append(de[t - lag])
            X.append(row)
            Y.append(de[t])
            
        N = len(Y)
        k = len(X[0])
        
        # XtX and XtY
        XtX = [[sum(X[i][r] * X[i][c] for i in range(N)) for c in range(k)] for r in range(k)]
        XtY = [sum(X[i][r] * Y[i] for i in range(N)) for r in range(k)]
        
        inv_XtX = mat_inv_2x2(XtX) if k == 2 else [[1.0 / XtX[0][0]]]
        
        if k == 2:
            gamma = inv_XtX[0][0] * XtY[0] + inv_XtX[0][1] * XtY[1]
            delta = inv_XtX[1][0] * XtY[0] + inv_XtX[1][1] * XtY[1]
            res = [Y[i] - (gamma * X[i][0] + delta * X[i][1]) for i in range(N)]
        else:
            gamma = inv_XtX[0][0] * XtY[0]
            res = [Y[i] - gamma * X[i][0] for i in range(N)]
            
        s2 = sum(r * r for r in res) / max(1, N - k)
        se_gamma = math.sqrt(max(1e-15, s2 * inv_XtX[0][0]))
        t_stat = gamma / se_gamma if se_gamma > 0 else 0.0
        
        # MacKinnon 5% critical value for cointegrating residuals (2 variables)
        crit_5pct = -3.34
        is_stationary = t_stat < crit_5pct
        return t_stat, is_stationary

    @staticmethod
    def engle_granger_2step(y: List[float], x: List[float]) -> Tuple[float, float, float, bool]:
        """
        Executes Engle-Granger Two-Step Cointegration Test.
        Step 1: OLS Regression y = alpha + beta * x
        Step 2: ADF test on residuals
        Returns: (alpha, beta, adf_t_stat, is_cointegrated)
        """
        alpha, beta, residuals = ols_1d(x, y)
        adf_stat, is_coint = EconometricTests.adf_test_residuals(residuals, max_lags=1)
        return alpha, beta, adf_stat, is_coint

    @staticmethod
    def johansen_bivariate_trace(y1: List[float], y2: List[float]) -> Tuple[float, float, int]:
        """
        Bivariate Johansen Cointegration Trace Test.
        Calculates trace statistics for r=0 and r<=1.
        Returns: (trace_r0, trace_r1, estimated_rank_r)
        """
        n = len(y1)
        assert n == len(y2) and n > 30, "Insufficient observations for Johansen test"
        
        # 1. First differences
        dy1 = [y1[i] - y1[i-1] for i in range(1, n)]
        dy2 = [y2[i] - y2[i-1] for i in range(1, n)]
        
        # 2. Auxiliary regressions on lagged differences (1 lag)
        # Current diffs: t = 1 .. len(dy1)-1
        dy1_curr = dy1[1:]
        dy2_curr = dy2[1:]
        dy1_lag = dy1[:-1]
        dy2_lag = dy2[:-1]
        y1_lag = y1[1:-1]
        y2_lag = y2[1:-1]

        _, _, r0_1 = ols_1d(dy1_lag, dy1_curr)
        _, _, r0_2 = ols_1d(dy2_lag, dy2_curr)
        _, _, r1_1 = ols_1d(dy1_lag, y1_lag)
        _, _, r1_2 = ols_1d(dy2_lag, y2_lag)

        T = len(r0_1)
        R0 = [[r0_1[i], r0_2[i]] for i in range(T)]
        R1 = [[r1_1[i], r1_2[i]] for i in range(T)]

        # 3. Product Moment Matrices S00, S01, S10, S11
        S00 = [[sum(R0[i][r] * R0[i][c] for i in range(T)) / T for c in range(2)] for r in range(2)]
        S01 = [[sum(R0[i][r] * R1[i][c] for i in range(T)) / T for c in range(2)] for r in range(2)]
        S10 = [[S01[c][r] for c in range(2)] for r in range(2)]
        S11 = [[sum(R1[i][r] * R1[i][c] for i in range(T)) / T for c in range(2)] for r in range(2)]
        
        # 4. Matrix M = S11^{-1} * S10 * S00^{-1} * S01
        inv_S00 = mat_inv_2x2(S00)
        inv_S11 = mat_inv_2x2(S11)
        
        M_temp = mat_mul_2x2(S10, inv_S00)
        M_temp2 = mat_mul_2x2(M_temp, S01)
        M = mat_mul_2x2(inv_S11, M_temp2)
        
        l1, l2 = eigenvalues_2x2(M)
        l1 = min(max(0.0, l1), 0.999999)
        l2 = min(max(0.0, l2), 0.999999)
        
        # 5. Trace Statistics
        trace_r0 = -T * (math.log(1.0 - l1) + math.log(1.0 - l2))
        trace_r1 = -T * math.log(1.0 - l2)
        
        # Critical values at 5% (Osterwald-Lenum / Johansen): r=0 -> 15.49, r<=1 -> 3.84
        if trace_r0 > 15.49:
            rank = 2 if trace_r1 > 3.84 else 1
        else:
            rank = 0
            
        return trace_r0, trace_r1, rank


# =====================================================================
# 3. ORNSTEIN-UHLENBECK CONTINUOUS PROCESS CALIBRATOR
# =====================================================================

@dataclass
class OUParameters:
    theta: float       # Mean reversion speed
    mu: float          # Long-term equilibrium level
    sigma: float        # Diffusion volatility
    half_life: float   # Half-life of mean reversion in time steps
    is_valid_arb: bool # Meets quantitative trading duration invariants

class OrnsteinUhlenbeckEstimator:
    """Calibrates continuous SDE dX_t = theta * (mu - X_t) dt + sigma * dW_t from discrete data."""

    @staticmethod
    def fit(series: List[float], dt: float = 1.0) -> OUParameters:
        """
        Fits OU process parameters using exact discrete AR(1) OLS mapping.
        X_t = a * X_{t-1} + b + eps
        """
        n = len(series)
        assert n >= 10, "Need at least 10 points to estimate OU process"
        
        x_prev = series[:-1]
        x_curr = series[1:]
        
        b_ols, a_ols, residuals = ols_1d(x_prev, x_curr)
        
        # If a >= 1.0 or a <= 0.0, process is non-stationary or oscillating explosively
        if a_ols >= 0.999999 or a_ols <= 0.000001:
            return OUParameters(theta=0.0, mu=mean(series), sigma=stdev(series), half_life=float('inf'), is_valid_arb=False)
            
        theta = -math.log(a_ols) / dt
        mu = b_ols / (1.0 - a_ols)
        
        sigma_eps = stdev(residuals)
        denom = dt * (1.0 - a_ols * a_ols)
        sigma = sigma_eps * math.sqrt((-2.0 * math.log(a_ols)) / denom) if denom > 0 else 0.0
        
        half_life = (math.log(2.0) / theta) if theta > 1e-12 else float('inf')
        
        # Quantitative Arb Validity: Half life between 3 and 100 bars
        is_valid_arb = 3.0 <= half_life <= 100.0 and theta > 0.0
        
        return OUParameters(theta=theta, mu=mu, sigma=sigma, half_life=half_life, is_valid_arb=is_valid_arb)


# =====================================================================
# 4. ONLINE DYNAMIC KALMAN FILTER HEDGE RATIO
# =====================================================================

class KalmanFilterPairs:
    """
    2D Online Adaptive Kalman Filter for Dynamic Hedge Ratio (alpha, beta).
    State vector: [alpha_t, beta_t]^T
    Measurement: y_t = alpha_t + beta_t * x_t + v_t
    """
    def __init__(self, delta_process_noise: float = 1e-4, measurement_noise_R: float = 1e-3):
        # State estimate: [alpha, beta]
        self.theta = [0.0, 1.0]
        
        # State error covariance P (2x2)
        self.P = [[1.0, 0.0], [0.0, 1.0]]
        
        # Process noise covariance Q (2x2)
        q_alpha = delta_process_noise * 0.1
        q_beta = delta_process_noise
        self.Q = [[q_alpha, 0.0], [0.0, q_beta]]
        
        # Measurement noise variance R
        self.R = measurement_noise_R
        
        # History
        self.alpha_history: List[float] = []
        self.beta_history: List[float] = []
        self.spread_innovations: List[float] = []

    def update(self, x_t: float, y_t: float) -> Tuple[float, float, float]:
        """
        Performs recursive Kalman predict and update cycle with new price observation (x_t, y_t).
        Returns: (alpha_estimate, beta_estimate, innovation_residual_spread)
        """
        # 1. Predict Step
        # theta_{t|t-1} = theta_{t-1|t-1}
        # P_{t|t-1} = P_{t-1|t-1} + Q
        P_prior = [
            [self.P[0][0] + self.Q[0][0], self.P[0][1] + self.Q[0][1]],
            [self.P[1][0] + self.Q[1][0], self.P[1][1] + self.Q[1][1]]
        ]
        
        # 2. Measurement Vector H = [1.0, x_t]
        H = [1.0, x_t]
        
        # Innovation residual: e_t = y_t - H * theta
        y_pred = H[0] * self.theta[0] + H[1] * self.theta[1]
        e_t = y_t - y_pred
        
        # Innovation variance: S_t = H * P_prior * H^T + R
        # P_prior * H^T:
        PHt = [
            P_prior[0][0] * H[0] + P_prior[0][1] * H[1],
            P_prior[1][0] * H[0] + P_prior[1][1] * H[1]
        ]
        S_t = H[0] * PHt[0] + H[1] * PHt[1] + self.R
        
        # Kalman Gain: K = PHt / S_t
        K = [PHt[0] / S_t, PHt[1] / S_t]
        
        # 3. Posterior State Update: theta = theta + K * e_t
        self.theta[0] += K[0] * e_t
        self.theta[1] += K[1] * e_t
        
        # 4. Posterior Covariance: P = (I - K * H) * P_prior
        # KH matrix (2x2):
        # [[K[0]*H[0], K[0]*H[1]], [K[1]*H[0], K[1]*H[1]]]
        I_KH = [
            [1.0 - K[0] * H[0], -K[0] * H[1]],
            [-K[1] * H[0], 1.0 - K[1] * H[1]]
        ]
        self.P = mat_mul_2x2(I_KH, P_prior)
        
        # Store history
        self.alpha_history.append(self.theta[0])
        self.beta_history.append(self.theta[1])
        self.spread_innovations.append(e_t)
        
        return self.theta[0], self.theta[1], e_t


# =====================================================================
# 5. STATISTICAL ARBITRAGE PAIRS TRADING SIMULATION ENGINE
# =====================================================================

@dataclass
class TradeRecord:
    entry_idx: int
    exit_idx: int
    direction: str       # "LONG_SPREAD" or "SHORT_SPREAD"
    entry_z: float
    exit_z: float
    entry_spread: float
    exit_spread: float
    gross_pnl: float
    net_pnl: float
    exit_reason: str     # "TAKE_PROFIT", "STOP_LOSS", "TIME_STOP"

class PairsTradingEngine:
    """
    Gold (XAU) / Silver (XAG) Statistical Arbitrage Trading Engine.
    Employs Dynamic Kalman Hedge Ratio + Rolling Z-Score Bands + Structural Stop Guard.
    """
    def __init__(
        self,
        z_entry: float = 2.0,
        z_exit: float = 0.0,
        z_stop: float = 3.5,
        ema_span: int = 20,
        fee_bps: float = 2.0,       # 2 bps transaction fee per leg
        slippage_bps: float = 1.5   # 1.5 bps slippage per leg
    ):
        self.z_entry = z_entry
        self.z_exit = z_exit
        self.z_stop = z_stop
        self.ema_alpha = 2.0 / (ema_span + 1.0)
        self.friction_rate = (fee_bps + slippage_bps) * 1e-4
        
        self.kf = KalmanFilterPairs()
        self.spread_mean: Optional[float] = None
        self.spread_var: Optional[float] = None
        
        # State Machine: 0 = Flat, 1 = Long Spread, -1 = Short Spread
        self.position: int = 0
        self.entry_idx: int = 0
        self.entry_z: float = 0.0
        self.entry_spread: float = 0.0
        self.trades: List[TradeRecord] = []

    def process_tick(self, idx: int, p_xau: float, p_xag: float) -> Tuple[float, float, int]:
        """
        Ingests synchronized price tick. Updates filter, z-score, and executes state machine.
        Returns: (current_beta, current_z_score, current_position_state)
        """
        # Dynamic Hedge Ratio update
        log_xau = math.log(p_xau)
        log_xag = math.log(p_xag)
        alpha, beta, spread = self.kf.update(log_xag, log_xau)
        
        # Rolling EMA & Variance for Spread (Prior calculation prevents instant distortion of Z-Score)
        if self.spread_mean is None:
            self.spread_mean = spread
            self.spread_var = 1e-6
            z_score = 0.0
        else:
            spread_std = math.sqrt(max(1e-8, self.spread_var))
            z_score = (spread - self.spread_mean) / spread_std
            
            diff = spread - self.spread_mean
            self.spread_mean += self.ema_alpha * diff
            self.spread_var = (1.0 - self.ema_alpha) * self.spread_var + self.ema_alpha * (diff * diff)
        
        # FSM Execution Logic
        if self.position == 0:
            # Flat: Check Entry Thresholds
            if z_score <= -self.z_entry:
                self.position = 1
                self.entry_idx = idx
                self.entry_z = z_score
                self.entry_spread = spread
            elif z_score >= self.z_entry:
                self.position = -1
                self.entry_idx = idx
                self.entry_z = z_score
                self.entry_spread = spread
                
        elif self.position == 1:
            # Long Spread Active (Bought XAU, Sold beta XAG) -> Profits when spread expands
            if z_score >= -self.z_exit:
                # Take profit on reversion to mean
                self._record_exit(idx, z_score, spread, "TAKE_PROFIT", beta)
            elif z_score <= -self.z_stop:
                # Emergency stop on co-drift divergence breakdown
                self._record_exit(idx, z_score, spread, "STOP_LOSS", beta)
                
        elif self.position == -1:
            # Short Spread Active (Sold XAU, Bought beta XAG) -> Profits when spread narrows
            if z_score <= self.z_exit:
                # Take profit on reversion to mean
                self._record_exit(idx, z_score, spread, "TAKE_PROFIT", beta)
            elif z_score >= self.z_stop:
                # Emergency stop on co-drift divergence breakdown
                self._record_exit(idx, z_score, spread, "STOP_LOSS", beta)
                
        return beta, z_score, self.position

    def _record_exit(self, exit_idx: int, exit_z: float, exit_spread: float, reason: str, beta: float):
        """Calculates PnL and logs closed trade."""
        delta_spread = exit_spread - self.entry_spread
        gross_pnl = delta_spread if self.position == 1 else -delta_spread
        
        # Roundtrip 2-leg friction
        friction = 2.0 * self.friction_rate * (1.0 + abs(beta))
        net_pnl = gross_pnl - friction
        
        trade = TradeRecord(
            entry_idx=self.entry_idx,
            exit_idx=exit_idx,
            direction="LONG_SPREAD" if self.position == 1 else "SHORT_SPREAD",
            entry_z=self.entry_z,
            exit_z=exit_z,
            entry_spread=self.entry_spread,
            exit_spread=exit_spread,
            gross_pnl=gross_pnl,
            net_pnl=net_pnl,
            exit_reason=reason
        )
        self.trades.append(trade)
        self.position = 0


# =====================================================================
# 6. RUNNABLE INVARIANT VERIFICATION SUITE (STDLIB SELF-CHECK)
# =====================================================================

def generate_synthetic_data(seed: int = 42) -> Tuple[List[float], List[float], List[float]]:
    """
    Generates synthetic cointegrated pairs (Gold/Silver proxy) and random walk data.
    True relationship: y_t = 0.5 + 2.2 * x_t + OU_spread_t
    """
    random.seed(seed)
    n = 300
    
    # 1. Driver asset (Silver Proxy X) ~ Geometric Random Walk
    x = [30.0]
    for _ in range(1, n):
        drift = 0.0002
        shock = random.gauss(0.0, 0.015)
        x.append(x[-1] * math.exp(drift + shock))
        
    # 2. Cointegrated Mean-Reverting Spread (OU Process: theta=0.15, mu=0.0, sigma=0.03)
    ou_spread = [0.0]
    theta_true = 0.15
    for _ in range(1, n):
        d_spread = -theta_true * ou_spread[-1] + random.gauss(0.0, 0.03)
        ou_spread.append(ou_spread[-1] + d_spread)
        
    # 3. Dependent Asset (Gold Proxy Y)
    # log(Y_t) = 0.5 + 2.2 * log(X_t) + ou_spread_t
    y = [math.exp(0.5 + 2.2 * math.log(x[i]) + ou_spread[i]) for i in range(n)]
    
    # 4. Spurious Uncorrelated Random Walk Z
    z = [100.0]
    for _ in range(1, n):
        z.append(z[-1] * math.exp(random.gauss(0.0, 0.02)))
        
    return x, y, z

def run_all_invariants():
    print("[*] Starting Neuron N044 Invariant Verification Suite (Pure Stdlib)...")
    
    # -------------------------------------------------------------
    # Invariant 1: Linear Algebra & OLS Determinism
    # -------------------------------------------------------------
    A = [[2.0, 1.0], [1.0, 2.0]]
    invA = mat_inv_2x2(A)
    assert abs(invA[0][0] - 2.0/3.0) < 1e-10, "Matrix inverse calculation failed"
    l1, l2 = eigenvalues_2x2(A)
    assert abs(l1 - 3.0) < 1e-10 and abs(l2 - 1.0) < 1e-10, "Eigenvalue calculation failed"
    print("  [✓] Invariant 1: 2x2 Matrix Inversion & Eigenvalue Solver verified.")

    # -------------------------------------------------------------
    # Invariant 2: Engle-Granger & ADF Cointegration Identification
    # -------------------------------------------------------------
    x_data, y_data, z_spurious = generate_synthetic_data(seed=1337)
    
    # Test True Cointegrated Pair (X vs Y)
    log_x = [math.log(p) for p in x_data]
    log_y = [math.log(p) for p in y_data]
    alpha_est, beta_est, adf_stat, is_coint = EconometricTests.engle_granger_2step(log_y, log_x)
    
    assert is_coint, f"Engle-Granger failed to detect true cointegration (t={adf_stat:.3f})"
    assert abs(beta_est - 2.2) < 0.25, f"Beta estimate {beta_est:.3f} deviates from true beta 2.2"
    
    # Test Spurious Uncorrelated Pair (X vs Z)
    log_z = [math.log(p) for p in z_spurious]
    _, _, adf_stat_spur, is_coint_spur = EconometricTests.engle_granger_2step(log_z, log_x)
    assert not is_coint_spur, f"Engle-Granger falsely accepted spurious pair (t={adf_stat_spur:.3f})"
    print(f"  [✓] Invariant 2: Engle-Granger Cointegration correctly discriminated (Coint t={adf_stat:.2f} < -3.34, Spurious t={adf_stat_spur:.2f}).")

    # -------------------------------------------------------------
    # Invariant 3: Bivariate Johansen Trace Test
    # -------------------------------------------------------------
    trace0, trace1, rank = EconometricTests.johansen_bivariate_trace(log_y, log_x)
    assert rank >= 1, f"Johansen test failed to identify cointegrating rank >= 1 (rank={rank}, trace0={trace0:.2f})"
    print(f"  [✓] Invariant 3: Johansen VECM Trace Test confirmed cointegration rank r={rank} (Trace0={trace0:.2f} > 15.49).")

    # -------------------------------------------------------------
    # Invariant 4: Ornstein-Uhlenbeck Parameter & Half-Life Recovery
    # -------------------------------------------------------------
    # Known OU series with theta = 0.20 (Half-life = ln(2)/0.20 = 3.46 bars)
    ou_sample = [0.0]
    random.seed(999)
    for _ in range(500):
        ou_sample.append(ou_sample[-1] - 0.20 * ou_sample[-1] + random.gauss(0.0, 0.05))
    
    ou_params = OrnsteinUhlenbeckEstimator.fit(ou_sample)
    assert ou_params.is_valid_arb, "OU Estimator flagged valid mean-reverting series as invalid"
    assert 2.0 <= ou_params.half_life <= 5.5, f"Estimated half-life {ou_params.half_life:.2f} outside expected range [2.0, 5.5]"
    assert abs(ou_params.mu) < 0.1, f"Estimated mean {ou_params.mu:.3f} deviates from zero"
    print(f"  [✓] Invariant 4: Ornstein-Uhlenbeck SDE Calibration recovered theta={ou_params.theta:.3f}, Half-Life={ou_params.half_life:.2f} bars.")

    # -------------------------------------------------------------
    # Invariant 5: Dynamic Kalman Filter Hedge Ratio Adaptation
    # -------------------------------------------------------------
    kf = KalmanFilterPairs()
    # Feed pair with sudden structural break at t=150 (beta jumps from 2.0 to 3.0)
    for t in range(300):
        px = 10.0 + random.gauss(0.0, 0.2)
        true_b = 2.0 if t < 150 else 3.0
        py = 1.0 + true_b * px + random.gauss(0.0, 0.1)
        a_t, b_t, e_t = kf.update(px, py)
        
    final_beta = kf.theta[1]
    assert abs(final_beta - 3.0) < 0.3, f"Kalman Filter failed to adapt to structural break (beta={final_beta:.3f}, expected ~3.0)"
    print(f"  [✓] Invariant 5: Kalman Filter dynamic hedge ratio tracked structural regime shift ({final_beta:.3f} ~ 3.00).")

    # -------------------------------------------------------------
    # Invariant 6: Pairs Trading State Machine & Stop-Loss Circuit Breaker
    # -------------------------------------------------------------
    engine = PairsTradingEngine(z_entry=1.8, z_exit=0.1, z_stop=3.5)
    for idx in range(len(x_data)):
        engine.process_tick(idx, y_data[idx], x_data[idx])
        
    assert len(engine.trades) > 0, "Pairs trading engine did not generate any trades"
    
    # Test emergency stop circuit breaker on divergent anomaly
    engine_stop_test = PairsTradingEngine(z_entry=1.8, z_exit=0.1, z_stop=3.0)
    engine_stop_test.process_tick(0, 1000.0, 20.0)
    engine_stop_test.process_tick(1, 1000.0, 20.0)
    # Force extreme divergent spike to trigger stop loss (Long position with collapsing spread)
    engine_stop_test.position = 1
    engine_stop_test.entry_idx = 2
    engine_stop_test.entry_spread = -0.5
    engine_stop_test.spread_mean = 0.0
    engine_stop_test.spread_var = 0.01
    
    # Tick with extreme spread collapse (p_xau drops, p_xag rises -> spread << 0 -> Z < -3.0)
    beta_out, z_out, pos_out = engine_stop_test.process_tick(3, 100.0, 1000.0)
    stop_trades = [t for t in engine_stop_test.trades if t.exit_reason == "STOP_LOSS"]
    assert len(stop_trades) > 0 and pos_out == 0, "Emergency circuit breaker failed to trigger on divergence"
    print(f"  [✓] Invariant 6: Pairs Trading State Machine executed {len(engine.trades)} trades with active Stop-Loss circuit breaker.")

    print("\n[SUCCESS] All 6 Neuron N044 Invariants Verified (100% Stdlib Deterministic Passing).")

if __name__ == "__main__":
    run_all_invariants()
```
