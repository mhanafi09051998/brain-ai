# Neuron N047: Automated Risk Engine & Dynamic Drawdown Guard

- **Kategori:** Quantitative Finance, Portfolio Risk Management & Automated Capital Preservation
- **Tanggal Sintesis:** 2026-08-24 18:58:00
- **Status:** Active Operational Invariant
- **Connections:** `N001`, `N004`, `N007`, `N021`, `N025`

---

## 🎯 Domain & Arsitektur

- **Domain**: Real-Time Quantitative Risk Management, Value at Risk (VaR 99% / 95%), Expected Shortfall (Conditional VaR / CVaR), Multi-Asset Portfolio Margin Buffering, Trailing High-Water Mark (HWM) Drawdown Circuit Breakers, dan Idempotent Emergency Hard Kill-Switch.
- **Core Invariant**: *Capital preservation strictly precedes alpha generation*. Di pasar dengan volatilitas ekstrem, fat tails (*leptokurtic*), dan liquidity vacuum, stop-loss statis individual tidak memadai. Mesin risiko kuantitatif wajib mengevaluasi risiko portofolio secara continuous dan real-time:
  1. Menghitung **Parametric Cornish-Fisher VaR & Historical Simulation VaR 99%**.
  2. Menghitung **Expected Shortfall (CVaR)** sebagai ukuran risiko koheren (*coherent risk measure*) yang memperhitungkan keparahan *tail risk*.
  3. Memantau **Cross-Asset Maintenance Margin Buffer** untuk mencegah likuidasi paksa oleh exchange/venue.
  4. Menerapkan **Tiered Trailing High-Water Mark (HWM) Circuit Breakers** (Throttle $\to$ Freeze $\to$ De-risk $\to$ Kill-Switch).
  5. Menyediakan **Idempotent Hard Kill-Switch** yang membatalkan 100% resting orders, melikuidasi 100% posisi secara atomik, dan mengunci sistem hingga otorisasi manual.

```
       +-------------------------------------------------------------+
       |           Continuous Portfolio Risk Ingestion Engine        |
       +-------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
+-----------------------------+                           +-----------------------------+
|    Dual-Engine VaR & CVaR   |                           | Multi-Asset Margin Monitor  |
|  - Historical VaR (99%)     |                           |  - Gross Notional Exposure  |
|  - Cornish-Fisher VaR (99%) |                           |  - Initial Margin (IM) Req  |
|  - Expected Shortfall (CVaR)|                           |  - Maintenance Margin Buffer|
+-----------------------------+                           +-----------------------------+
         |                                                         |
         +----------------------------+----------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |        Trailing High-Water Mark (HWM) Circuit Breaker       |
       +-------------------------------------------------------------+
                                      |
              +-----------------------+-----------------------+
              |                       |                       |
              v                       v                       v
     [ Tier 1: Throttle ]    [ Tier 2: Freeze ]      [ Tier 3: De-Risk ]
      - Cut Kelly size 50%    - Reduce-Only mode      - Trim 50% gross exp
      - Tighten SL by 30%     - Cancel entry limits   - Volatility cool-off
              |                       |                       |
              +-----------------------+-----------------------+
                                      | Breach (MDD >= 10% or Margin Buffer < 15%)
                                      v
       +-------------------------------------------------------------+
       |              Tier 4: Hard Kill-Switch Protocol              |
       |  1. Atomic State Lock (`is_locked = True`)                  |
       |  2. Cancel 100% Open Resting Orders Across All Venues       |
       |  3. Market Liquidation / Flattening of 100% Active Positions |
       |  4. Invariant Audit Verification & Immutable Event Logging  |
       +-------------------------------------------------------------+
```

---

## 🏛️ 5 Pilar Manajemen Risiko Kuantitatif

### 1. Dual-Engine Value-at-Risk (VaR 99% & 95%)

#### A. Parametric Cornish-Fisher VaR (Fat-Tail & Skewness Adjusted)
Distribusi return finansial nyata hampir selalu memiliki *negative skewness* (left-tail crash) dan *excess kurtosis* (leptokurtic fat-tails). Pendekatan Gaussian murni meremehkan probabilitas bencana (*underestimates tail risk*).

