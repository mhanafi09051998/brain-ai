# Neuron N025: High-Frequency Orderbook Microstructure & HFT Quant Engine

## ?? Domain & Arsitektur
- **Domain**: High-Frequency Trading (HFT), Market Microstructure, L2/L3 Orderbook Reconstruction, Algorithmic Execution, Quantitative Arbitrage (Gold XAU/USD, Crypto CEX/DEX).
- **Core Invariant**: Jangan pernah mengeksekusi order kuantitatif berdasarkan harga *mid-market* naif tanpa memperhitungkan *orderbook queue imbalance*, *dynamic liquidity slippage*, *cross-venue latency penalty*, dan *drawdown-bounded Kelly allocation*.

---

## ? 4 Pilar Mikrostruktur & Eksekusi Kuantitatif

### 1. L2/L3 Orderbook Delta & Micro-Price Dynamics
- **L2 (Price-Aggregated) vs L3 (Market-By-Order - MBO)**:
  - L2 menyimpan akumulasi volume pada setiap tick harga $(P_i, V_i)$.
  - L3 melacak lifecycle setiap individual order $(\text{order\_id}, \text{price}, \text{size}, \text{priority})$.
- **Sequence Gap & Snapshot Resynchronization**:
  - Setiap delta WebSocket update memiliki `seq_id` monotonik.
  - Jika $\text{seq}_{incoming} \neq \text{seq}_{local} + 1$, bekukan order routing, drop queue, dan minta L2 snapshot baru dari REST API untuk mencegah *phantom fill* atau *stale pricing*.
- **Order Book Imbalance (OBI)**:
  $$I = \frac{V_b - V_a}{V_b + V_a}, \quad I \in [-1, 1]$$
- **Micro-Price (Stoikov-Shifted Mid-Price)**:
  $$P_{\text{micro}} = P_b \cdot \left(\frac{V_a}{V_b + V_a}\right) + P_a \cdot \left(\frac{V_b}{V_b + V_a}\right) = \frac{P_b V_a + P_a V_b}{V_b + V_a}$$
  Jika $V_b \gg V_a$, $P_{\text{micro}} \to P_a$ (tekanan beli mendorong probabilitas fill pada ask).

---

### 2. Gold (XAU/USD) & DEX Cross-Venue Arbitrage
- **Gold Triad Invariant**:
  - London Bullion Market (LBMA Spot XAU/USD) $\leftrightarrow$ COMEX Gold Futures (GC) $\leftrightarrow$ Tokenized Gold (PAXG / XAUt).
  - *Basis Spread*: $S_{basis} = P_{futures} - P_{spot} - (\text{Carry Cost} - \text{Convenience Yield})$.
- **CEX-DEX Latency & Constant Product Market Maker (CPMM) Arbitrage**:
  - AMM Pool: $x \cdot y = k \implies P_{DEX} = \frac{y}{x}$.
  - Profit Arb Terbuka jika:
    $$\Delta P = |P_{CEX} - P_{DEX}| > \text{Fee}_{CEX} + \text{Fee}_{DEX} + \text{Gas}_{tx} + \text{Impact}_{slip} + \text{Adverse Selection Margin}$$
- **Triangular Cycle Detection**:
  - Graf mata uang dengan bobot edge $-\ln(\text{rate}_{ij} \cdot (1 - \text{fee}))$.
  - Deteksi siklus negatif via Bellman-Ford untuk arbitrase instan tanpa risiko arah pasar (*delta-neutral*).

---

### 3. Fractional Kelly Criterion & Risk of Ruin
- **Discrete Formulation (Win/Loss Payoff)**:
  $$f^* = \frac{b \cdot p - q}{b} = \frac{p(b+1) - 1}{b}$$
  di mana $b = \frac{\text{Avg Win}}{\text{Avg Loss}}$, $p = P(\text{Win})$, $q = 1 - p$.
- **Continuous / Gaussian Form**:
  $$f^* = \frac{\mu - r}{\sigma^2}$$
- **Half-Kelly / Fractional Guardrail ($\kappa = 0.25 - 0.5$)**:
  - Full Kelly ($f^*$) memaksimalkan expected $\log(\text{wealth})$, tetapi menghasilkan $MDD > 50\%$ dan rentan terhadap estimasi parameter yang noisy.
  - Terapkan $f_{actual} = \kappa \cdot f^*$ untuk memangkas variansi portofolio sebesar $75\%$ dengan tetap mempertahankan $87.5\%$ dari laju pertumbuhan optimal (*growth rate*).

