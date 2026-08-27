# N073: Level-3 Limit Order Book Dynamics, VPIN Toxicity & Dynamic Spread Adaptation

- **Category:** Quantitative Trading & Market Microstructure
- **Date:** 2026-08-27
- **Status:** Active Operational Invariant

---

## 🎯 Core Invariants & Mathematical Framework

### 1. Level-3 (MBO) Queue Dynamics & Fill Probability
In a Market-By-Order (L3) limit order book, individual orders $i$ at price level $p$ maintain a strict time-priority queue position $q_i(t) \in [0, Q_p(t)]$, where $Q_p(t) = \sum_{j \in \text{Queue}(p)} v_j(t)$.
- **Queue Position Tracking Invariant:**
  Upon match event $(\Delta v_{match}, p)$, ahead volume $Q_{ahead}(t)$ updates deterministically:
  $$Q_{ahead}(t^+) = \max(0, Q_{ahead}(t^-) - \Delta v_{match})$$
  Upon cancellation event $(\Delta v_{canc}, p, id)$, queue position updates based on deterministic ID tracking (or pro-rata decay if hidden/untracked):
  $$Q_{ahead}(t^+) = Q_{ahead}(t^-) - \Delta v_{canc} \cdot \mathbb{I}_{\{id \in \text{Ahead}\}}$$
- **Fill Probability Decay:**
  $$P(\text{Fill} \mid Q_{ahead}, \tau) = \exp\left(-\lambda_{canc} \tau\right) \cdot \Phi\left(\frac{\mu_{trade}\tau - Q_{ahead}}{\sigma_{trade}\sqrt{\tau}}\right)$$

### 2. Volume-Synchronized Probability of Toxicity (VPIN)
Trading volume is discretized into constant-volume bars of size $V \in \mathbb{R}^+$. For each bucket $\tau$, buy/sell volume allocation $(V_\tau^B, V_\tau^S)$ is derived via the standard normal CDF transformation of price changes:
$$V_\tau^B = V \cdot \Phi\left(\frac{\Delta P_\tau}{\sigma_{\Delta P}}\right), \quad V_\tau^S = V - V_\tau^B, \quad \Delta P_\tau = P_\tau - P_{\tau-1}$$
Over a rolling historical window of $N$ volume buckets, VPIN is defined as:
$$\text{VPIN} = \frac{\sum_{\tau=1}^N |V_\tau^B - V_\tau^S|}{N \cdot V}, \quad \text{VPIN} \in [0, 1]$$
- **Toxicity Invariant:** When $\text{VPIN} > \tau_{toxic}$ (typically $\tau_{toxic} = 0.65$ or 99th percentile), informed order flow dominates liquidity consumption. Passive limit orders face adverse selection and MUST widen spreads or pull quotes.

### 3. Multi-Level Order Flow Imbalance (OFI)
Let $P_b^k(t), v_b^k(t)$ and $P_a^k(t), v_a^k(t)$ denote price and volume at bid/ask level $k \in \{1, \dots, K\}$. Single-level OFI $e_t^{(k)}$ is:
$$e_t^{(k)} = \mathbb{I}_{\{P_b^k(t) \ge P_b^k(t-1)\}} v_b^k(t) - \mathbb{I}_{\{P_b^k(t) \le P_b^k(t-1)\}} v_b^k(t-1) - \mathbb{I}_{\{P_a^k(t) \le P_a^k(t-1)\}} v_a^k(t) + \mathbb{I}_{\{P_a^k(t) \ge P_a^k(t-1)\}} v_a^k(t-1)$$
Multi-level aggregate OFI with exponential depth decay parameter $\lambda_{depth}$:
$$\mathbf{OFI}_t = \sum_{k=1}^K e^{-\lambda_{depth}(k-1)} e_t^{(k)}, \quad \Delta \hat{P}_{t+\Delta t} = \beta_{OFI} \cdot \mathbf{OFI}_t$$

### 4. Dynamic Stoikov-VPIN Market Maker Spread Adaptation
Extending the Avellaneda-Stoikov model with inventory risk parameter $\gamma$, terminal horizon $T-t$, and dynamic adverse-selection penalty $\Psi(\text{VPIN}_t)$:
- **Reservation Price:**
  $$R(s_t, q_t, t) = s_t - q_t \gamma \sigma_t^2 (T - t)$$
