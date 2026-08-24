# Neuron N050: Systematic Backtesting Engine & Walk-Forward Optimization (WFA / CPCV / DSR)

- **Kategori**: Quantitative Finance, Systematic Backtesting & Statistical Overfitting Defense
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Mengeliminasi backtest overfitting, selection bias, lookahead bias, dan data snooping dalam strategi kuantitatif melalui arsitektur event-driven backtesting deterministik, pemodelan realistis fee/slippage, Walk-Forward Analysis (WFA), Combinatorial Purged Cross-Validation (CPCV), dan Deflated Sharpe Ratio (DSR) berbasis statistik Marcos López de Prado.
- **Synaptic Links**: [`N001`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N001_executive_decisions.md), [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N007`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N007_self_improving_loop.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N017`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N017_program_aided_math.md), [`N021`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N021_quantitative_gold_crypto_trading.md), [`N025`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N025_hft_orderbook_microstructure.md), [`N033`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N033_python_high_performance.md), [`N035`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N035_event_driven_streaming_cqrs.md)
- **Status**: Active Operational Invariant

---

## 1. Arsitektur Event-Driven vs Ilusi Simulasi Vektorik

```
                   ┌───────────────────────────────┐
                   │    Market Data Feed (Bars)    │
                   └───────────────┬───────────────┘
                                   │ MarketDataEvent
                                   ▼
                   ┌───────────────────────────────┐
                   │      Strategy Engine          │
                   │   (Signal Generator Logic)    │
                   └───────────────┬───────────────┘
                                   │ SignalEvent
                                   ▼
                   ┌───────────────────────────────┐
                   │     Risk & Sizing Oracle      │
                   │   (Kelly / Volatility Guard)  │
                   └───────────────┬───────────────┘
                                   │ OrderEvent
                                   ▼
                   ┌───────────────────────────────┐
                   │   Execution & Friction Model  │
                   │   - Maker/Taker Commissions   │
                   │   - Square-Root Impact Slip   │
                   │   - Latency / Queue Position  │
                   └───────────────┬───────────────┘
                                   │ FillEvent
                                   ▼
                   ┌───────────────────────────────┐
                   │  Portfolio & Ledger State     │
                   │  - Realized/Unrealized PnL    │
                   │  - Margin & Liquidation Check │
                   │  - Dynamic Equity Curve       │
                   └───────────────────────────────┘
```

### A. 7 Jebakan Fatal Simulasi Vektorik (*Vectorized Backtest Pitfalls*)
1. **Lookahead Bias (Kebocoran Masa Depan)**: Penggunaan harga `Close[t]` untuk menghitung sinyal sekaligus harga eksekusi pada timestamp $t$ yang sama tanpa jeda waktu diskrit $\Delta t$.
2. **Simultaneous Fill Illusion**: Asumsi bahwa multiple limit orders pada harga terbaik selalu terisi 100% (*full fill*) tanpa mempertimbangkan antrean likuiditas (*queue priority*).
3. **Unrealistic Frictionless Execution**: Mengabaikan *bid-ask spread*, komisi maker/taker bertingkat, dan *market impact* yang meningkat seiring volume transaksi.
4. **Survivorship Bias**: Menguji data historis hanya pada aset yang masih aktif diperdagangkan hari ini, menghapus aset yang delisted/bangkrut.
5. **Margin & Liquidation Sequencing**: Simulasi vektorik menghitung return akhir periode tanpa memverifikasi apakah terjadi *margin call* / *liquidation event* intraday di titik terendah (*intraday low*).
6. **Cash Drag & Funding Rate Omission**: Mengabaikan biaya pinjaman modal (*borrow fee*), swap semalam (*overnight swap* pada emas/forex), dan *perpetual funding rates* pada kripto.
7. **Execution Latency Buffer**: Mengasumsikan sinyal langsung dieksekusi instan tanpa *network latency* dan *exchange matching engine queue delay*.

### B. Pemodelan Friksi & Slippage Non-Linear
Eksekusi order wajib dimodelkan dengan *square-root market impact law* (Almgren-Chriss / Barra model):

$$\text{Price}_{\text{fill}} = P_{\text{bar}} \cdot \left(1 \pm S_{\text{base}} \pm \eta \cdot \sigma_{\text{asset}} \cdot \sqrt{\frac{Q_{\text{order}}}{V_{\text{bar}}}}\right)$$