---

### 4. Dynamic Slippage & Almgren-Chriss Market Impact
- **Discrete Level Sweeping**:
  - Menghitung harga eksekusi tertimbang volume (*Volume-Weighted Execution Price* - VWEP):
    $$\bar{P}_{exec} = \frac{\sum_{k=1}^m p_k \cdot v_k}{Q}, \quad \text{Slip}_{bps} = \left|\frac{\bar{P}_{exec} - P_{BBO}}{P_{BBO}}\right| \times 10^4$$
- **Almgren-Chriss Impact Framework**:
  - *Permanent Impact* (Informasi yang diserap pasar): $I_{perm} = \gamma \cdot \frac{Q}{V_{ADV}}$
  - *Temporary Impact* (Likuiditas sesaat yang terkuras): $I_{temp} = \eta \cdot \text{sign}(Q) \cdot \left(\frac{|Q|}{V_{trade}}\right)^\alpha$ $(\alpha \approx 0.5)$

---

## ?? Zero-Dependency Stdlib Python Implementation & Self-Check

```python
"""
Neuron N025: High-Frequency Orderbook Microstructure & HFT Execution Simulator.
Standard library only. Deterministic validation suite.
"""

from typing import Dict, List, Tuple
import math

class OrderBookL2:
    """L2 Aggregated Limit Order Book with Delta Processing & Micro-Price."""
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids: Dict[float, float] = {}  # Price -> Size
        self.asks: Dict[float, float] = {}  # Price -> Size
        self.last_seq: int = 0

    def apply_delta(self, seq: int, side: str, price: float, size: float) -> bool:
        """Applies incremental book update. Returns False on sequence gap."""
        if self.last_seq != 0 and seq != self.last_seq + 1:
            return False  # Sequence gap: requires snapshot reset
        
        self.last_seq = seq
        book = self.bids if side == "bid" else self.asks
        if size <= 0.0:
            book.pop(price, None)
        else:
            book[price] = size
        return True

    def get_bbo(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Returns ((best_bid_p, best_bid_v), (best_ask_p, best_ask_v))."""
        if not self.bids or not self.asks:
            raise ValueError("Incomplete order book")
        best_bid_p = max(self.bids.keys())
        best_ask_p = min(self.asks.keys())
        return (best_bid_p, self.bids[best_bid_p]), (best_ask_p, self.asks[best_ask_p])

    def calculate_microprice(self) -> float:
        """Calculates volume-weighted micro-price (Stoikov formulation)."""
        (bb_p, bb_v), (ba_p, ba_v) = self.get_bbo()
        total_v = bb_v + ba_v
        if total_v == 0:
            return (bb_p + ba_p) / 2.0
        return (bb_p * ba_v + ba_p * bb_v) / total_v

    def calculate_order_imbalance(self) -> float:
        """Calculates Order Book Imbalance (OBI) in range [-1.0, 1.0]."""
        (_, bb_v), (_, ba_v) = self.get_bbo()
        denom = bb_v + ba_v
        return (bb_v - ba_v) / denom if denom > 0 else 0.0

    def simulate_sweep(self, side: str, order_size: float) -> Tuple[float, float]:
        """Simulates market order sweep through book. Returns (vwap_price, slippage_bps)."""
        if order_size <= 0:
            raise ValueError("Order size must be positive")
        
        book_items = sorted(self.asks.items(), key=lambda x: x[0]) if side == "buy" else sorted(self.bids.items(), key=lambda x: x[0], reverse=True)
        (best_p, _) = book_items[0]
        
        remaining = order_size
        cost = 0.0
        for price, vol in book_items:
            fill_v = min(remaining, vol)
            cost += fill_v * price
            remaining -= fill_v
            if remaining <= 0:
                break
        
        if remaining > 0:
            raise ValueError("Insufficient liquidity to fill market order")
        
        avg_price = cost / order_size
        slippage_bps = abs(avg_price - best_p) / best_p * 10000.0
        return avg_price, slippage_bps


class QuantRiskEngine:
    """Fractional Kelly Criterion & Position Sizing Engine."""
    @staticmethod
    def fractional_kelly(win_rate: float, win_loss_ratio: float, fraction: float = 0.5) -> float:
        """Computes fractional Kelly fraction f = kappa * ((p*b - q)/b)."""
        if win_rate <= 0 or win_rate >= 1 or win_loss_ratio <= 0:
            return 0.0
        q = 1.0 - win_rate
        f_star = (win_rate * win_loss_ratio - q) / win_loss_ratio
        if f_star <= 0:
            return 0.0
        return max(0.0, min(1.0, f_star * fraction))

    @staticmethod
    def almgren_chriss_impact(qty: float, daily_vol: float, sigma: float, eta: float = 0.1, gamma: float = 0.05) -> float:
        """Calculates combined permanent + temporary market impact estimate."""
        adv_ratio = qty / daily_vol if daily_vol > 0 else 0.0
        perm_impact = gamma * sigma * adv_ratio
        temp_impact = eta * sigma * math.sqrt(adv_ratio)
        return perm_impact + temp_impact


# Self-Check Verification Suite
def run_neuron_tests():
    # 1. Test Order Book & Delta Reconstruction
    ob = OrderBookL2("XAU/USD")
    assert ob.apply_delta(1, "bid", 2350.00, 10.0)
    assert ob.apply_delta(2, "bid", 2349.90, 25.0)
    assert ob.apply_delta(3, "ask", 2350.20, 5.0)
    assert ob.apply_delta(4, "ask", 2350.50, 20.0)
    
    # Gap detection check
    assert not ob.apply_delta(6, "bid", 2349.80, 15.0), "Sequence gap should be rejected"
    assert ob.apply_delta(5, "bid", 2349.80, 15.0), "Continuous sequence must be accepted"

    # Micro-price check (Heavy Bid should pull microprice towards ask)
    micro_p = ob.calculate_microprice()
    mid_p = (2350.00 + 2350.20) / 2.0  # 2350.10
    obi = ob.calculate_order_imbalance()
    # Bid Vol = 10, Ask Vol = 5 => Imbalance = (10 - 5)/15 = +0.333
    assert obi > 0.33 and obi < 0.34, f"Unexpected OBI: {obi}"
    # Micro-price = (2350.00*5 + 2350.20*10) / 15 = 2350.1333... > mid_p
    assert micro_p > mid_p, f"Microprice {micro_p} should be shifted above mid {mid_p} due to bid pressure"

    # 2. Test Market Order Sweep & Slippage
    avg_p, slip = ob.simulate_sweep("buy", 15.0)
    # Buy 15: fills 5 @ 2350.20 + 10 @ 2350.50 => cost = 11751 + 23505 = 35256 / 15 = 2350.40
    assert abs(avg_p - 2350.40) < 1e-6, f"Expected 2350.40 avg price, got {avg_p}"
    assert slip > 0.0, "Slippage must be positive for multi-level sweep"

    # 3. Test Kelly Sizing Engine
    # 60% win rate, 1.5:1 payoff ratio -> full Kelly = (0.6*1.5 - 0.4)/1.5 = 0.5 / 1.5 = 0.3333
    # Half-Kelly (kappa=0.5) -> 0.1666...
    half_k = QuantRiskEngine.fractional_kelly(0.60, 1.50, 0.5)
    assert abs(half_k - (1.0 / 6.0)) < 1e-4, f"Unexpected half-Kelly fraction: {half_k}"

    # Negative EV should yield 0 allocation
    neg_k = QuantRiskEngine.fractional_kelly(0.40, 1.0, 0.5)
    assert neg_k == 0.0, "Negative EV trade must yield 0 allocation"

    # 4. Market Impact
    impact = QuantRiskEngine.almgren_chriss_impact(qty=100.0, daily_vol=100000.0, sigma=0.015)
    assert impact > 0.0, "Market impact must be strictly positive for non-zero volume"

    print("  [?] Neuron N025 Invariants Verified: L2 Delta, Micro-Price, Slippage, & Fractional Kelly.")

if __name__ == "__main__":
    run_neuron_tests()
```

---

## ?? Invariant Ringkas
1. **Never Trade on Flat Mid-Price**: Gunakan $P_{\text{micro}}$ untuk menangkap tekanan likuiditas mikrostruktur sebelum orderbook bergerak.
2. **Strict Sequence Continuity**: Tolak dan resync state ketika terjadi *sequence gap* pada WebSocket delta feed.
3. **Half-Kelly Ceiling ($\kappa \le 0.5$)**: Lindungi modal dari *estimation error* dan *fat-tail volatility*.
4. **Depth Sweep Validation**: Selalu estimasi *slippage* riil berbasis kedalaman L2 sebelum mengirimkan market order agresif.