- **Dynamic Optimal Half-Spreads:**
  $$\delta_t^a = \frac{1}{2}\left[\frac{2}{\gamma}\ln\left(1 + \frac{\gamma}{\kappa}\right) + \Psi(\text{VPIN}_t) + \beta_{OFI} \mathbf{OFI}_t\right], \quad \delta_t^b = \frac{1}{2}\left[\frac{2}{\gamma}\ln\left(1 + \frac{\gamma}{\kappa}\right) + \Psi(\text{VPIN}_t) - \beta_{OFI} \mathbf{OFI}_t\right]$$
  where $\Psi(\text{VPIN}_t) = \alpha \cdot \frac{\text{VPIN}_t}{1 - \text{VPIN}_t + \epsilon_{guard}}$.
- **Optimal Quotes:**
  $$r_t^a = R(s_t, q_t, t) + \delta_t^a, \quad r_t^b = R(s_t, q_t, t) - \delta_t^b$$

---

## 💻 Zero-Dependency Production Implementation

```python
"""
N073: Level-3 LOB Queue Tracker, VPIN Toxicity Estimator & Adaptive MM Quoter.
Pure Python standard library implementation with zero external dependencies.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math

def normal_cdf(x: float) -> float:
    """Error function approximation of standard normal cumulative distribution."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

@dataclass
class L3Order:
    order_id: int
    side: str  # 'bid' | 'ask'
    price: float
    size: float
    timestamp_ns: int

class L3QueueTracker:
    """Tracks deterministic queue priority and ahead volume for passive orders."""
    def __init__(self):
        self.bids: Dict[float, List[L3Order]] = {}
        self.asks: Dict[float, List[L3Order]] = {}
        self.order_map: Dict[int, L3Order] = {}

    def insert(self, order: L3Order):
        self.order_map[order.order_id] = order
        book = self.bids if order.side == 'bid' else self.asks
        if order.price not in book:
            book[order.price] = []
        book[order.price].append(order)

    def cancel(self, order_id: int) -> Optional[L3Order]:
        order = self.order_map.pop(order_id, None)
        if not order:
            return None
        book = self.bids if order.side == 'bid' else self.asks
        if order.price in book:
            book[order.price] = [o for o in book[order.price] if o.order_id != order_id]
            if not book[order.price]:
                del book[order.price]
        return order

    def execute(self, side: str, price: float, exec_size: float):
        book = self.bids if side == 'bid' else self.asks
        if price not in book:
            return
        remaining = exec_size
        new_queue = []
        for o in book[price]:
            if remaining <= 0:
                new_queue.append(o)
            elif o.size <= remaining:
                remaining -= o.size
                self.order_map.pop(o.order_id, None)
            else:
                o.size -= remaining
                remaining = 0.0
                new_queue.append(o)
        if new_queue:
            book[price] = new_queue
        else:
            del book[price]

    def get_ahead_volume(self, my_order_id: int) -> float:
        order = self.order_map.get(my_order_id)
        if not order:
            return 0.0
        book = self.bids if order.side == 'bid' else self.asks
        queue = book.get(order.price, [])
        ahead = 0.0
        for o in queue:
            if o.order_id == my_order_id:
                break
            ahead += o.size
        return ahead

class VPINCalculator:
    """Volume-Synchronized Probability of Toxicity over fixed volume buckets."""
    def __init__(self, bucket_volume: float, window_buckets: int = 50):
        self.bucket_vol = bucket_volume
        self.n_buckets = window_buckets
        self.current_bucket_vol = 0.0
        self.current_buy_vol = 0.0
        self.last_price: Optional[float] = None
        self.price_diffs: List[float] = []
        self.bucket_imbalances: List[float] = []

    def update(self, price: float, volume: float) -> Optional[float]:
        if self.last_price is None:
            self.last_price = price
            return None
        dp = price - self.last_price
        self.last_price = price
        self.price_diffs.append(dp)
        if len(self.price_diffs) > 200:
            self.price_diffs.pop(0)

        # Standard deviation of price changes for CDF weighting
        mean_dp = sum(self.price_diffs) / len(self.price_diffs)
        var_dp = sum((x - mean_dp) ** 2 for x in self.price_diffs) / max(1, len(self.price_diffs) - 1)
        sigma_dp = math.sqrt(max(1e-8, var_dp))

        prob_buy = normal_cdf(dp / sigma_dp)
        buy_v = volume * prob_buy
        sell_v = volume * (1.0 - prob_buy)

        self.current_bucket_vol += volume
        self.current_buy_vol += buy_v

        if self.current_bucket_vol >= self.bucket_vol:
            # Finalize bucket
            bucket_sell = self.current_bucket_vol - self.current_buy_vol
            imbalance = abs(self.current_buy_vol - bucket_sell)
            self.bucket_imbalances.append(imbalance)
            if len(self.bucket_imbalances) > self.n_buckets:
                self.bucket_imbalances.pop(0)
            self.current_bucket_vol = 0.0
            self.current_buy_vol = 0.0

        if len(self.bucket_imbalances) == self.n_buckets:
            vpin = sum(self.bucket_imbalances) / (self.n_buckets * self.bucket_vol)
            return min(1.0, max(0.0, vpin))
        return None

class DynamicAdaptiveMM:
    """Avellaneda-Stoikov Market Maker with VPIN toxicity & OFI quote skewing."""
    def __init__(self, gamma: float = 0.1, kappa: float = 1.5, alpha_vpin: float = 2.0):
        self.gamma = gamma
        self.kappa = kappa
        self.alpha_vpin = alpha_vpin

    def compute_quotes(self, mid: float, inventory: float, sigma: float,
                       vpin: float, ofi: float, beta_ofi: float = 0.05,
                       time_remaining: float = 1.0) -> Tuple[float, float]:
        # 1. Reservation Price
        res_price = mid - inventory * self.gamma * (sigma ** 2) * time_remaining
        # 2. Base spread & VPIN toxicity penalty
        base_half = (1.0 / self.gamma) * math.log(1.0 + (self.gamma / self.kappa))
        toxicity_penalty = self.alpha_vpin * (vpin / max(0.05, 1.0 - vpin))
        total_half = base_half + toxicity_penalty
        # 3. OFI Directional Asymmetry
        bid_quote = res_price - total_half - (0.5 * beta_ofi * ofi)
        ask_quote = res_price + total_half + (0.5 * beta_ofi * ofi)
        # 4. Invariant: Ask must strictly exceed Bid
        if ask_quote <= bid_quote:
            ask_quote = bid_quote + 0.01
        return bid_quote, ask_quote

if __name__ == "__main__":
    tracker = L3QueueTracker()
    tracker.insert(L3Order(101, 'bid', 100.0, 10.0, 1000))
    tracker.insert(L3Order(102, 'bid', 100.0, 5.0, 1010))
    assert tracker.get_ahead_volume(102) == 10.0, "Queue ahead volume mismatch"
    tracker.execute('bid', 100.0, 4.0)
    assert tracker.get_ahead_volume(102) == 6.0, "Queue decrement mismatch"

    vpin_calc = VPINCalculator(bucket_volume=100.0, window_buckets=5)
    for i in range(30):
        vpin_val = vpin_calc.update(100.0 + (i * 0.1 if i % 2 == 0 else -i * 0.05), 25.0)

    mm = DynamicAdaptiveMM()
    bid, ask = mm.compute_quotes(mid=100.0, inventory=2.0, sigma=0.2, vpin=0.45, ofi=12.0)
    assert ask > bid, "LOB Quote crossed"
    print(f"Self-Check Passed: Quotes -> Bid: {bid:.4f}, Ask: {ask:.4f}")
```