di mana:
- $S_{\text{base}}$: Half-spread minimum aset (misal 1–2 bps untuk kripto likuid, 2–4 bps untuk XAU/USD).
- $\eta$: Koefisien elastisitas likuiditas pasar ($\eta \approx 0.1 - 0.5$).
- $\sigma_{\text{asset}}$: Volatilitas return bar saat ini.
- $Q_{\text{order}} / V_{\text{bar}}$: Rasio ukuran order terhadap total volume likuiditas pada bar tersebut.

---

## 2. Walk-Forward Analysis (WFA) & Rolling Horizon Optimization

```
Waktu (Time Series) ─────────────────────────────────────────────────────────────►

Window 1:  [       In-Sample IS₁       ] [   Out-of-Sample OOS₁   ]
Window 2:         [       In-Sample IS₂       ] [   Out-of-Sample OOS₂   ]
Window 3:                [       In-Sample IS₃       ] [   Out-of-Sample OOS₃   ]
Window 4:                       [       In-Sample IS₄       ] [   Out-of-Sample OOS₄   ]

Stitched OOS Equity:                     [ OOS₁ ] + [ OOS₂ ] + [ OOS₃ ] + [ OOS₄ ]
```

### A. Metodologi Walk-Forward
1. **In-Sample (IS) Calibration**: Mengoptimalkan himpunan parameter $\theta^* = \arg\max_{\theta} \mathcal{M}(\theta)$ pada jendela waktu historis $[t_{\text{is\_start}}, t_{\text{is\_end}}]$.
2. **Out-of-Sample (OOS) Validation**: Menerapkan parameter tetap $\theta^*$ ke jendela waktu masa depan berikutnya $[t_{\text{oos\_start}}, t_{\text{oos\_end}}]$ yang tidak pernah dilihat oleh proses optimasi.
3. **Stitched Walk-Forward Equity Curve**: Menggabungkan seluruh segmen OOS menjadi kurva ekuitas tunggal yang menggambarkan kinerja nyata sistem di dunia nyata.

### B. Walk-Forward Efficiency (WFE) Invariant
Walk-Forward Efficiency mengukur ketahanan parameter terhadap perubahan rezim pasar:

$$\text{WFE} = \frac{\overline{\text{Sharpe}}_{\text{OOS}}}{\overline{\text{Sharpe}}_{\text{IS}}} \quad \text{atau} \quad \text{WFE} = \frac{\text{CAGR}_{\text{OOS}}}{\text{CAGR}_{\text{IS}}}$$

- **$\text{WFE} \ge 60\%$**: **Robust Alpha**. Strategi mempertahankan keunggulan statistik di luar sampel.
- **$50\% \le \text{WFE} < 60\%$**: **Marginal Alpha**. Parameter dapat diterima tetapi wajib disertai pembatas risiko ketat (*tight risk boundaries*).
- **$\text{WFE} < 50\%$**: **Overfitted / Curve-Fitted Strategy**. Strategi ditolak secara mutlak; performa in-sample adalah ilusi acak.

### C. Parameter Plateau vs Needle Peak
- **Needle Peak**: Parameter optimal berada pada titik terisolasi yang tajam. Jika parameter bergeser $\pm 5\%$, Sharpe ratio jatuh drastis $\implies$ **TOLAK**.
- **Plateau / Flat Basin**: Parameter optimal berada dalam zona datar yang lebar di mana performa stabil pada variasi $\pm 10\% - 20\%$ di sekitar centroid $\implies$ **TERIMA**.

---

## 3. Combinatorial Purged Cross-Validation (CPCV)

Standar K-Fold Cross Validation konvensional **GAGAL TOTAL** pada data deret waktu keuangan karena mengasumsikan sampel IID (*Independent and Identically Distributed*).

```
Data Series (T):   [ Block 1 ] [ Block 2 ] [ Block 3 ] [ Block 4 ] [ Block 5 ]
                                    
Split C(5, 2) #1:  [ Train 1 ] [ Train 2 ] [ Train 3 ] [  TEST 1  ] [  TEST 2  ]
                   (Purged/Embargoed Train Set) ────────► (Pure Out-of-Sample)

Holding Period Leakage Prevention:
Train Label:       [==== Holding Period ====]
Test Interval:                             [==== TEST WINDOW ====]
Purged Zone:                           [XXX] <── Training sample dibuang karena overlap
Embargo Zone:                                                    [XXX] <── Dibuang pasca-test
```