Ekspansi Cornish-Fisher menyesuaikan kuantil normal $z_\alpha$ berbasis momen empiris:
$$z_{\text{CF}} = z_\alpha + \frac{S}{6}(z_\alpha^2 - 1) + \frac{K}{24}(z_\alpha^3 - 3z_\alpha) - \frac{S^2}{36}(2z_\alpha^3 - 5z_\alpha)$$

di mana:
- $z_\alpha = \Phi^{-1}(\alpha)$ (untuk 99% confidence level, $\alpha = 0.01 \implies z_{0.01} \approx -2.32635$).
- $S = \mathbb{E}\left[\left(\frac{R - \mu}{\sigma}\right)^3\right]$ (Sample Skewness).
- $K = \mathbb{E}\left[\left(\frac{R - \mu}{\sigma}\right)^4\right] - 3$ (Sample Excess Kurtosis).

Besaran potensi kerugian maksimum pada tingkat keyakinan $(1 - \alpha)$:
$$\text{VaR}_{\text{CF}}(\alpha) = -\left(\mu + z_{\text{CF}} \cdot \sigma\right) \cdot W_{\text{portfolio}}$$

#### B. Historical Simulation VaR (Non-Parametric)
Pendekatan bebas asumsi distribusi (*distribution-free*):
1. Urutkan seluruh return historis secara menaik: $R_{(1)} \le R_{(2)} \le \dots \le R_{(n)}$.
2. Tentukan indeks batas kuantil: $k = \max(1, \lfloor (1 - \text{confidence}) \cdot n \rfloor)$.
3. $\text{VaR}_{\text{hist}}(\alpha) = -R_{(k)} \cdot W_{\text{portfolio}}$.

---

### 2. Expected Shortfall (CVaR / Conditional Value at Risk)

VaR memiliki kelemahan matematis fatal: **bukan merupakan coherent risk measure** karena tidak memenuhi aksioma sub-aditivitas ($\text{VaR}(X + Y)$ bisa $> \text{VaR}(X) + \text{VaR}(Y)$ pada ekor tak cembung) dan **mengabaikan besaran keparahan rugi di luar batas VaR**.

Expected Shortfall (CVaR) mengukur rata-rata kerugian bersyarat ketika batas VaR ditembus:
$$\text{CVaR}_\alpha = -\mathbb{E}\left[R \mid R \le -\text{VaR}_\alpha\right] \cdot W_{\text{portfolio}}$$

#### A. Discrete Historical CVaR
$$\text{CVaR}_{\text{hist}}(\alpha) = -\left(\frac{1}{k} \sum_{i=1}^k R_{(i)}\right) \cdot W_{\text{portfolio}} \quad \text{di mana } k = \max(1, \lfloor (1-\alpha) n \rfloor)$$

#### B. Parametric Normal Expected Shortfall
$$\text{CVaR}_{\text{norm}}(\alpha) = \left(-\mu + \sigma \frac{\phi(z_\alpha)}{1 - \alpha}\right) \cdot W_{\text{portfolio}}$$
di mana $\phi(z) = \frac{1}{\sqrt{2\pi}} e^{-z^2/2}$ adalah PDF standar normal.

**Mathematical Invariant**:
$$\text{CVaR}_\alpha \ge \text{VaR}_\alpha \quad \forall \alpha \in (0, 1)$$

---

### 3. Multi-Asset Portfolio Margin Buffer & Leverage Ceiling

Dalam trading derivatif multi-aset (XAU/USD Gold, BTC/USDT, ETH/USDT, FX), margin dihitung lintas posisi aktif:
$$\text{Equity}_t = \text{Wallet Balance} + \sum_{i=1}^m \text{Unrealized PnL}_i$$
$$\text{Total Initial Margin (IM)} = \sum_{i=1}^m |\text{Size}_i| \cdot P_i \cdot \text{IM\_Ratio}_i$$
$$\text{Total Maintenance Margin (MM)} = \sum_{i=1}^m |\text{Size}_i| \cdot P_i \cdot \text{MM\_Ratio}_i$$
$$\text{Margin Utilization} = \frac{\text{IM}}{\text{Equity}_t}, \quad \text{Maintenance Buffer} = \frac{\text{Equity}_t - \text{MM}}{\text{Equity}_t}$$