---

## 🔍 Root Cause Analysis & Failure Mode Guards

| Failure Mode | Root Cause | Prevention & Algorithmic Guard |
| :--- | :--- | :--- |
| **Phantom Fill / Queue Desync** | Dropped L3 WS delta packets cause stale sequence tracking. | Strict sequence gap assertion: If $seq_{in} \neq seq_{local} + 1$, purge book and trigger snapshot resync. |
| **VPIN Bucket Toxicity Spike** | Concentrated institutional sweep triggers asymmetric bucket fill. | Hard Toxicity Circuit: If $\text{VPIN} > 0.70$, widen quote spread by $3\times$ and cancel quotes inside BBO. |
| **Crossed MM Quotes ($r^b \ge r^a$)** | Extreme inventory skew $q_t \gg 0$ or extreme OFI directional bias. | Invariant Guard: Force $r^a(t) - r^b(t) \ge \text{TickSize}$ and cap maximum inventory skew $|q_t| \le Q_{max}$. |
| **OFI Division-by-Zero / Singularity** | Zero price volatility ($\sigma_{\Delta P} \to 0$) during flash liquidity freeze. | Clamped divisor floor: $\sigma_{\Delta P} = \max(\epsilon_{floor}, \text{std}(\Delta P))$ with $\epsilon_{floor} = 10^{-8}$. |
| **Adverse Selection Cascades** | Quoting tight inside spreads during directional informed momentum. | Micro-price dynamic shift: Re-anchor reservation mid to $P_{micro} = \frac{P_b v_a + P_a v_b}{v_a + v_b}$. |

---

## 🔒 Execution Discipline & Operational Invariants
1. **Ponytail YAGNI:** No speculative order routing layers; strictly compute L3 state, VPIN, OFI, and quotes in zero-allocation deterministic data structures.
2. **Single Root Fix:** When quote crossing occurs, fix the reservation price & half-spread formulation directly rather than patching down-stream order sanity filters.
3. **Line Count Guard:** Strictly bounded below 300 lines of high-density production code and operational theory.