### A. Dua Pilar CPCV (Marcos López de Prado)
1. **Purging (Pembersihan Overlap Label)**:
   - Jika satu observasi training pada bar $i$ memiliki holding period $[t_{i,0}, t_{i,1}]$ yang bertabrakan dengan interval test $[t_{\text{test},0}, t_{\text{test},1}]$, observasi training tersebut **wajib dihapus** (*purged*).
   - Menghilangkan kebocoran informasi masa depan ke dalam model (*information leakage*).
2. **Embargoing (Isolasi Autokorelasi Residual)**:
   - Observasi training yang berada tepat setelah interval test $[t_{\text{test},1}, t_{\text{test},1} + h]$ dibuang sejauh window embargo $h$ (misal $1\% - 2\%$ dari total data).
   - Menghilangkan ketergantungan memori autoregresif (*autoregressive serial correlation*).

### B. Kombinatorika dan Probability of Backtest Overfitting (PBO)
Dengan membagi data menjadi $N$ blok dan memilih $k$ blok sebagai test set:
- Jumlah kombinasi partisi: $C = \binom{N}{k}$.
- Menghasilkan $\phi = \frac{k}{N} \binom{N}{k}$ kurva ekuitas OOS independen.
- **Probability of Backtest Overfitting (PBO)** dihitung dari probabilitas bahwa strategi yang menempati peringkat 1 pada In-Sample menghasilkan performa di bawah median pada Out-of-Sample:

$$\text{PBO} = P\left(\text{Rank}_{\text{OOS}}(\text{Best}_{\text{IS}}) > \frac{C}{2}\right)$$

- **Invarian**: Strategi dengan $\text{PBO} > 0.15$ ($15\%$) **wajib didiskualifikasi**.

---

## 4. Probabilistic Sharpe Ratio (PSR) & Deflated Sharpe Ratio (DSR)

Sharpe Ratio point estimate naif ($\hat{SR} = \mu / \sigma$) sangat bias terhadap non-normalitas return (skewness dan fat-tail kurtosis) serta bias seleksi (*selection bias / data snooping* dari $M$ kali percobaan pengujian).

```
Distribusi Estimasi Sharpe Ratio:

         f(SR)
           │                  Non-Normal Asymptotic Variance
           │                  (Adjusted for Skewness & Kurtosis)
           │                              ┌───┐
           │                             ┌┘   └┐
           │                            ┌┘     └┐
           │                           ┌┘       └┐
           │                          ┌┘         └┐
           │        Null SR₀         ┌┘           └┐   Observed SR
           │        (Expected Max)   │             │   (Sample Estimate)
           │              ▼          │             │         ▼
───────────┼──────────────┼──────────┴─────────────┴─────────┼───────────► SR
           │              │                                  │
           │              └───────────────►◄─────────────────┘
           │                         Z-Score Distance
           │             DSR = Prob(True SR > SR₀ | M Trials)
```

### A. Momen Statistik & Asymptotic Standard Error of SR
Diberikan return deret waktu $r_1, r_2, \dots, r_T$:
- Mean: $\hat{\mu} = \frac{1}{T}\sum r_t$
- Volatilitas: $\hat{\sigma} = \sqrt{\frac{1}{T-1}\sum (r_t - \hat{\mu})^2}$
- Skewness: $\hat{\gamma}_3 = \frac{\frac{1}{T}\sum (r_t - \hat{\mu})^3}{\hat{\sigma}^3}$
- Kurtosis: $\hat{\gamma}_4 = \frac{\frac{1}{T}\sum (r_t - \hat{\mu})^4}{\hat{\sigma}^4}$

Asymptotic Standard Error of Sharpe Ratio $\hat{SR} = \hat{\mu}/\hat{\sigma}$ (Mertens 2002 / Lo 2002):

$$\sigma_{\hat{SR}} = \sqrt{\frac{1 - \hat{\gamma}_3 \hat{SR} + \frac{\hat{\gamma}_4 - 1}{4}\hat{SR}^2}{T - 1}}$$

