# Neuron N046: Algorithmic Execution Engines & Smart Order Routing

Prinsip arsitektur mesin eksekusi algoritmik institusional, pemodelan dampak pasar kuantitatif (*Market Impact*), dekomposisi order cerdas (*Smart Order Routing - SOR*), likuidasi optimal Almgren-Chriss, rekonstruksi likuiditas tersembunyi (*Iceberg Detection*), dan guardrail eksekusi berlatensi mikro:

- **Kategori**: Quantitative Finance, High-Frequency Trading (HFT), Algorithmic Execution, Market Microstructure
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Meminimalkan biaya transaksi institusional (*Implementation Shortfall*), mengeliminasi *adverse selection* dan *information leakage*, merutekan order lintas bursa terfragmentasi secara optimal via Smart Order Router (SOR), mengeksekusi jadwal likuidasi optimal Almgren-Chriss dengan parameter toleransi risiko ($\lambda$), mendeteksi iceberg orders pada L2/L3 orderbook, dan menyediakan mesin eksekusi TWAP/VWAP/POV deterministik berkinerja tinggi.
- **Synaptic Links**: [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N011`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N011_mechanical_sympathy_perf.md), [`N021`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N021_quantitative_gold_crypto_trading.md), [`N025`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N025_hft_orderbook_microstructure.md), [`N033`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N033_python_high_performance.md), [`N035`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N035_event_driven_streaming_cqrs.md)
- **Status**: Active Operational Invariant

---

## 1. Mathematical Taxonomy & Execution Engine Foundations

```
                    ┌─────────────────────────────────────────┐
                    │       Parent Order (Q, Side, T)         │
                    └────────────────────┬────────────────────┘
                                         │
                    ┌────────────────────▼────────────────────┐
                    │        Strategy Selector Engine         │
                    │   ┌────────┬────────┬────────┬───────┐  │
                    │   │  TWAP  │  VWAP  │  POV   │ A-C   │  │
                    │   └────┬───┴────┬───┴────┬───┴───┬───┘  │
                    └────────┼────────┼────────┼───────┼──────┘
                             │        │        │       │
                             ▼        ▼        ▼       ▼
                    ┌─────────────────────────────────────────┐
                    │    Child Order Schedule Generator (qₖ)  │
                    │      + Poisson Jitter / Randomization   │
                    └────────────────────┬────────────────────┘
                                         │
                    ┌────────────────────▼────────────────────┐
                    │      Iceberg & Hidden Liquidity Probe   │
                    └────────────────────┬────────────────────┘
                                         │
                    ┌────────────────────▼────────────────────┐
                    │     Smart Order Router (SOR Engine)     │
                    │  (Latency Penalty, Fee/Rebate, Queues)  │
                    └────┬───────────────┬───────────────┬────┘
                         │               │               │
                         ▼               ▼               ▼
                   [ Venue A (Lit) ] [ Venue B (Lit) ] [ Dark Pool ]
```

### A. Benchmark Metrics & Implementation Shortfall
1. **Implementation Shortfall (Perold 1988)**:
   Mengukur selisih total antara nilai teoritis order pada saat keputusan investasi dibuat (*Decision Price* $P_0$) dan nilai realisasi eksekusi aktual bersih setelah biaya:
   $$\text{IS} = \text{Side} \cdot \left( \sum_{i=1}^{M} q_i p_i - Q_{\text{total}} P_0 \right) + \text{Fees} + \text{Taxes}$$
   Komponen dekomposisi Implementation Shortfall:
   - **Execution Cost (Slippage)**: $\sum q_i (p_i - P_0)$
   - **Opportunity Cost (Unexecuted Shares)**: $(Q_{\text{total}} - \sum q_i) (P_T - P_0)$
   - **Fixed Costs**: Brokerage Commissions, Exchange Fees, Clearing Fees.

2. **Volume-Weighted Average Price (VWAP) Benchmark**:
   $$\text{VWAP}_{\text{market}} = \frac{\sum_{t=1}^N P_t \cdot V_t}{\sum_{t=1}^N V_t}, \quad \text{VWAP}_{\text{exec}} = \frac{\sum_{k=1}^M p_k \cdot q_k}{\sum_{k=1}^M q_k}$$
   $$\text{Slippage}_{\text{bps}} = \text{Side} \cdot \left( \frac{\text{VWAP}_{\text{exec}} - \text{VWAP}_{\text{market}}}{\text{VWAP}_{\text{market}}} \right) \times 10^4$$

3. **Time-Weighted Average Price (TWAP) Benchmark**:
   $$\text{TWAP}_{\text{market}} = \frac{1}{N} \sum_{t=1}^N P_t$$

---

## 2. Execution Strategy Architectures

### A. Time-Weighted Average Price (TWAP) with Randomized Jitter
1. **Uniform Discretization**:
   Membagi horizon waktu $T$ menjadi $N$ sub-interval $\Delta t = T / N$.
   $$q_k^{\text{base}} = \frac{Q_{\text{remaining}}}{N - k + 1}$$
2. **Anti-Adversarial Poisson Jitter**:
   Eksekusi deterministic slice waktu statis mudah dieksploitasi oleh predatory HFT momentum algorithms (*sniping & front-running*). Interval waktu dan ukuran slice dimodulasi menggunakan perturbasi stokastik:
   $$\Delta t_k = \Delta t_{\text{nominal}} \cdot (1 + \epsilon_t), \quad \epsilon_t \sim \text{Uniform}(-\delta_t, \delta_t)$$
   $$q_k = q_k^{\text{base}} \cdot (1 + \epsilon_q), \quad \epsilon_q \sim \text{Uniform}(-\delta_q, \delta_q)$$
   dengan constraint konservasi total volume $\sum_{k=1}^N q_k = Q_{\text{total}}$.

### B. Volume-Weighted Average Price (VWAP) Engine
1. **Intraday Historical Volume Profile ($w_k$)**:
   Volume pasar terdistribusi secara karakteristik *U-shaped* (tinggi saat pembukaan dan penutupan, rendah di tengah hari):
   $$w_k = \frac{\bar{V}_k}{\sum_{j=1}^N \bar{V}_j}, \quad \sum_{k=1}^N w_k = 1.0$$
2. **Dynamic Trajectory Updating & Tracking Error Minimization**:
   Target volume kumulatif pada interval $k$:
   $$Q_k^{\text{target}} = Q_{\text{total}} \cdot \sum_{j=1}^k w_j$$
   Koreksi slice adaptif saat volume pasar riil menyimpang dari ekspektasi historis:
   $$q_k = \max\left(0, Q_k^{\text{target}} - Q_{k-1}^{\text{executed}}\right) \times \left(1 + \alpha \cdot \frac{V_{\text{market}, k}^{\text{actual}} - \bar{V}_k}{\bar{V}_k}\right)$$

### C. Percentage of Volume (POV / Participation Rate)
1. **Dynamic Market Tracking**:
   Menjaga rasio partisipasi eksekusi $\rho \in (0, 0.5]$ (umumnya 10% – 20% dari volume pasar berjalan):
   $$q_k = \min\left(Q_{\text{remaining}}, \frac{\rho}{1 - \rho} \cdot V_{\text{market}, k}\right)$$
2. **Volume Surge & Illiquidity Caps**:
   - **Participation Cap**: Jika volume pasar melonjak tajam akibat berita, batasi $q_k \le q_{\max}$ untuk mencegah konsumsi likuiditas berlebihan.
   - **Timeout Flush**: Jika pasar membeku (*illiquid flatlining*), picu *urgency multiplier* saat mendekati *cutoff deadline* $T_{\text{end}}$.

---

## 3. Almgren-Chriss Optimal Liquidation Framework

```
 Trajectory x(t) (Shares Remaining)
 1.0 ┼───────┐
     │        \   Linear TWAP (λ = 0, Risk Neutral)
 0.8 │         \
     │          \──────────┐
 0.6 │           \          \
     │  Risk-Averse (λ > 0)  \
 0.4 │   Optimal Almgren-     \
     │   Chriss Trajectory     \
 0.2 │          \               \
     │           `─────────────────────┐
 0.0 ┼─────────────────────────────────┴────────► Time t
     0           T/4        T/2       3T/4      T
```

### A. Mathematical Derivation of Optimal Liquidation
Dikembangkan oleh Robert Almgren dan Neil Chriss (2000), framework ini merumuskan trade-off analitis antara **Market Impact** (biaya akibat mengeksekusi terlalu cepat) dan **Market Volatility Risk** (risiko harga bergerak melawan posisi jika mengeksekusi terlalu lambat).

1. **State Variables**:
   - $X_0$: Total order size awal pada $t = 0$.
   - $x_k$: Sisa saham pada interval $t_k$, dengan $x_0 = X_0$ dan $x_N = 0$.
   - $n_k = x_{k-1} - x_k$: Jumlah saham yang dieksekusi pada interval $[t_{k-1}, t_k]$.
   - $\tau = \Delta t = T / N$: Durasi interval waktu diskrit.
   - $v_k = n_k / \tau$: Laju penjualan per unit waktu.

2. **Price Dynamics & Impact Model**:
   - **Permanent Impact** (pergeseran harga fundamental akibat penyerapan likuiditas):
     $$S_k = S_{k-1} + \sigma \tau^{1/2} \xi_k - \tau \gamma(v_k)$$
     di mana $\xi_k \sim \mathcal{N}(0, 1)$ adalah i.i.d price shock, dan $\gamma(v) = \gamma v$ adalah fungsi linier.
   - **Temporary Impact** (diskon harga sesaat yang diderita oleh order agresif):
     $$\tilde{S}_k = S_{k-1} - \eta(v_k)$$
     di mana $\eta(v) = \eta v$ adalah parameter elastisitas likuiditas sesaat.

3. **Objective Utility Function (Mean-Variance Trade-Off)**:
   Total pendapatan eksekusi $E = \sum_{k=1}^N n_k \tilde{S}_k$.
   $$\min_{\{x_k\}} U(x) = \mathbb{E}[x] + \lambda \mathbb{V}[x]$$
   di mana $\mathbb{E}[x]$ adalah ekspektasi total biaya dampak (*Expected Shortfall*), $\mathbb{V}[x]$ adalah variansi biaya akibat volatilitas harga $\sigma$, dan $\lambda$ adalah koefisien penghindaran risiko (*Risk Aversion Parameter*):
   $$\mathbb{E}[x] = \frac{1}{2} \gamma X_0^2 + \frac{\eta}{\tau} \sum_{k=1}^N (x_{k-1} - x_k)^2$$
   $$\mathbb{V}[x] = \sigma^2 \sum_{k=1}^N \tau x_k^2$$

4. **Euler-Lagrange Closed-Form Solution**:
   Persamaan beda varians-biaya:
   $$\frac{x_{j-1} - 2x_j + x_{j+1}}{\tau^2} = \kappa^2 x_j$$
   di mana *Urgency Parameter* $\kappa$ didefinisikan sebagai:
   $$\kappa = \frac{1}{\tau} \text{arcosh}\left(1 + \frac{\lambda \sigma^2 \tau^2}{2 \eta}\right) \approx \sqrt{\frac{\lambda \sigma^2}{\eta}} \quad (\text{untuk } \tau \to 0)$$
   **Solusi Trajectory Optimal $x(t_j)$**:
   $$x_j = \frac{\sinh(\kappa (T - t_j))}{\sinh(\kappa T)} X_0$$
   - **Half-Life of Liquidation**: $t_{1/2} = \frac{\ln 2}{\kappa}$.
   - Kasus Batas $\lambda \to 0$ (Risk-Neutral): $x_j = \left(1 - \frac{t_j}{T}\right) X_0$ (Identik dengan TWAP linier murni).
   - Kasus Batas $\lambda \to \infty$ (Extreme Risk-Averse): $\kappa \to \infty \implies$ Immediate market dump pada $t = 0$.

---

## 4. Iceberg Order Detection & L3 Hidden Liquidity Reconstruction

```
  Visible L2 Book Layer              Hidden Reserve (Iceberg Core)
 ┌──────────────────────┐           ┌─────────────────────────────┐
 │ Displayed: 500 lots  │ ◄─ Reload ┤ Remaining Hidden: 4500 lots │
 └──────────┬───────────┘           └─────────────────────────────┘
            │ Fill 500
            ▼
 ┌──────────────────────┐
 │ Displayed: 500 lots  │ (Instant Queue Reset at identical price!)
 └──────────────────────┘
```

### A. Iceberg Mechanism
Order institusional besar memecah instruksi menjadi:
- $V_{\text{visible}}$ (Peak Size): Volume yang ditampilkan di buku order publik (L2).
- $V_{\text{hidden}}$: Volume cadangan yang disembunyikan di matching engine bursa.
- Saat $V_{\text{visible}}$ terisi penuh, engine bursa secara otomatis menerbitkan order limit baru sebesar $V_{\text{visible}}$ pada harga yang sama, tetapi diletakkan di **antrean prioritas waktu paling belakang** (*FIFO time priority reset*).

### B. Algoritma Deteksi & Estimasi Hidden Size
1. **Trade Print vs Book Depth Invariant**:
   Jika dalam jendela waktu $\Delta t_{\text{threshold}}$, volume transaksi akumulasi pada tingkat harga $P^*$ melebihi volume yang ditampilkan $V_{\text{displayed}}(P^*)$ tanpa pergeseran harga (*price displacement*):
   $$\sum_{i=1}^m \text{TradeSize}_i(P^*) > V_{\text{displayed}}(P^*) \implies \text{Iceberg Detected}$$
2. **Reload Signature Timing**:
   Kemunculan kembali volume pada $P^*$ dalam rentang latency deterministic $\delta t_{\text{reload}} \in [0.1\text{ms}, 5.0\text{ms}]$ setelah depth habis.
3. **Hidden Size Estimation (Maximum Likelihood / Run-Length)**:
   $$\hat{V}_{\text{hidden}} = (K_{\text{reloads}} + \hat{\theta}_{\text{prior}}) \times V_{\text{peak}} - V_{\text{executed}}$$

---

## 5. Smart Order Routing (SOR) Engine & Cross-Venue Sweeper

### A. Consolidated Order Book (COB) Reconstruction
Merekonsiliasi orderbook lintas $V$ bursa terpisah (misal Binance, Coinbase, Bybit, Kraken, atau LSE, Chi-X, BATS, Turquoise):
$$\text{COB}_{\text{Ask}} = \text{MergeSort}\left(\bigcup_{v \in \mathcal{V}} \mathcal{O}_{\text{Ask}}^{(v)}\right), \quad \text{COB}_{\text{Bid}} = \text{MergeSort}\left(\bigcup_{v \in \mathcal{V}} \mathcal{O}_{\text{Bid}}^{(v)}\right)$$

### B. Routing Cost Objective Function
Untuk mengeksekusi child slice $q$ pada bursa $v$, total biaya efektif per unit adalah:
$$\mathcal{C}_v(p, q) = p \cdot q \cdot (1 + \text{Fee}_v - \text{Rebate}_v) + \text{SlippageImpact}_v(q) + \mathcal{P}_{\text{latency}}(L_v)$$
di mana:
- $\text{Fee}_v$: Biaya Taker Fee bursa $v$.
- $\text{Rebate}_v$: Maker Rebate jika menggunakan post-only limit routing.
- $\mathcal{P}_{\text{latency}}(L_v) = \beta \cdot L_v \cdot \sigma_{\text{mid}}$: Penalti risiko harga bergeser (*adverse selection risk*) selama transit order melintasi jaringan dengan latency one-way $L_v$.

### C. Optimal Multi-Venue Sweep Allocation (Lagrangian Knapsack Solver)
Untuk total order $Q$, alokasikan $q_v^*$ pada setiap venue $v \in \mathcal{V}$ sehingga:
$$\min_{\{q_v\}} \sum_{v \in \mathcal{V}} \int_0^{q_v} P_v(s) \, ds + \sum_{v \in \mathcal{V}} \text{Cost}_v(q_v) \quad \text{s.t.} \quad \sum_{v \in \mathcal{V}} q_v = Q, \quad 0 \le q_v \le \text{Depth}_v$$

---

## 6. Comprehensive Stdlib Implementation & Deterministic Verification

Berikut implementasi lengkap mesin eksekusi algoritmik dan Smart Order Router berbasis Python Standard Library:

```python
"""
Neuron N046: Algorithmic Execution Engines & Smart Order Routing (SOR)
Pure Python Standard Library (Zero External Dependencies).
Deterministic verification covering TWAP, VWAP, POV, Almgren-Chriss, Iceberg Detection, and SOR.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable
import math
import random
import time

# ============================================================================
# 1. DATA STRUCTURES & MARKET SIMULATION PRIMITIVES
# ============================================================================

@dataclass
class TradePrint:
    timestamp: float
    price: float
    size: float
    side: str  # "buy" or "sell"

@dataclass
class OrderLevel:
    price: float
    size: float

@dataclass
class OrderBookSnapshot:
    venue_id: str
    bids: List[OrderLevel]  # sorted descending
    asks: List[OrderLevel]  # sorted ascending
    timestamp: float
    fee_bps: float = 5.0      # Taker fee in bps (5 bps = 0.05%)
    rebate_bps: float = 1.0   # Maker rebate in bps
    latency_ms: float = 2.0   # Network round-trip latency in ms

@dataclass
class Fill:
    venue_id: str
    price: float
    size: float
    fee_cost: float
    slippage_bps: float
    timestamp: float

# ============================================================================
# 2. ALMGREN-CHRISS OPTIMAL LIQUIDATION ENGINE
# ============================================================================

class AlmgrenChrissEngine:
    """
    Optimal execution trajectory solver based on Almgren & Chriss (2000).
    Minimizes E[x] + lambda * V[x] under linear market impact and volatility risk.
    """
    def __init__(
        self,
        total_shares: float,
        total_time_seconds: float,
        num_intervals: int,
        volatility: float,          # sigma: annual/intraday price volatility
        temporary_impact: float,    # eta: temporary impact parameter
        permanent_impact: float,    # gamma: permanent impact parameter
        risk_aversion: float        # lambda: risk aversion coefficient
    ):
        if total_shares <= 0 or total_time_seconds <= 0 or num_intervals <= 0:
            raise ValueError("Parameters must be strictly positive")
        self.X0 = total_shares
        self.T = total_time_seconds
        self.N = num_intervals
        self.tau = self.T / self.N
        self.sigma = volatility
        self.eta = max(1e-9, temporary_impact)
        self.gamma = max(1e-9, permanent_impact)
        self.lam = max(0.0, risk_aversion)

    def calculate_kappa(self) -> float:
        """Calculates urgency parameter kappa."""
        if self.lam <= 1e-12:
            return 0.0  # Risk-neutral case (pure TWAP limit)
        val = 1.0 + (self.lam * (self.sigma ** 2) * (self.tau ** 2)) / (2.0 * self.eta)
        return (1.0 / self.tau) * math.acosh(val)

    def compute_holdings_trajectory(self) -> List[float]:
        """
        Computes remaining shares x_j for j = 0, 1, ..., N.
        x_j = sinh(kappa * (T - t_j)) / sinh(kappa * T) * X0
        """
        kappa = self.calculate_kappa()
        trajectory = []

        if kappa <= 1e-9:
            # Linear TWAP trajectory when risk aversion is zero
            for j in range(self.N + 1):
                t_j = j * self.tau
                x_j = self.X0 * (1.0 - (t_j / self.T))
                trajectory.append(max(0.0, x_j))
        else:
            sinh_k_T = math.sinh(kappa * self.T)
            for j in range(self.N + 1):
                t_j = j * self.tau
                sinh_k_remain = math.sinh(kappa * (self.T - t_j))
                x_j = self.X0 * (sinh_k_remain / sinh_k_T)
                trajectory.append(max(0.0, x_j))

        # Enforce boundary conditions
        trajectory[0] = self.X0
        trajectory[-1] = 0.0
        return trajectory

    def compute_trade_schedule(self) -> List[float]:
        """Computes slice sizes n_k = x_{k-1} - x_k for k = 1, ..., N."""
        holdings = self.compute_holdings_trajectory()
        trades = []
        for k in range(1, len(holdings)):
            n_k = holdings[k - 1] - holdings[k]
            trades.append(max(0.0, n_k))
        return trades

    def compute_expected_cost_and_variance(self) -> Tuple[float, float]:
        """Calculates theoretical Expected Cost E[x] and Variance V[x]."""
        trades = self.compute_trade_schedule()
        holdings = self.compute_holdings_trajectory()

        # E[x] = 0.5 * gamma * X0^2 + (eta / tau) * sum(n_k^2)
        expected_cost = 0.5 * self.gamma * (self.X0 ** 2)
        expected_cost += (self.eta / self.tau) * sum(n_k ** 2 for n_k in trades)

        # V[x] = sigma^2 * tau * sum(x_k^2)
        variance = (self.sigma ** 2) * self.tau * sum(x_k ** 2 for x_k in holdings[1:])
        return expected_cost, variance

# ============================================================================
# 3. TWAP EXECUTION ENGINE WITH POISSON JITTER
# ============================================================================

class TWAPEngine:
    """
    Time-Weighted Average Price execution engine with anti-gaming jitter.
    """
    def __init__(
        self,
        total_quantity: float,
        duration_seconds: float,
        num_slices: int,
        jitter_pct: float = 0.2,
        seed: Optional[int] = 42
    ):
        self.total_quantity = total_quantity
        self.duration_seconds = duration_seconds
        self.num_slices = num_slices
        self.jitter_pct = min(0.5, max(0.0, jitter_pct))
        self.rng = random.Random(seed)
        self.executed_quantity = 0.0

    def generate_schedule(self) -> List[Tuple[float, float]]:
        """
        Generates list of (target_timestamp_offset, slice_size).
        Ensures exact sum(slice_sizes) == total_quantity.
        """
        base_interval = self.duration_seconds / self.num_slices
        base_slice = self.total_quantity / self.num_slices

        schedule = []
        current_time = 0.0
        raw_slices = []

        for _ in range(self.num_slices):
            time_jitter = 1.0 + self.rng.uniform(-self.jitter_pct, self.jitter_pct)
            size_jitter = 1.0 + self.rng.uniform(-self.jitter_pct, self.jitter_pct)

            interval = base_interval * time_jitter
            current_time += interval
            raw_slices.append((current_time, base_slice * size_jitter))

        # Normalize slice sizes to sum exactly to total_quantity
        sum_raw = sum(s for _, s in raw_slices)
        normalized = []
        for t, s in raw_slices:
            norm_size = (s / sum_raw) * self.total_quantity
            normalized.append((t, norm_size))

        return normalized

# ============================================================================
# 4. VWAP EXECUTION ENGINE WITH ADAPTIVE VOLUME PROFILE
# ============================================================================

class VWAPEngine:
    """
    Volume-Weighted Average Price engine tracking historical U-shaped profile
    with dynamic volume tracking corrections.
    """
    def __init__(
        self,
        total_quantity: float,
        historical_volume_weights: List[float]
    ):
        total_weight = sum(historical_volume_weights)
        if total_weight <= 0:
            raise ValueError("Volume weights must sum to a positive number")
        self.total_quantity = total_quantity
        # Normalize weights
        self.weights = [w / total_weight for w in historical_volume_weights]
        self.num_bins = len(self.weights)
        self.cumulative_weights = []
        c = 0.0
        for w in self.weights:
            c += w
            self.cumulative_weights.append(c)

    def get_target_for_bin(
        self,
        bin_idx: int,
        already_executed: float,
        actual_volume_ratio: float = 1.0
    ) -> float:
        """
        Calculates optimal slice for bin_idx based on remaining deficit and volume surge.
        """
        if bin_idx < 0 or bin_idx >= self.num_bins:
            raise IndexError("Bin index out of range")

        expected_prev = self.total_quantity * (self.cumulative_weights[bin_idx - 1] if bin_idx > 0 else 0.0)
        deficit = expected_prev - already_executed
        base_slice = self.total_quantity * self.weights[bin_idx]

        # Dynamically scale slice if real-time market volume is higher/lower than expected
        adjusted_slice = (base_slice + 0.5 * deficit) * actual_volume_ratio
        return max(0.0, min(self.total_quantity - already_executed, adjusted_slice))

# ============================================================================
# 5. PERCENTAGE OF VOLUME (POV) ENGINE
# ============================================================================

class POVEngine:
    """
    Participation Rate / Percentage of Volume execution engine.
    Ensures execution stays within target participation bounds rho of market tape.
    """
    def __init__(
        self,
        total_quantity: float,
        target_participation_rate: float = 0.15,
        max_participation_cap: float = 0.30
    ):
        if not (0.0 < target_participation_rate <= max_participation_cap < 1.0):
            raise ValueError("Invalid participation rate constraints")
        self.total_quantity = total_quantity
        self.rho = target_participation_rate
        self.rho_max = max_participation_cap
        self.executed_quantity = 0.0

    def compute_slice(self, market_volume_interval: float) -> float:
        """
        Calculates child order size for an observed market volume interval.
        q = min(remaining, (rho / (1 - rho)) * market_vol)
        """
        remaining = self.total_quantity - self.executed_quantity
        if remaining <= 0 or market_volume_interval <= 0:
            return 0.0

        # Sizing formula ensuring order is exactly rho% of (market_volume + our_order)
        target_slice = (self.rho / (1.0 - self.rho)) * market_volume_interval
        max_slice = (self.rho_max / (1.0 - self.rho_max)) * market_volume_interval

        effective_slice = min(remaining, min(target_slice, max_slice))
        self.executed_quantity += effective_slice
        return effective_slice

# ============================================================================
# 6. ICEBERG ORDER DETECTOR (L2/L3 HIDDEN LIQUIDITY PROBE)
# ============================================================================

class IcebergDetector:
    """
    Detects iceberg hidden liquidity by correlating trade tape prints
    with displayed order book depth refills at static price levels.
    """
    def __init__(self, refill_time_window_ms: float = 50.0):
        self.window_ms = refill_time_window_ms
        # Track level state: price -> dict(visible_size, cumulative_traded, last_refill_ts, reload_count)
        self.level_state: Dict[float, Dict] = {}

    def on_book_update(self, side: str, price: float, visible_size: float, timestamp_ms: float):
        """Called on L2 book depth update."""
        if price not in self.level_state:
            self.level_state[price] = {
                "visible_size": visible_size,
                "cumulative_traded": 0.0,
                "last_refill_ts": timestamp_ms,
                "reload_count": 0,
                "initial_peak": visible_size,
                "side": side
            }
        else:
            state = self.level_state[price]
            # Check if depth was replenished after being depleted by trades
            if visible_size > state["visible_size"] and state["cumulative_traded"] > 0:
                time_delta = timestamp_ms - state["last_refill_ts"]
                if time_delta <= self.window_ms:
                    state["reload_count"] += 1
            state["visible_size"] = visible_size
            state["last_refill_ts"] = timestamp_ms

    def on_trade(self, price: float, trade_size: float, timestamp_ms: float) -> Optional[Dict]:
        """
        Called on public trade tape execution.
        Returns detection report if an iceberg order invariant is triggered.
        """
        if price not in self.level_state:
            return None

        state = self.level_state[price]
        state["cumulative_traded"] += trade_size
        state["visible_size"] = max(0.0, state["visible_size"] - trade_size)

        # Invariant: If cumulative traded volume on this price level exceeds initial visible peak
        # while depth remains available, an iceberg order is active.
        if state["cumulative_traded"] > state["initial_peak"] and state["reload_count"] >= 1:
            estimated_hidden = (state["reload_count"] + 1) * state["initial_peak"] - state["cumulative_traded"]
            return {
                "price": price,
                "side": state["side"],
                "reload_count": state["reload_count"],
                "cumulative_traded": state["cumulative_traded"],
                "peak_size": state["initial_peak"],
                "estimated_hidden_remaining": max(0.0, estimated_hidden),
                "is_iceberg": True
            }
        return None

# ============================================================================
# 7. SMART ORDER ROUTER (SOR) ENGINE
# ============================================================================

class SmartOrderRouter:
    """
    Multi-venue Smart Order Router (SOR) with Consolidated Order Book (COB)
    sweeping, latency-adjusted pricing, and maker/taker fee optimization.
    """
    def __init__(self, venues: List[OrderBookSnapshot]):
        self.venues = {v.venue_id: v for v in venues}

    def compute_effective_cost(
        self,
        venue: OrderBookSnapshot,
        price: float,
        size: float,
        side: str
    ) -> float:
        """
        Computes effective execution price including taker fee and latency penalty.
        Effective Ask = Price * (1 + fee_bps/10000) + (latency_ms * 0.0001)
        Effective Bid = Price * (1 - fee_bps/10000) - (latency_ms * 0.0001)
        """
        fee_multiplier = 1.0 + (venue.fee_bps / 10000.0) if side == "buy" else 1.0 - (venue.fee_bps / 10000.0)
        latency_penalty = venue.latency_ms * 0.001  # small penalty per ms of latency

        if side == "buy":
            return (price * fee_multiplier) + latency_penalty
        else:
            return (price * fee_multiplier) - latency_penalty

    def route_market_sweep(self, side: str, total_quantity: float) -> List[Fill]:
        """
        Sweeps the Consolidated Order Book across all venues to achieve optimal VWEP.
        """
        fills: List[Fill] = []
        remaining_qty = total_quantity

        # Flatten and score all available orderbook levels across all venues
        candidates: List[Tuple[float, float, str, OrderLevel]] = []

        for v_id, v in self.venues.items():
            book = v.asks if side == "buy" else v.bids
            for level in book:
                eff_cost = self.compute_effective_cost(v, level.price, level.size, side)
                candidates.append((eff_cost, level.price, v_id, level))

        # Sort candidates:
        # If buying: lowest effective cost first
        # If selling: highest effective cost first
        candidates.sort(key=lambda x: x[0], reverse=(side == "sell"))

        for eff_cost, nominal_price, v_id, level in candidates:
            if remaining_qty <= 0:
                break

            fill_size = min(remaining_qty, level.size)
            venue = self.venues[v_id]
            fee_cost = fill_size * nominal_price * (venue.fee_bps / 10000.0)

            # Record fill
            fills.append(Fill(
                venue_id=v_id,
                price=nominal_price,
                size=fill_size,
                fee_cost=fee_cost,
                slippage_bps=abs(eff_cost - nominal_price) / nominal_price * 10000.0,
                timestamp=time.time()
            ))

            remaining_qty -= fill_size

        return fills

# ============================================================================
# 8. PURE STDLIB RUNNABLE VERIFICATION SUITE
# ============================================================================

def test_almgren_chriss_trajectory_invariants():
    """Validates Almgren-Chriss mathematical invariants."""
    total_shares = 100000.0
    total_time = 60.0
    num_intervals = 10

    # 1. Test Risk-Neutral (lambda = 0) -> Must converge to uniform linear TWAP
    ac_neutral = AlmgrenChrissEngine(
        total_shares=total_shares,
        total_time_seconds=total_time,
        num_intervals=num_intervals,
        volatility=0.30,
        temporary_impact=0.05,
        permanent_impact=0.01,
        risk_aversion=0.0
    )
    holdings_neutral = ac_neutral.compute_holdings_trajectory()
    trades_neutral = ac_neutral.compute_trade_schedule()

    assert len(holdings_neutral) == num_intervals + 1, "Holdings must have N+1 points"
    assert math.isclose(holdings_neutral[0], total_shares, rel_tol=1e-5), "Initial holding must be X0"
    assert math.isclose(holdings_neutral[-1], 0.0, abs_tol=1e-5), "Final holding must be 0"

    # In risk-neutral case, every slice must be identical (10000 shares each)
    expected_slice = total_shares / num_intervals
    for trade in trades_neutral:
        assert math.isclose(trade, expected_slice, rel_tol=1e-4), f"Risk-neutral trade {trade} != {expected_slice}"

    # 2. Test High Risk-Aversion (lambda > 0) -> Front-loaded decay trajectory
    ac_averse = AlmgrenChrissEngine(
        total_shares=total_shares,
        total_time_seconds=total_time,
        num_intervals=num_intervals,
        volatility=0.30,
        temporary_impact=0.05,
        permanent_impact=0.01,
        risk_aversion=1e-4
    )
    holdings_averse = ac_averse.compute_holdings_trajectory()
    trades_averse = ac_averse.compute_trade_schedule()

    # Front-loaded invariant: First trade must be strictly larger than last trade
    assert trades_averse[0] > trades_averse[-1], "Risk-averse liquidation must be strictly front-loaded"
    assert sum(trades_averse) <= total_shares + 1e-4, "Sum of trades must conserve total quantity"

    # Variance invariant: Risk-averse schedule must have strictly lower price variance than TWAP
    cost_n, var_n = ac_neutral.compute_expected_cost_and_variance()
    cost_a, var_a = ac_averse.compute_expected_cost_and_variance()
    assert var_a < var_n, f"Risk averse variance {var_a} must be strictly lower than neutral variance {var_n}"
    assert cost_a > cost_n, f"Risk averse expected impact {cost_a} must be higher due to aggressive front-loading"

def test_twap_and_vwap_engine_invariants():
    """Validates TWAP jitter bounds and VWAP profile tracking."""
    total_qty = 50000.0
    twap = TWAPEngine(total_quantity=total_qty, duration_seconds=100.0, num_slices=5, jitter_pct=0.15, seed=123)
    schedule = twap.generate_schedule()

    assert len(schedule) == 5, "TWAP must produce exact slice count"
    total_scheduled = sum(size for _, size in schedule)
    assert math.isclose(total_scheduled, total_qty, rel_tol=1e-6), "TWAP must conserve exact total shares"

    # VWAP U-shape profile test
    u_shape_weights = [0.30, 0.15, 0.10, 0.15, 0.30]  # Classic U-shape
    vwap = VWAPEngine(total_quantity=total_qty, historical_volume_weights=u_shape_weights)

    # Bin 0 target must be 30% of total
    slice_0 = vwap.get_target_for_bin(0, already_executed=0.0)
    assert math.isclose(slice_0, 15000.0, rel_tol=1e-5), "Bin 0 slice must match 30% of total"

    # Midday Bin 2 target must be 10%
    slice_2 = vwap.get_target_for_bin(2, already_executed=22500.0)
    assert math.isclose(slice_2, 5000.0, rel_tol=1e-5), "Bin 2 slice must match 10% of total"

def test_pov_and_iceberg_invariants():
    """Validates POV rate limits and Iceberg hidden liquidity detection."""
    # 1. POV Engine
    pov = POVEngine(total_quantity=10000.0, target_participation_rate=0.20, max_participation_cap=0.35)
    # Market trades 1000 shares -> our share should be (0.2 / 0.8) * 1000 = 250 shares
    # So our order (250) is 250 / (1000 + 250) = 20%
    s1 = pov.compute_slice(1000.0)
    assert math.isclose(s1, 250.0, rel_tol=1e-5), f"POV slice {s1} != 250.0"
    assert pov.executed_quantity == 250.0

    # 2. Iceberg Detector
    detector = IcebergDetector(refill_time_window_ms=100.0)
    price = 2500.0
    # Step A: Visible book shows 500 lots
    detector.on_book_update("buy", price=price, visible_size=500.0, timestamp_ms=1000.0)

    # Step B: 500 lots traded
    rep1 = detector.on_trade(price=price, trade_size=500.0, timestamp_ms=1010.0)
    assert rep1 is None, "Should not trigger iceberg before reload"

    # Step C: Book reloads 500 lots at same price 15ms later
    detector.on_book_update("buy", price=price, visible_size=500.0, timestamp_ms=1025.0)

    # Step D: Another trade print arrives (cumulative traded = 700 > peak 500)
    rep2 = detector.on_trade(price=price, trade_size=200.0, timestamp_ms=1030.0)
    assert rep2 is not None, "Iceberg must be detected upon reload and trade excess"
    assert rep2["is_iceberg"] is True
    assert rep2["reload_count"] == 1
    assert rep2["cumulative_traded"] == 700.0

def test_smart_order_router_sweep_invariants():
    """Validates SOR cross-venue Consolidated Order Book routing and fee optimization."""
    # Venue A: Price 100.00, Size 100, Fee 10 bps, Latency 1ms
    # Venue B: Price 100.02, Size 200, Fee 1 bps,  Latency 10ms
    # Venue C: Price 99.98,  Size 50,  Fee 2 bps,  Latency 1ms (Cheapest Ask)
    v_a = OrderBookSnapshot("VENUE_A", bids=[], asks=[OrderLevel(100.00, 100.0)], timestamp=0.0, fee_bps=10.0, latency_ms=1.0)
    v_b = OrderBookSnapshot("VENUE_B", bids=[], asks=[OrderLevel(100.02, 200.0)], timestamp=0.0, fee_bps=1.0,  latency_ms=10.0)
    v_c = OrderBookSnapshot("VENUE_C", bids=[], asks=[OrderLevel(99.98, 50.0)],   timestamp=0.0, fee_bps=2.0,  latency_ms=1.0)

    sor = SmartOrderRouter([v_a, v_b, v_c])

    # Sweep 120 shares on buy side
    fills = sor.route_market_sweep(side="buy", total_quantity=120.0)

    assert len(fills) >= 2, "Must route across multiple venues"
    # First fill must come from VENUE_C (cheapest price 99.98)
    assert fills[0].venue_id == "VENUE_C", "First fill must sweep lowest effective ask"
    assert fills[0].size == 50.0

    # Second fill must sweep VENUE_B because low fee (1 bps) beats VENUE_A (10 bps) on net effective cost
    assert fills[1].venue_id == "VENUE_B", "SOR must choose VENUE_B over VENUE_A due to net fee advantage"
    assert fills[1].size == 70.0

    total_filled = sum(f.size for f in fills)
    assert math.isclose(total_filled, 120.0, rel_tol=1e-6), "Total filled must equal requested sweep"

def run_all_execution_engine_tests():
    """Runs complete test suite and verifies all invariants."""
    test_almgren_chriss_trajectory_invariants()
    test_twap_and_vwap_engine_invariants()
    test_pov_and_iceberg_invariants()
    test_smart_order_router_sweep_invariants()
    return "All N046 Algorithmic Execution & SOR Invariants Successfully Passed."

if __name__ == "__main__":
    result = run_all_execution_engine_tests()
    print(f"[OK] {result}")
```

---

## 7. Execution Invariants & Operational Rules

1. **Conservation of Volume Invariant**:
   $$\sum_{k=1}^N q_k + Q_{\text{unexecuted}} \equiv Q_{\text{parent}}$$
   Tidak boleh ada child order yang diterbitkan yang menyebabkan *overfill* melampaui ukuran parent order.

2. **Adverse Selection & Latency Cap Rule**:
   Rute SOR wajib menyertakan latency penalty $\mathcal{P}(L_v)$. Jangan merutekan ke bursa berlatensi tinggi jika potensi pergeseran harga (*market drift*) melampaui selisih spread/fee.

3. **Almgren-Chriss Boundary Guarantee**:
   Trajectory likuidasi $x(t)$ wajib memenuhi $x(0) = X_0$ dan $x(T) = 0$. Untuk parameter $\lambda > 0$, laju likuidasi $v(t)$ bersifat monotonik turun (*strictly decelerating*).

4. **Iceberg Anti-Adverse Sweep Invariant**:
   Saat probe mendeteksi iceberg order aktif pada level limit harga $P^*$, SOR dilarang memicu aggressive market sweep penuh yang membongkar hidden reserve secara instan tanpa memperhitungkan slippage dampak sekunder.