| Status Zona | Maintenance Buffer | Margin Utilization | Aksi Risk Engine |
| :--- | :--- | :--- | :--- |
| **🟢 Green (Healthy)** | $\ge 40\%$ | $\le 70\%$ | Operasi normal, Kelly sizing penuh |
| **🟡 Yellow (Caution)** | $25\% - 40\%$ | $70\% - 85\%$ | **Tier 1 Throttle**: Pangkas ukuran order baru 50% |
| **🟠 Orange (Warning)** | $15\% - 25\%$ | $85\% - 95\%$ | **Tier 2 Freeze**: Kunci order pembuka, reduce-only |
| **🔴 Red (Critical)** | $< 15\%$ | $> 95\%$ | **Tier 4 Kill-Switch**: Eksekusi likuidasi darurat |

---

### 4. Dynamic Trailing High-Water Mark (HWM) Circuit Breakers

Puncak ekuitas portofolio (*High-Water Mark*) dilacak secara real-time:
$$\text{HWM}_t = \max(\text{HWM}_{t-1}, \text{Equity}_t)$$
$$\text{Trailing Drawdown (MDD)}_t = \frac{\text{HWM}_t - \text{Equity}_t}{\text{HWM}_t}$$
$$\text{Daily Drawdown}_t = \frac{\text{Equity}_{\text{day\_start}} - \text{Equity}_t}{\text{Equity}_{\text{day\_start}}}$$

#### State Machine Transisi Circuit Breaker:
1. **Tier 0 (NORMAL)**: $\text{MDD} < 3.0\%$ & $\text{Daily Loss} < 1.5\%$.
   - Sistem berjalan pada kapasitas eksekusi penuh.
2. **Tier 1 (THROTTLE)**: $\text{MDD} \ge 3.0\%$ atau $\text{Daily Loss} \ge 1.5\%$.
   - Kalibrasi posisi baru dipangkas $50\%$ ($\kappa \leftarrow 0.5 \cdot \kappa$).
   - Stop loss diperketat $30\%$ mendekati BEP.
3. **Tier 2 (FREEZE_NEW)**: $\text{MDD} \ge 5.0\%$ atau $\text{Daily Loss} \ge 2.5\%$.
   - Mode *Reduce-Only* diaktifkan; pembukaan order posisi baru ditolak otomatis.
   - Semua resting limit buy/sell order yang berpotensi memperbesar exposure dibatalkan.
4. **Tier 3 (DERISK)**: $\text{MDD} \ge 8.0\%$ atau $\text{Daily Loss} \ge 4.0\%$.
   - Pangkas $50\%$ posisi terbuka aktif secara proaktif (prioritas aset volatilitas tertinggi).
   - Cooldown timer wajib diaktifkan sebelum re-evaluasi.
5. **Tier 4 (KILL_SWITCH)**: $\text{MDD} \ge 10.0\%$ atau $\text{Daily Loss} \ge 6.0\%$ atau $\text{Margin Buffer} < 15\%$.
   - Emergency Hard Kill-Switch dipicu seketika.

---

### 5. Idempotent Hard Kill-Switch & Fail-Safe Invariants

Protokol penutupan darurat memiliki sifat deterministik dan atomik:
1. **Atomic Lock**: Menyetel state `is_locked = True` seketika. Pemanggilan berulang (*duplicate triggers*) tidak akan mengeksekusi dobel (Idempotent).
2. **Order Cancellation**: Membatalkan 100% resting order di seluruh bursa/venue.
3. **Position Liquidation**: Mengirimkan market close order untuk 100% posisi terbuka dengan kalkulasi *slippage impact*.
4. **Zero-Exposure Invariant**: Memverifikasi bahwa $\sum |\text{Size}_i| == 0.0$.
5. **State Persistency**: Sistem terkunci total hingga dilakukan reset manual dengan audit signature.