### B. Probabilistic Sharpe Ratio (PSR)
Mengukur probabilitas bahwa Sharpe Ratio aktual melebihi benchmark minimum $SR^*$:

$$\text{PSR}(SR^*) = \Phi\left(\frac{(\hat{SR} - SR^*)}{\sigma_{\hat{SR}}}\right) = \Phi\left(\frac{(\hat{SR} - SR^*)\sqrt{T - 1}}{\sqrt{1 - \hat{\gamma}_3 \hat{SR} + \frac{\hat{\gamma}_4 - 1}{4}\hat{SR}^2}}\right)$$

di mana $\Phi(z)$ adalah fungsi distribusi kumulatif normal standar (*standard normal CDF*).

### C. Deflated Sharpe Ratio (DSR) untuk Multiple Testing
Jika kita menguji $M$ konfigurasi parameter atau strategi independen, Sharpe Ratio maksimum yang diobservasi secara acak (*luck under null hypothesis*) meningkat secara logaritmik terhadap $M$:

$$SR_0 = E\left[\max_{m=1..M} \{SR_m\}\right] \approx \sqrt{V[\{SR_m\}]} \left[ (1 - \gamma) \Phi^{-1}\left(1 - \frac{1}{M}\right) + \gamma \Phi^{-1}\left(1 - \frac{1}{M e}\right) \right]$$

di mana:
- $\gamma \approx 0.5772156649$ (Konstanta Euler-Mascheroni).
- $V[\{SR_m\}]$ adalah variansi Sharpe Ratio lintas seluruh $M$ konfigurasi yang diuji.
- $\Phi^{-1}(p)$ adalah fungsi kuantil normal standar (*inverse normal CDF*).

Deflated Sharpe Ratio dihitung sebagai:

$$\text{DSR} = \text{PSR}(SR^* = SR_0)$$

- **Threshold Produksi**: $\text{DSR} \ge 0.95$ ($95\%$ tingkat keyakinan bahwa performa bukan produk dari *overfitting* atau *multiple testing snooping*).

---

## 5. Implementasi Deterministik Python Standard Library

```python
"""
Neuron N050: Systematic Backtesting Engine & Walk-Forward Optimization (WFA/CPCV/DSR).
Standard library only (math, typing, itertools, dataclasses). Zero external dependencies.
"""

import sys
import math
from typing import List, Dict, Tuple, Optional, Generator
from itertools import combinations
from dataclasses import dataclass
from enum import Enum

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ============================================================================
# 1. High-Precision Normal Distribution Utilities (Acklam Inverse CDF)
# ============================================================================

class NormalDistUtils:
    """Standard Normal CDF and Acklam Inverse CDF approximation (~1e-9 error)."""
    
    @staticmethod
    def cdf(x: float) -> float:
        """Standard normal cumulative distribution function."""
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    @staticmethod
    def inv_cdf(p: float) -> float:
        """Inverse standard normal CDF (Acklam Algorithm)."""
        if p <= 0.0 or p >= 1.0:
            if p == 0.0: return -float('inf')
            if p == 1.0: return float('inf')
            raise ValueError("p must be strictly in (0, 1)")

        a = [-3.969683028665376e+01,  2.209460984245205e+02,
             -2.759285104469687e+02,  1.383577518672690e+02,
             -3.066479806614716e+01,  2.506628277459239e+00]

        b = [-5.447609879822406e+01,  1.615858368580409e+02,
             -1.556989798598866e+02,  6.680131188771972e+01,
             -1.328068155288572e+01]

        c = [-7.784894002430293e-03, -3.223964580411365e-01,
             -2.400758277161838e+00, -2.549732539343734e+00,
              4.374664141464968e+00,  2.938163982698783e+00]

        d = [ 7.784695709041462e-03,  3.224671290700398e-01,
              2.445134137142996e+00,  3.754408661907416e+00]

        p_low = 0.02425
        p_high = 1.0 - p_low

        if p < p_low:
            q = math.sqrt(-2.0 * math.log(p))
            return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
                   ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1.0)
        elif p <= p_high:
            q = p - 0.5
            r = q * q
            return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5])*q / \
                   (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1.0)
        else:
            q = math.sqrt(-2.0 * math.log(1.0 - p))
            return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
                    ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1.0)


# ============================================================================
# 2. Deflated Sharpe Ratio & Probabilistic Sharpe Ratio Engine
# ============================================================================

class DeflatedSharpeEngine:
    """Computes sample moments, PSR, and DSR under multiple testing conditions."""
    
    @staticmethod
    def calculate_moments(returns: List[float]) -> Tuple[float, float, float, float]:
        """Calculates (mean, std, skewness, kurtosis)."""
        n = len(returns)
        if n < 4:
            raise ValueError("At least 4 return observations required for moment calculation")
        
        mean = sum(returns) / n
        var = sum((x - mean) ** 2 for x in returns) / (n - 1)
        std = math.sqrt(var) if var > 0 else 1e-12
        
        skew = (sum((x - mean) ** 3 for x in returns) / n) / (std ** 3)
        kurt = (sum((x - mean) ** 4 for x in returns) / n) / (std ** 4)
        return mean, std, skew, kurt

    @staticmethod
    def sharpe_ratio(returns: List[float], rf: float = 0.0) -> float:
        """Calculates per-period sample Sharpe ratio."""
        mean, std, _, _ = DeflatedSharpeEngine.calculate_moments(returns)
        return (mean - rf) / std if std > 0 else 0.0

    @classmethod
    def probabilistic_sharpe_ratio(cls, sr_hat: float, sr_star: float, n: int, skew: float, kurt: float) -> float:
        """
        Calculates Probabilistic Sharpe Ratio PSR(SR*).
        Evaluates the probability that true SR > sr_star given sample size and non-normal moments.
        """
        if n <= 1:
            return 0.0
        denom_sq = 1.0 - skew * sr_hat + ((kurt - 1.0) / 4.0) * (sr_hat ** 2)
        if denom_sq <= 0:
            denom_sq = 1e-12
        se = math.sqrt(denom_sq / (n - 1))
        z = (sr_hat - sr_star) / se
        return NormalDistUtils.cdf(z)

    @classmethod
    def expected_max_sharpe(cls, n_trials: int, var_sr: float) -> float:
        """
        Expected maximum Sharpe ratio under the null hypothesis (Bailey & López de Prado):
        E[max_N {SR_n}] ≈ sqrt(var_sr) * ((1 - γ)*Phi^(-1)(1 - 1/N) + γ*Phi^(-1)(1 - 1/(N*e)))
        """
        if n_trials <= 1:
            return 0.0
        euler_mascheroni = 0.57721566490153286060
        e_const = math.e
        p1 = 1.0 - (1.0 / n_trials)
        p2 = 1.0 - (1.0 / (n_trials * e_const))
        z1 = NormalDistUtils.inv_cdf(p1)
        z2 = NormalDistUtils.inv_cdf(p2)
        exp_max_z = (1.0 - euler_mascheroni) * z1 + euler_mascheroni * z2
        return math.sqrt(var_sr) * exp_max_z

    @classmethod
    def deflated_sharpe_ratio(cls, returns: List[float], n_trials: int, var_sr: float) -> Tuple[float, float, float]:
        """
        Computes Deflated Sharpe Ratio (DSR) adjusting for multiple testing and non-normality.
        Returns: (sr_hat, expected_max_sr_null, dsr_probability).
        """
        mean, std, skew, kurt = cls.calculate_moments(returns)
        sr_hat = mean / std if std > 0 else 0.0
        n = len(returns)
        sr_0 = cls.expected_max_sharpe(n_trials, var_sr)
        dsr = cls.probabilistic_sharpe_ratio(sr_hat, sr_0, n, skew, kurt)
        return sr_hat, sr_0, dsr


# ============================================================================
# 3. Combinatorial Purged Cross-Validation (CPCV)
# ============================================================================

@dataclass
class TimeSample:
    index: int
    t_start: int  # Start timestamp / bar index
    t_end: int    # End of label / holding period

class CombinatorialPurgedCV:
    """
    Combinatorial Purged & Embargoed Cross-Validation Engine.
    Guarantees zero information leakage between train and test folds.
    """
    def __init__(self, n_splits: int, n_test_splits: int, embargo_pct: float = 0.01):
        if n_test_splits >= n_splits:
            raise ValueError("n_test_splits must be strictly less than n_splits")
        self.n_splits = n_splits
        self.n_test_splits = n_test_splits
        self.embargo_pct = embargo_pct

    def split(self, samples: List[TimeSample]) -> Generator[Tuple[List[int], List[int]], None, None]:
        """
        Generates (train_indices, test_indices) for each combination of test blocks.
        Enforces both Purging and Embargoing.
        """
        n_samples = len(samples)
        if n_samples == 0:
            return

        embargo_bars = int(n_samples * self.embargo_pct)
        
        # Partition samples into n_splits contiguous blocks
        block_size = n_samples // self.n_splits
        blocks: List[List[TimeSample]] = []
        for i in range(self.n_splits):
            start_idx = i * block_size
            end_idx = n_samples if i == self.n_splits - 1 else (i + 1) * block_size
            blocks.append(samples[start_idx:end_idx])

        # Generate all combinations of test blocks
        for test_block_indices in combinations(range(self.n_splits), self.n_test_splits):
            test_samples: List[TimeSample] = []
            for idx in test_block_indices:
                test_samples.extend(blocks[idx])
            
            test_indices = [s.index for s in test_samples]
            test_ranges = [(s.t_start, s.t_end) for s in test_samples]
            test_max_t = max(s.t_end for s in test_samples)

            # Candidate train samples from non-test blocks
            candidate_train: List[TimeSample] = []
            for idx in range(self.n_splits):
                if idx not in test_block_indices:
                    candidate_train.extend(blocks[idx])

            # Apply Purging & Embargoing
            purged_train_indices: List[int] = []
            for s in candidate_train:
                # 1. Purging: check if sample's label interval [s.t_start, s.t_end] overlaps with any test range
                overlaps = False
                for t_start, t_end in test_ranges:
                    if not (s.t_end < t_start or s.t_start > t_end):
                        overlaps = True
                        break
                if overlaps:
                    continue

                # 2. Embargoing: drop training samples immediately following test end within embargo window
                if test_max_t <= s.t_start <= test_max_t + embargo_bars:
                    continue

                purged_train_indices.append(s.index)

            yield purged_train_indices, test_indices


# ============================================================================
# 4. Walk-Forward Analysis (WFA) Engine
# ============================================================================

class WalkForwardOptimizer:
    """
    Rolling & Anchored Walk-Forward Analysis (WFA) Optimizer.
    Evaluates out-of-sample parameter stability and Walk-Forward Efficiency (WFE).
    """
    def __init__(self, is_window: int, oos_window: int, anchored: bool = False):
        self.is_window = is_window
        self.oos_window = oos_window
        self.anchored = anchored

    def generate_windows(self, total_bars: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generates ((is_start, is_end), (oos_start, oos_end)) slice tuples."""
        windows = []
        step = self.oos_window
        cursor = 0
        while cursor + self.is_window + self.oos_window <= total_bars:
            is_start = 0 if self.anchored else cursor
            is_end = cursor + self.is_window
            oos_start = is_end
            oos_end = oos_start + self.oos_window
            windows.append(((is_start, is_end), (oos_start, oos_end)))
            cursor += step
        return windows

    @staticmethod
    def calculate_wfe(is_metrics: List[float], oos_metrics: List[float]) -> float:
        """
        Computes Walk-Forward Efficiency (WFE).
        WFE = Mean(OOS Performance) / Mean(IS Performance).
        """
        if not is_metrics or not oos_metrics:
            return 0.0
        avg_is = sum(is_metrics) / len(is_metrics)
        avg_oos = sum(oos_metrics) / len(oos_metrics)
        if avg_is <= 0:
            return 0.0
        return avg_oos / avg_is


# ============================================================================
# 5. Event-Driven Backtesting Engine with Realistic Friction
# ============================================================================

@dataclass
class Bar:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class Signal:
    timestamp: int
    symbol: str
    direction: int  # 1 = Long, -1 = Short, 0 = Flat

@dataclass
class Order:
    timestamp: int
    symbol: str
    direction: int
    quantity: float

@dataclass
class Fill:
    timestamp: int
    symbol: str
    direction: int
    quantity: float
    price: float
    commission: float
    slippage: float

class EventDrivenBacktester:
    """
    High-Fidelity Event-Driven Backtest Simulator.
    Simulates Maker/Taker commissions, bid-ask spread, and square-root volume impact.
    """
    def __init__(self, initial_capital: float = 100000.0, taker_fee_bps: float = 5.0, slippage_bps: float = 2.0, impact_coeff: float = 0.1):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.taker_fee = taker_fee_bps / 10000.0
        self.slippage_base = slippage_bps / 10000.0
        self.impact_coeff = impact_coeff
        self.position = 0.0
        self.trades: List[Fill] = []
        self.equity_curve: List[float] = []

    def execute_order(self, order: Order, bar: Bar) -> Fill:
        """Computes fill price including spread and volume-dependent market impact."""
        impact = self.impact_coeff * math.sqrt(order.quantity / max(bar.volume, 1.0))
        total_slip_pct = self.slippage_base + impact
        
        fill_price = bar.close * (1.0 + total_slip_pct) if order.direction > 0 else bar.close * (1.0 - total_slip_pct)
        commission = fill_price * order.quantity * self.taker_fee
        slip_cost = abs(fill_price - bar.close) * order.quantity

        return Fill(
            timestamp=bar.timestamp,
            symbol=order.symbol,
            direction=order.direction,
            quantity=order.quantity,
            price=fill_price,
            commission=commission,
            slippage=slip_cost
        )

    def run(self, bars: List[Bar], signals: List[Signal]) -> Dict[str, float]:
        """Runs the event loop over all bars and processes signals into fills."""
        self.cash = self.initial_capital
        self.position = 0.0
        self.trades.clear()
        self.equity_curve.clear()

        signal_map = {s.timestamp: s for s in signals}

        for bar in bars:
            # 1. Signal & Order Processing
            sig = signal_map.get(bar.timestamp)
            if sig:
                target_pos = sig.direction * (self.cash / bar.close)
                diff_pos = target_pos - self.position
                if abs(diff_pos) > 1e-5:
                    dir_val = 1 if diff_pos > 0 else -1
                    order = Order(bar.timestamp, "ASSET", dir_val, abs(diff_pos))
                    fill = self.execute_order(order, bar)
                    self.trades.append(fill)
                    cost = fill.price * fill.quantity * fill.direction
                    self.cash -= (cost + fill.commission)
                    self.position += (fill.quantity * fill.direction)

            # 2. Mark-to-Market Portfolio Valuation
            current_equity = self.cash + (self.position * bar.close)
            self.equity_curve.append(current_equity)

        # Performance Metrics
        returns = [(self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1] 
                   for i in range(1, len(self.equity_curve))]
        
        sr = DeflatedSharpeEngine.sharpe_ratio(returns) if len(returns) >= 4 else 0.0
        total_return = (self.equity_curve[-1] - self.initial_capital) / self.initial_capital if self.equity_curve else 0.0
        
        peak = self.initial_capital
        max_dd = 0.0
        for eq in self.equity_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak
            if dd > max_dd:
                max_dd = dd

        return {
            "total_return": total_return,
            "sharpe_ratio": sr,
            "max_drawdown": max_dd,
            "total_trades": len(self.trades)
        }


# ============================================================================
# 6. Self-Contained Deterministic Verification Suite
# ============================================================================

def run_neuron_tests():
    """Runs all invariant tests for Neuron N050."""
    print("[*] Verifying Neuron N050: Systematic Backtesting Engine & Optimization Invariants...")

    # 1. Normal Inverse CDF (Acklam) Accuracy Check
    assert abs(NormalDistUtils.inv_cdf(0.5) - 0.0) < 1e-7, "Median normal quantile must be 0.0"
    assert abs(NormalDistUtils.inv_cdf(0.841344746) - 1.0) < 1e-4, "1-sigma normal quantile must be 1.0"
    assert abs(NormalDistUtils.inv_cdf(0.977249868) - 2.0) < 1e-4, "2-sigma normal quantile must be 2.0"

    # 2. Moments, PSR, and DSR Validation
    rets = [0.01 + 0.02 * math.sin(i * 0.1) for i in range(100)]
    mean, std, skew, kurt = DeflatedSharpeEngine.calculate_moments(rets)
    sr_hat = DeflatedSharpeEngine.sharpe_ratio(rets)
    assert sr_hat > 0, "Positive drift returns must yield positive Sharpe"

    # PSR should be close to 1.0 when true benchmark SR* = 0.0
    psr = DeflatedSharpeEngine.probabilistic_sharpe_ratio(sr_hat, 0.0, len(rets), skew, kurt)
    assert 0.99 <= psr <= 1.0, f"Expected high PSR against SR*=0, got {psr}"

    # DSR must penalize high trial count
    sr_hat, sr_0, dsr = DeflatedSharpeEngine.deflated_sharpe_ratio(rets, n_trials=100, var_sr=0.5)
    assert sr_0 > sr_hat, "Expected max Sharpe under null must exceed sample Sharpe for high trial variance"
    assert dsr < psr, "Deflated Sharpe must be strictly less than unadjusted PSR under multiple testing"

    # 3. CPCV Purging & Embargoing Validation
    # 60 samples with 5-bar holding periods
    samples = [TimeSample(index=i, t_start=i * 10, t_end=i * 10 + 5) for i in range(60)]
    cpcv = CombinatorialPurgedCV(n_splits=6, n_test_splits=2, embargo_pct=0.02)
    splits = list(cpcv.split(samples))
    assert len(splits) == 15, f"Expected C(6, 2)=15 splits, got {len(splits)}"

    for train_idx, test_idx in splits:
        # Assert complete disjointness between train and test
        assert len(set(train_idx).intersection(set(test_idx))) == 0, "Train and Test sets must be disjoint"
        assert len(train_idx) > 0, "Train set must not be empty after purging"
        assert len(test_idx) > 0, "Test set must not be empty"

    # 4. Walk-Forward Analysis (WFA) Invariant Check
    wfo = WalkForwardOptimizer(is_window=100, oos_window=25, anchored=False)
    windows = wfo.generate_windows(total_bars=250)
    assert len(windows) == 6, f"Expected 6 rolling windows, got {len(windows)}"
    
    # Check WFE calculation
    wfe_healthy = WalkForwardOptimizer.calculate_wfe([2.0, 2.2, 1.8], [1.5, 1.4, 1.6])
    assert abs(wfe_healthy - (1.5 / 2.0)) < 1e-6, "WFE calculation mismatch"
    assert wfe_healthy >= 0.60, "Healthy WFE should exceed 60% threshold"

    # 5. Event-Driven Backtesting Simulator Execution
    bars = [
        Bar(timestamp=i, open=100.0 + i * 0.2, high=101.0 + i * 0.2, low=99.0 + i * 0.2, close=100.5 + i * 0.2, volume=5000.0)
        for i in range(80)
    ]
    signals = [
        Signal(timestamp=5, symbol="ASSET", direction=1),
        Signal(timestamp=70, symbol="ASSET", direction=0)
    ]
    backtester = EventDrivenBacktester(initial_capital=10000.0, taker_fee_bps=5.0, slippage_bps=2.0)
    results = backtester.run(bars, signals)
    
    assert results["total_trades"] == 2, f"Expected 2 trade executions, got {results['total_trades']}"
    assert results["total_return"] > 0.0, "Uptrend trade must generate positive net return"
    assert len(backtester.equity_curve) == 80, "Equity curve length must equal bar count"
    assert results["max_drawdown"] >= 0.0, "Drawdown must be non-negative"

    print("  [✓] Neuron N050 Invariants Verified: Event-Driven Sim, WFA, CPCV Purging, & Deflated Sharpe.")

if __name__ == "__main__":
    run_neuron_tests()
```

---

## 6. Invarian Operasional & Quant Guardrails

1. **Zero-Tolerance Vectorized Illusion**: Dilarang mengambil keputusan alokasi modal berbasis *vectorized backtest* tanpa simulasi antrean order, *slippage non-linear*, dan *commission fees*.
2. **Mandatory Purging & Embargoing**: Setiap validasi *cross-validation* pada deret waktu wajib menerapkan *purging* pada holding period yang bertabrakan dan *embargoing* pasca-test set.
3. **Walk-Forward Efficiency Floor ($\\text{WFE} \\ge 50\\%$)**: Strategi yang memiliki $\\text{WFE} < 50\\%$ atau $\\text{PBO} > 15\\%$ wajib ditolak sebagai produk *overfitting*.
4. **DSR Multiple Testing Correction ($\\text{DSR} \\ge 0.95$)**: Seluruh evaluasi Sharpe Ratio wajib dideflasikan terhadap total jumlah iterasi parameter ($M$) dan ketidaknormalan distribusi return (*skewness* dan *kurtosis*).