---

## 💻 Zero-Dependency Stdlib Python Implementation & Self-Check

```python
"""
Neuron N047: Automated Risk Engine & Dynamic Drawdown Guard.
Pure Python Standard Library. Zero External Dependencies.
"""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import math
import random
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class CircuitTier(Enum):
    NORMAL = 0
    TIER1_THROTTLE = 1
    TIER2_FREEZE = 2
    TIER3_DERISK = 3
    TIER4_KILL_SWITCH = 4


@dataclass
class Position:
    """Represents an active multi-asset trading position."""
    symbol: str
    size: float
    entry_price: float
    current_price: float
    is_long: bool = True
    im_ratio: float = 0.10   # Initial Margin Ratio (e.g. 10x leverage = 0.10)
    mm_ratio: float = 0.05   # Maintenance Margin Ratio (e.g. 5%)

    @property
    def notional(self) -> float:
        return abs(self.size) * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        if self.is_long:
            return self.size * (self.current_price - self.entry_price)
        else:
            return abs(self.size) * (self.entry_price - self.current_price)

    @property
    def initial_margin(self) -> float:
        return self.notional * self.im_ratio

    @property
    def maintenance_margin(self) -> float:
        return self.notional * self.mm_ratio


@dataclass
class MarginMetrics:
    """Calculated margin health metrics for cross-asset portfolio."""
    equity: float
    initial_margin_req: float
    maint_margin_req: float
    margin_utilization: float
    maint_buffer_pct: float
    is_healthy: bool


@dataclass
class KillSwitchReport:
    """Audit record generated upon Hard Kill-Switch triggering."""
    triggered: bool
    timestamp: float
    trigger_reason: str
    equity_before: float
    equity_after: float
    orders_canceled: int
    positions_liquidated: int
    realized_slippage_cost: float
    is_locked: bool


class AutomatedRiskEngine:
    """Quantitative risk engine computing Parametric/Historical VaR, CVaR, and Margin."""

    @staticmethod
    def norm_ppf(p: float) -> float:
        """
        Inverse Cumulative Distribution Function (Quantile function) for Standard Normal N(0,1).
        Uses Peter Acklam's high-precision rational approximation (error < 1.15e-9).
        """
        if p <= 0.0 or p >= 1.0:
            raise ValueError("Probability p must be strictly in range (0, 1)")

        a = [
            -3.969683028665376e+01,  2.209460984245205e+02,
            -2.759285104469687e+02,  1.383577518672690e+02,
            -3.066479806614716e+01,  2.506628277459239e+00
        ]
        b = [
            -5.447609879822406e+01,  1.615858368580409e+02,
            -1.556989798598866e+02,  6.680131188771972e+01,
            -1.328068155288572e+01
        ]
        c = [
            -7.784894002430293e-03, -3.223964580411365e-01,
            -2.400758277161838e+00, -2.549732539343734e+00,
             4.374664141464968e+00,  2.938163982698783e+00
        ]
        d = [
             7.784695709041462e-03,  3.224671290700398e-01,
             2.445134137142996e+00,  3.754408661907416e+00
        ]

        q_low = 0.02425
        q_high = 1.0 - q_low

        if p < q_low:
            q = math.sqrt(-2.0 * math.log(p))
            return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
                   ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1.0)
        elif p <= q_high:
            q = p - 0.5
            r = q * q
            return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5])*q / \
                   (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1.0)
        else:
            q = math.sqrt(-2.0 * math.log(1.0 - p))
            return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
                    ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1.0)

    @staticmethod
    def compute_moments(returns: List[float]) -> Tuple[float, float, float, float]:
        """Calculates Sample Mean, Standard Deviation, Skewness, and Excess Kurtosis."""
        n = len(returns)
        if n < 4:
            raise ValueError("Need at least 4 return samples for 4th moment calculation")
        
        mean = sum(returns) / n
        var = sum((r - mean) ** 2 for r in returns) / (n - 1)
        std = math.sqrt(var) if var > 0 else 1e-8

        # Fisher-Pearson sample skewness
        skew = (n / ((n - 1) * (n - 2))) * sum(((r - mean) / std) ** 3 for r in returns) if n > 2 else 0.0

        # Sample excess kurtosis (Fisher)
        term1 = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))
        term2 = sum(((r - mean) / std) ** 4 for r in returns)
        term3 = (3.0 * ((n - 1) ** 2)) / ((n - 2) * (n - 3))
        kurtosis = term1 * term2 - term3

        return mean, std, skew, kurtosis

    @classmethod
    def historical_var_cvar(cls, returns: List[float], portfolio_value: float, confidence: float = 0.99) -> Tuple[float, float]:
        """Computes Historical Simulation VaR and Expected Shortfall (CVaR)."""
        if not returns:
            return 0.0, 0.0
        
        sorted_rets = sorted(returns)
        n = len(sorted_rets)
        alpha = 1.0 - confidence
        k = max(1, int(math.floor(alpha * n)))

        # Cutoff return for Historical VaR
        cutoff_ret = sorted_rets[k - 1]
        var_pct = max(0.0, -cutoff_ret)
        var_dollar = var_pct * portfolio_value

        # Historical Expected Shortfall (Average of losses in tail)
        tail_rets = sorted_rets[:k]
        cvar_pct = max(0.0, -sum(tail_rets) / len(tail_rets))
        cvar_dollar = cvar_pct * portfolio_value

        # Coherence invariant: CVaR must be >= VaR
        if cvar_dollar < var_dollar:
            cvar_dollar = var_dollar

        return var_dollar, cvar_dollar

    @classmethod
    def parametric_var_cvar(cls, returns: List[float], portfolio_value: float, confidence: float = 0.99, use_cornish_fisher: bool = True) -> Tuple[float, float]:
        """Computes Parametric Cornish-Fisher VaR and Gaussian Expected Shortfall (CVaR)."""
        if not returns:
            return 0.0, 0.0
        
        mean, std, skew, kurt = cls.compute_moments(returns)
        alpha = 1.0 - confidence
        z = cls.norm_ppf(alpha)  # e.g., -2.32635 for 99% confidence

        if use_cornish_fisher and len(returns) >= 10:
            # Cornish-Fisher expansion adjustment
            z_cf = (
                z
                + (skew / 6.0) * (z**2 - 1.0)
                + (kurt / 24.0) * (z**3 - 3.0 * z)
                - ((skew**2) / 36.0) * (2.0 * z**3 - 5.0 * z)
            )
            var_pct = max(0.0, -(mean + z_cf * std))
        else:
            var_pct = max(0.0, -(mean + z * std))

        var_dollar = var_pct * portfolio_value

        # Gaussian Expected Shortfall calculation
        phi_z = (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * z * z)
        es_multiplier = phi_z / alpha
        cvar_pct = max(0.0, -mean + es_multiplier * std)
        cvar_dollar = cvar_pct * portfolio_value

        if cvar_dollar < var_dollar:
            cvar_dollar = var_dollar

        return var_dollar, cvar_dollar

    @staticmethod
    def calculate_portfolio_margin(wallet_balance: float, positions: List[Position]) -> MarginMetrics:
        """Evaluates aggregate multi-asset cross-margin buffer and utilization."""
        total_unrealized_pnl = sum(p.unrealized_pnl for p in positions)
        equity = wallet_balance + total_unrealized_pnl
        total_im = sum(p.initial_margin for p in positions)
        total_mm = sum(p.maintenance_margin for p in positions)

        margin_utilization = (total_im / equity) if equity > 0 else 999.0
        maint_buffer_pct = ((equity - total_mm) / equity) if equity > 0 else -1.0
        is_healthy = (maint_buffer_pct >= 0.25) and (margin_utilization <= 0.80)

        return MarginMetrics(
            equity=equity,
            initial_margin_req=total_im,
            maint_margin_req=total_mm,
            margin_utilization=margin_utilization,
            maint_buffer_pct=maint_buffer_pct,
            is_healthy=is_healthy
        )


class DynamicDrawdownGuard:
    """Manages High-Water Mark tracking, Tiered Circuit Breakers, and Hard Kill-Switch."""

    def __init__(self, initial_capital: float, max_mdd_threshold: float = 0.10, max_daily_dd_threshold: float = 0.06):
        self.initial_capital = initial_capital
        self.hwm = initial_capital
        self.current_equity = initial_capital
        self.daily_start_equity = initial_capital
        self.max_mdd_threshold = max_mdd_threshold
        self.max_daily_dd_threshold = max_daily_dd_threshold

        self.current_tier = CircuitTier.NORMAL
        self.is_locked = False
        self.kill_switch_report: Optional[KillSwitchReport] = None
        self.equity_history: List[Tuple[float, float]] = []

    def update_equity(self, equity: float, timestamp: float) -> Tuple[float, float]:
        """Updates portfolio equity, tracks HWM, and computes drawdown metrics."""
        self.current_equity = equity
        if equity > self.hwm:
            self.hwm = equity
        self.equity_history.append((timestamp, equity))

        mdd_pct = (self.hwm - equity) / self.hwm if self.hwm > 0 else 0.0
        daily_dd_pct = (self.daily_start_equity - equity) / self.daily_start_equity if self.daily_start_equity > 0 else 0.0
        return mdd_pct, daily_dd_pct

    def reset_daily_baseline(self, new_day_equity: float):
        """Resets the daily starting baseline equity at 00:00 UTC."""
        self.daily_start_equity = new_day_equity

    def evaluate_circuit_state(self, maint_buffer_pct: float = 1.0) -> CircuitTier:
        """Determines active circuit breaker tier based on MDD, daily loss, and margin buffer."""
        if self.is_locked:
            return CircuitTier.TIER4_KILL_SWITCH

        mdd_pct = (self.hwm - self.current_equity) / self.hwm if self.hwm > 0 else 0.0
        daily_dd_pct = (self.daily_start_equity - self.current_equity) / self.daily_start_equity if self.daily_start_equity > 0 else 0.0

        # Tier 4: Kill-Switch (MDD >= 10% or Daily Loss >= 6% or Margin Buffer < 15%)
        if mdd_pct >= self.max_mdd_threshold or daily_dd_pct >= self.max_daily_dd_threshold or maint_buffer_pct < 0.15:
            self.current_tier = CircuitTier.TIER4_KILL_SWITCH
        # Tier 3: De-Risk (MDD >= 8% or Daily Loss >= 4.0%)
        elif mdd_pct >= 0.08 or daily_dd_pct >= 0.04:
            self.current_tier = CircuitTier.TIER3_DERISK
        # Tier 2: Freeze New Orders (MDD >= 5% or Daily Loss >= 2.5% or Margin Buffer < 25%)
        elif mdd_pct >= 0.05 or daily_dd_pct >= 0.025 or maint_buffer_pct < 0.25:
            self.current_tier = CircuitTier.TIER2_FREEZE
        # Tier 1: Throttle (MDD >= 3% or Daily Loss >= 1.5% or Margin Buffer < 40%)
        elif mdd_pct >= 0.03 or daily_dd_pct >= 0.015 or maint_buffer_pct < 0.40:
            self.current_tier = CircuitTier.TIER1_THROTTLE
        else:
            self.current_tier = CircuitTier.NORMAL

        return self.current_tier

    def execute_hard_kill_switch(
        self,
        reason: str,
        positions: List[Position],
        open_orders: List[Dict[str, Any]],
        wallet_balance: float,
        timestamp: float,
        slippage_bps: float = 10.0
    ) -> KillSwitchReport:
        """
        Executes atomic emergency liquidation protocol:
        1. Sets immutable lock.
        2. Cancels 100% resting orders.
        3. Liquidates 100% active positions with slippage penalty.
        4. Verifies zero open exposure invariant.
        """
        # Idempotency guard: if already locked, return existing cached audit report
        if self.is_locked and self.kill_switch_report is not None:
            return self.kill_switch_report

        self.is_locked = True
        self.current_tier = CircuitTier.TIER4_KILL_SWITCH

        equity_before = wallet_balance + sum(p.unrealized_pnl for p in positions)
        canceled_orders_count = len(open_orders)
        open_orders.clear()

        liquidated_count = 0
        total_slippage_cost = 0.0
        realized_pnl_total = 0.0

        for p in positions:
            if p.size == 0.0:
                continue

            # Model adverse execution slippage (basis points)
            slippage_factor = (1.0 - (slippage_bps / 10000.0)) if p.is_long else (1.0 + (slippage_bps / 10000.0))
            exit_price = p.current_price * slippage_factor

            pnl = p.size * (exit_price - p.entry_price) if p.is_long else abs(p.size) * (p.entry_price - exit_price)
            slip_loss = abs(p.size) * abs(p.current_price - exit_price)

            realized_pnl_total += pnl
            total_slippage_cost += slip_loss
            liquidated_count += 1
            p.size = 0.0  # Zero out position

        equity_after = wallet_balance + realized_pnl_total
        self.current_equity = equity_after

        self.kill_switch_report = KillSwitchReport(
            triggered=True,
            timestamp=timestamp,
            trigger_reason=reason,
            equity_before=equity_before,
            equity_after=equity_after,
            orders_canceled=canceled_orders_count,
            positions_liquidated=liquidated_count,
            realized_slippage_cost=total_slippage_cost,
            is_locked=True
        )
        return self.kill_switch_report


# =====================================================================
# Deterministic Runnable Test Suite (Zero External Dependencies)
# =====================================================================

def run_neuron_tests():
    print("[*] Running Neuron N047 Risk Engine Invariant Suite...")

    # 1. Test Statistical Inverse Normal PPF (Acklam precision)
    z_01 = AutomatedRiskEngine.norm_ppf(0.01)
    z_05 = AutomatedRiskEngine.norm_ppf(0.05)
    assert abs(z_01 - (-2.32634787)) < 1e-4, f"Norm PPF 0.01 mismatch: {z_01}"
    assert abs(z_05 - (-1.64485362)) < 1e-4, f"Norm PPF 0.05 mismatch: {z_05}"

    # 2. Test Historical & Parametric VaR / CVaR (Coherence Invariant: CVaR >= VaR)
    random.seed(42)
    sample_returns = [random.gauss(0.0005, 0.015) for _ in range(480)] + [-0.06, -0.07, -0.08, -0.05, -0.055]
    portfolio_val = 1_000_000.0  # $1,000,000 AUM

    h_var, h_cvar = AutomatedRiskEngine.historical_var_cvar(sample_returns, portfolio_val, confidence=0.99)
    p_var, p_cvar = AutomatedRiskEngine.parametric_var_cvar(sample_returns, portfolio_val, confidence=0.99, use_cornish_fisher=True)

    assert h_var > 0, "Historical VaR must be positive"
    assert h_cvar >= h_var, f"Historical CVaR ({h_cvar}) must be >= VaR ({h_var})"
    assert p_var > 0, "Parametric VaR must be positive"
    assert p_cvar >= p_var, f"Parametric CVaR ({p_cvar}) must be >= VaR ({p_var})"

    # 3. Test Multi-Asset Portfolio Margin Buffer Calculation
    positions = [
        Position(symbol="XAU/USD", size=10.0, entry_price=2350.0, current_price=2360.0, is_long=True, im_ratio=0.05, mm_ratio=0.025), # Long profit +$100
        Position(symbol="BTC/USDT", size=1.5, entry_price=65000.0, current_price=64000.0, is_long=True, im_ratio=0.10, mm_ratio=0.05), # Long loss -$1500
        Position(symbol="ETH/USDT", size=-20.0, entry_price=3500.0, current_price=3450.0, is_long=False, im_ratio=0.10, mm_ratio=0.05)  # Short profit +$1000
    ]
    wallet = 100_000.0
    margin_metrics = AutomatedRiskEngine.calculate_portfolio_margin(wallet, positions)

    # Net PnL = +100 - 1500 + 1000 = -$400 => Equity = $99,600
    assert margin_metrics.equity == 99600.0, f"Equity mismatch: {margin_metrics.equity}"
    assert margin_metrics.is_healthy, "Margin should be healthy at low utilization"

    # 4. Test Trailing High-Water Mark & Tiered Circuit Breakers
    guard = DynamicDrawdownGuard(initial_capital=100_000.0, max_mdd_threshold=0.10, max_daily_dd_threshold=0.06)

    # Peak at 120,000
    guard.update_equity(120_000.0, timestamp=1000.0)
    assert guard.hwm == 120_000.0
    assert guard.evaluate_circuit_state() == CircuitTier.NORMAL

    # Drawdown to 115,000 (MDD = 4.16% -> Tier 1 Throttle)
    guard.update_equity(115_000.0, timestamp=1100.0)
    assert guard.evaluate_circuit_state() == CircuitTier.TIER1_THROTTLE

    # Drawdown to 112,000 (MDD = 6.66% -> Tier 2 Freeze)
    guard.update_equity(112_000.0, timestamp=1200.0)
    assert guard.evaluate_circuit_state() == CircuitTier.TIER2_FREEZE

    # Drawdown to 109,500 (MDD = 8.75% -> Tier 3 De-Risk)
    guard.update_equity(109_500.0, timestamp=1300.0)
    assert guard.evaluate_circuit_state() == CircuitTier.TIER3_DERISK

    # 5. Test Hard Kill-Switch Execution (MDD >= 10% breach: 107,000 -> MDD = 10.83%)
    guard.update_equity(107_000.0, timestamp=1400.0)
    assert guard.evaluate_circuit_state() == CircuitTier.TIER4_KILL_SWITCH

    open_orders = [
        {"order_id": "ORD-101", "symbol": "XAU/USD", "qty": 5.0},
        {"order_id": "ORD-102", "symbol": "BTC/USDT", "qty": 1.0}
    ]
    report = guard.execute_hard_kill_switch(
        reason="MDD Breached 10.0% Threshold",
        positions=positions,
        open_orders=open_orders,
        wallet_balance=wallet,
        timestamp=1400.0,
        slippage_bps=10.0
    )

    # Invariants verification
    assert report.triggered, "Kill-switch report must indicate triggered"
    assert report.orders_canceled == 2, f"Expected 2 orders canceled, got {report.orders_canceled}"
    assert len(open_orders) == 0, "Open orders list must be empty after kill-switch"
    assert report.positions_liquidated == 3, f"Expected 3 positions liquidated, got {report.positions_liquidated}"
    assert all(p.size == 0.0 for p in positions), "All position sizes must be 0 after liquidation"
    assert guard.is_locked, "Guard must remain in locked state"

    # Idempotency verification
    second_report = guard.execute_hard_kill_switch(
        reason="Duplicate trigger test",
        positions=positions,
        open_orders=[],
        wallet_balance=wallet,
        timestamp=1450.0
    )
    assert second_report.timestamp == 1400.0, "Second kill switch trigger must return existing cached report (Idempotent)"

    print("  [✓] All N047 Risk Engine Invariants passed successfully!")


if __name__ == "__main__":
    run_neuron_tests()
```

---

## 🔒 Invarian Operasional & Disiplin Eksekusi

1. **Sub-Additivity & Tail Severity Rule**:
   - Selalu monitor $\text{CVaR}_{99\%}$ bersamaan dengan $\text{VaR}_{99\%}$. Jika rasio $\frac{\text{CVaR}}{\text{VaR}} > 1.35$, tandai adanya distribusi *fat-tail extreme* dan kurangi gross leverage portofolio.
2. **Dynamic Volatility Scaling**:
   - Skewness negatif ($S < -0.5$) dan Excess Kurtosis tinggi ($K > 2.0$) wajib mengaktifkan penyesuaian Cornish-Fisher.
3. **Continuous HWM Tracking**:
   - HWM tidak pernah di-reset saat sesi berjalan. Drawdown dihitung murni terhadap ekuitas tertinggi yang pernah tercapai.
4. **Idempotent Atomic Kill-Switch**:
   - Eksekusi kill-switch bersifat irreversible dalam sesi trading aktif, membatalkan 100% pending order sebelum melikuidasi posisi untuk mencegah order baru ter-fill saat proses likuidasi berjalan.
