# Neuron N048: DeFi Liquidity Engineering & Cross-Chain MEV Protection

## 🧠 Domain & Arsitektur
- **Domain**: DeFi Quantitative Liquidity, Concentrated Liquidity AMMs (Uniswap v3 Tick Mathematics), Impermanent Loss & Volatility Calculus, Uncollateralized Flash Loan Arbitrage, Toxic MEV Dynamics (Sandwich Attacks, Just-In-Time Liquidity), Searcher-Builder Infrastructure (Flashbots Protect, Jito-Solana MEV Relays, Private Bundles, PBS Architecture).
- **Core Invariant**: Jangan pernah mengeksekusi penyediaan likuiditas DeFi atau perutean order on-chain tanpa memodelkan dinamika kurva terpusat $(\Delta x, \Delta y)$, menghitung batas kerugian impermanen (*impermanent loss leverage*), mengunci atomisitas eksekusi Flash Loan via `revert()` guard, dan melindungi transaksi bernilai tinggi dari serangan *sandwich MEV* melalui *private builder bundles* dan *dynamic adaptive slippage*.

---

## 🏛️ 5 Pilar DeFi Liquidity Engineering & MEV Defense

### 1. Uniswap v3 Concentrated Liquidity Math & Tick Geometry
- **Kurva Likuiditas Terpusat & Virtual Reserves**:
  Uniswap v3 membatasi penyediaan likuiditas pada interval harga $[P_a, P_b]$. Kurva invarian dinyatakan sebagai:
  $$\left(x + \frac{L}{\sqrt{P_b}}\right)\left(y + L\sqrt{P_a}\right) = L^2$$
  di mana $L = \sqrt{k}$ adalah *liquidity density*, $x$ dan $y$ adalah cadangan riil dalam rentang tersebut.

- **Tick Geometry & Fixed-Point Arithmetic ($Q64.96$)**:
  - Hubungan Tick Index $i$ dan Harga $P$:
    $$P(i) = 1.0001^i \implies \sqrt{P}(i) = 1.0001^{i/2}$$
  - Tick Spacing $t_s$ menentukan granularitas interval (e.g., $t_s = 10$ untuk fee 0.05%, $t_s = 60$ untuk fee 0.3%).
  - Token amounts sebagai fungsi dari $\sqrt{P}, \sqrt{P_a}, \sqrt{P_b}$:
    $$\Delta x = \Delta\left(\frac{1}{\sqrt{P}}\right) \cdot L = L \cdot \frac{\sqrt{P_b} - \sqrt{P}}{\sqrt{P} \cdot \sqrt{P_b}} \quad (\text{saat } P < P_b)$$
    $$\Delta y = \Delta(\sqrt{P}) \cdot L = L \cdot (\sqrt{P} - \sqrt{P_a}) \quad (\text{saat } P > P_a)$$

- **Status Alokasi Portofolio Berdasarkan Posisi Rentang**:
  - $P \le P_a$: Posisi 100% terdiri dari Token 0 ($x > 0, y = 0$).
  - $P \ge P_b$: Posisi 100% terdiri dari Token 1 ($x = 0, y > 0$).
  - $P_a < P < P_b$: Posisi aktif terdiversifikasi ($x > 0, y > 0$).

---

### 2. Impermanent Loss (IL) & Capital Efficiency Calculus
- **Impermanent Loss Klasik (Uniswap v2 / CPMM)**:
  Untuk rasio perubahan harga $k = \frac{P_1}{P_0}$:
  $$V_{\text{hold}}(k) = \frac{V_0}{2}(1 + k), \quad V_{\text{pool}}(k) = V_0 \sqrt{k}$$
  $$IL_{v2}(k) = \frac{V_{\text{pool}} - V_{\text{hold}}}{V_{\text{hold}}} = \frac{2\sqrt{k}}{1+k} - 1$$

- **Impermanent Loss Terpusat (Uniswap v3 Amplified IL)**:
  - Faktor Pengali Efisiensi Modal (*Capital Efficiency Leverage* $\eta$):
    $$\eta = \frac{L_{v3}}{L_{v2}} = \frac{1}{1 - \sqrt{P_a / P_b}} \quad (\text{untuk rentang simetris di sekitar } P_0)$$
  - Di dalam rentang $[P_a, P_b]$, kurva IL teramplifikasi secara linier oleh faktor $\eta$.
  - Di luar rentang, posisi berhenti mengumpulkan fee transaksi dan menjadi posisi *naked hold* dari aset yang terdepresiasi (*adverse selection* maksimal).

- **Hedging & Volatility Strategies**:
  - Delta Hedging: Membuka short position pada perpetual futures sebesar $\Delta = \frac{\partial V_{\text{pool}}}{\partial P}$.
  - Squeeth / Power Perpetual: Replikasi opsi gamma kuadratik untuk mengimbangi kelengkungan (*negative gamma*) dari AMM LP.

---

### 3. Flash Loan Atomic Arbitrage Architecture
- **Invarian Eksekusi Atomik Tunggal**:
  Flash loan memungkinkan peminjaman aset tanpa agunan (*uncollateralized*) selama pokok pinjaman beserta fee dikembalikan dalam blok/transaksi yang sama.
  $$\Pi_{\text{net}} = \Delta x_{\text{out}} - \Delta x_{\text{in}}(1 + f_{\text{fl}}) - \text{GasCost} - \text{Bribe} > 0$$
  Jika $\Pi_{\text{net}} \le 0 \implies \text{revert()}$ seluruh mutasi state dibatalkan tanpa kehilangan pokok.

- **Optimasi Ukuran Input Arbitrase Lintas-Pool ($\Delta x^*$)**:
  Untuk dua pool konstan produk ($x_A \cdot y_A = k_A$, $x_B \cdot y_B = k_B$) dengan effective fee $\gamma_A = 1 - f_A$ dan $\gamma_B = 1 - f_B$:
  $$\Delta x^* = \frac{\sqrt{x_A \cdot y_A \cdot x_B \cdot y_B \cdot \gamma_A \cdot \gamma_B} - x_A \cdot x_B}{\gamma_A \cdot x_B + y_A}$$
  Mengeksekusi lebih besar dari $\Delta x^*$ menyebabkan *price impact* melampaui margin keuntungan spread (*over-trading drag*).

---

### 4. Toxic MEV Dynamics: Sandwich Attacks & JIT Liquidity
- **Anatomi Serangan Sandwich**:
  1. **Frontrun ($Tx_1$)**: Searcher mendeteksi transaksi korban ($Tx_v$) di public mempool yang membeli Token Y dengan toleransi slippage $S_{\text{tol}}$. Searcher membeli Token Y terlebih dahulu, menaikkan harga spot ke batas maksimum toleransi korban:
     $$P_{\text{spot}} \to P_{\text{victim\_max}} = P_0 \cdot (1 + S_{\text{tol}})$$
  2. **Victim Execution ($Tx_v$)**: Transaksi korban dieksekusi pada harga terburuk yang diizinkan (`amountOutMin`).
  3. **Backrun ($Tx_2$)**: Searcher menjual kembali Token Y yang diperoleh pada $Tx_1$ ke pool yang kini memiliki cadangan Token X lebih tinggi, mengantongi selisih nilai murni (*extracted value*).

- **Just-In-Time (JIT) Liquidity Exploitation**:
  Searcher menyuntikkan likuiditas v3 ultra-terpusat tepat pada tick transaksi korban satu posisi sebelum $Tx_v$, menyerap seluruh fee perdagangan, dan membakar (*burn*) likuiditas tersebut pada posisi tepat setelah $Tx_v$ dalam bundel blok yang sama.

- **Pertahanan & Mitigasi Pengguna**:
  - *Dynamic Adaptive Slippage*: Membatasi toleransi slippage ke tingkat mikro (misal 0.05% - 0.10%) berdasarkan volatilitas blok.
  - *Private Mempool Routing*: Menghindari mempool publik p2p via Flashbots Protect atau Jito Block Engine.
  - *Batch Auctions & CoW Protocol*: Mencocokkan order secara off-chain dengan *uniform clearing price* yang mengeliminasi prioritas urutan miner (*frontrun immune*).

---

### 5. Searcher-Builder Infrastructure: Flashbots & Jito Relays
- **Proposer-Builder Separation (PBS) & Bundle Architecture**:
  Pemisahan peran antara pencari MEV (*Searchers*), penyusun blok (*Block Builders*), dan validator (*Proposers*):
  $$\text{Bundle} = [Tx_1, Tx_v, Tx_2] \quad \text{atau} \quad [Tx_{\text{arb}}, Tx_{\text{bribe}}]$$
  - **Atomisitas Bundel**: Semua transaksi dalam bundel dieksekusi secara berurutan tanpa ada transaksi luar yang menyela (*atomic interleaving*). Jika salah satu transaksi revert, seluruh bundel dibatalkan tanpa mengekspos gas failure on-chain.

- **Bribe & Coinbase Payment Optimization**:
  Searcher membayar suap langsung ke `block.coinbase` atau tip account Jito:
  $$\text{Bribe} = \alpha \cdot (\text{Gross Revenue} - \text{Gas Cost}), \quad \alpha \in [0.85, 0.99]$$
  Dalam lelang MEV kompetitif, pembagian tip $\alpha \to 1.0$ mendekati ekuilibrium Nash di mana efisiensi latensi dan algoritma menentukan pemenang.

---

## 💻 Zero-Dependency Stdlib Python Implementation & Self-Check

```python
"""
Neuron N048: DeFi Liquidity Engineering & Cross-Chain MEV Protection Simulator.
Standard library only. Fully deterministic verification suite.
"""

import math
from typing import Dict, List, Tuple, Optional


class UniswapV3Math:
    """Concentrated Liquidity Math & Tick Geometry (Uniswap v3 Invariants)."""

    @staticmethod
    def tick_to_price(tick: int) -> float:
        """Converts integer tick index to price P = 1.0001^tick."""
        return 1.0001 ** tick

    @staticmethod
    def price_to_tick(price: float) -> int:
        """Converts price P to discrete integer tick index."""
        if price <= 0:
            raise ValueError("Price must be positive")
        return int(math.floor(math.log(price, 1.0001)))

    @staticmethod
    def get_liquidity_for_amounts(
        sqrt_p: float,
        sqrt_pa: float,
        sqrt_pb: float,
        amount0: float,
        amount1: float
    ) -> float:
        """Calculates maximum liquidity L providable given asset reserves and range."""
        if sqrt_pa > sqrt_pb:
            sqrt_pa, sqrt_pb = sqrt_pb, sqrt_pa

        if sqrt_p <= sqrt_pa:
            # 100% Token 0
            return amount0 * (sqrt_pa * sqrt_pb) / (sqrt_pb - sqrt_pa)
        elif sqrt_p < sqrt_pb:
            # Dual Token 0 & Token 1 active liquidity
            l0 = amount0 * (sqrt_p * sqrt_pb) / (sqrt_pb - sqrt_p)
            l1 = amount1 / (sqrt_p - sqrt_pa)
            return min(l0, l1)
        else:
            # 100% Token 1
            return amount1 / (sqrt_pb - sqrt_pa)

    @staticmethod
    def get_amounts_for_liquidity(
        sqrt_p: float,
        sqrt_pa: float,
        sqrt_pb: float,
        liquidity: float
    ) -> Tuple[float, float]:
        """Calculates token0 (x) and token1 (y) reserves for a given liquidity L."""
        if sqrt_pa > sqrt_pb:
            sqrt_pa, sqrt_pb = sqrt_pb, sqrt_pa

        if sqrt_p <= sqrt_pa:
            amount0 = liquidity * (sqrt_pb - sqrt_pa) / (sqrt_pa * sqrt_pb)
            amount1 = 0.0
        elif sqrt_p < sqrt_pb:
            amount0 = liquidity * (sqrt_pb - sqrt_p) / (sqrt_p * sqrt_pb)
            amount1 = liquidity * (sqrt_p - sqrt_pa)
        else:
            amount0 = 0.0
            amount1 = liquidity * (sqrt_pb - sqrt_pa)
        return amount0, amount1


class ImpermanentLossCalculator:
    """Calculates Impermanent Loss & Capital Efficiency Multipliers."""

    @staticmethod
    def il_v2(price_ratio: float) -> float:
        """
        Standard Uniswap v2 Impermanent Loss formula.
        price_ratio k = P_final / P_initial.
        Returns IL as a negative decimal (e.g., -0.0571 for -5.71%).
        """
        k = price_ratio
        if k <= 0:
            return -1.0
        return (2.0 * math.sqrt(k)) / (1.0 + k) - 1.0

    @staticmethod
    def il_v3(p_initial: float, p_final: float, pa: float, pb: float) -> float:
        """
        Calculates exact Uniswap v3 concentrated LP impermanent loss
        relative to holding the initial asset basket (HODL baseline).
        """
        sqrt_p0 = math.sqrt(p_initial)
        sqrt_p1 = math.sqrt(p_final)
        sqrt_pa = math.sqrt(pa)
        sqrt_pb = math.sqrt(pb)

        L = 1.0
        x0, y0 = UniswapV3Math.get_amounts_for_liquidity(sqrt_p0, sqrt_pa, sqrt_pb, L)
        v_hold = x0 * p_final + y0

        x1, y1 = UniswapV3Math.get_amounts_for_liquidity(sqrt_p1, sqrt_pa, sqrt_pb, L)
        v_pool = x1 * p_final + y1

        if v_hold == 0:
            return 0.0
        return (v_pool - v_hold) / v_hold

    @staticmethod
    def capital_efficiency(pa: float, pb: float) -> float:
        """Calculates capital efficiency multiplier of v3 concentrated position vs v2."""
        return 1.0 / (1.0 - math.sqrt(pa / pb))


class CPMMConstantProductPool:
    """Constant Product Market Maker (x * y = k) Pool Simulator."""

    def __init__(self, reserve_x: float, reserve_y: float, fee: float = 0.003):
        self.rx = reserve_x
        self.ry = reserve_y
        self.fee = fee

    @property
    def spot_price_y_per_x(self) -> float:
        return self.ry / self.rx

    def get_amount_out(self, amount_in: float, zero_for_one: bool) -> float:
        """Calculates token output given input and swap fee."""
        gamma = 1.0 - self.fee
        if zero_for_one:  # Swap Token X for Token Y
            dx_eff = amount_in * gamma
            return (self.ry * dx_eff) / (self.rx + dx_eff)
        else:  # Swap Token Y for Token X
            dy_eff = amount_in * gamma
            return (self.rx * dy_eff) / (self.ry + dy_eff)

    def execute_swap(self, amount_in: float, zero_for_one: bool) -> float:
        """Executes swap on pool and mutates state reserves."""
        out = self.get_amount_out(amount_in, zero_for_one)
        if zero_for_one:
            self.rx += amount_in
            self.ry -= out
        else:
            self.ry += amount_in
            self.rx -= out
        return out


class FlashLoanArbitrageEngine:
    """Flash Loan Atomic Arbitrage Engine with optimal size determination."""

    @staticmethod
    def optimize_arbitrage_input(
        pool_buy_y: CPMMConstantProductPool,
        pool_sell_y: CPMMConstantProductPool,
        flash_loan_fee: float = 0.0009
    ) -> Tuple[float, float]:
        """
        Determines optimal borrow amount (Token X) to buy Token Y cheap on pool_buy_y
        and sell Token Y high on pool_sell_y.
        Returns: (optimal_borrow_x, net_profit_x)
        """
        gamma_a = 1.0 - pool_buy_y.fee
        gamma_b = 1.0 - pool_sell_y.fee

        best_profit = -float("inf")
        best_dx = 0.0

        # Discrete line search across bounded search space
        max_search = pool_buy_y.rx * 0.5
        steps = 500
        step_size = max_search / steps

        for i in range(1, steps + 1):
            dx = i * step_size
            # Step 1: Swap X -> Y on pool_buy_y
            dx_eff = dx * gamma_a
            dy = (pool_buy_y.ry * dx_eff) / (pool_buy_y.rx + dx_eff)

            # Step 2: Swap Y -> X on pool_sell_y
            dy_eff = dy * gamma_b
            dx_out = (pool_sell_y.rx * dy_eff) / (pool_sell_y.ry + dy_eff)

            # Flash loan repayment invariant
            repayment = dx * (1.0 + flash_loan_fee)
            net_profit = dx_out - repayment

            if net_profit > best_profit:
                best_profit = net_profit
                best_dx = dx

        return best_dx, best_profit


class SandwichAttackEngine:
    """Simulates Toxic MEV Sandwich Attack and Evaluates Slippage Defenses."""

    @staticmethod
    def simulate_sandwich(
        pool: CPMMConstantProductPool,
        victim_in_x: float,
        slippage_tolerance: float,
        frontrun_in_x: float
    ) -> Dict[str, any]:
        """
        Executes:
        1. Expected victim output without attack.
        2. Frontrun swap: Attacker buys Token Y with frontrun_in_x.
        3. Victim swap: Executes on manipulated pool. Reverts if output < amountOutMin.
        4. Backrun swap: Attacker dumps acquired Token Y back for Token X.
        """
        expected_victim_y = pool.get_amount_out(victim_in_x, zero_for_one=True)
        min_victim_y = expected_victim_y * (1.0 - slippage_tolerance)

        sim_pool = CPMMConstantProductPool(pool.rx, pool.ry, pool.fee)

        # 1. Frontrun
        attacker_y = sim_pool.execute_swap(frontrun_in_x, zero_for_one=True)

        # 2. Victim execution
        victim_actual_y = sim_pool.execute_swap(victim_in_x, zero_for_one=True)
        if victim_actual_y < min_victim_y:
            # Transaction reverted on-chain
            return {
                "success": False,
                "victim_reverted": True,
                "attacker_profit_x": -frontrun_in_x * sim_pool.fee,
                "victim_slippage_pct": 0.0
            }

        # 3. Backrun
        attacker_recovered_x = sim_pool.execute_swap(attacker_y, zero_for_one=False)
        attacker_profit = attacker_recovered_x - frontrun_in_x
        victim_slippage = (expected_victim_y - victim_actual_y) / expected_victim_y

        return {
            "success": attacker_profit > 0,
            "victim_reverted": False,
            "attacker_profit_x": attacker_profit,
            "victim_slippage_pct": victim_slippage * 100.0,
            "victim_received_y": victim_actual_y,
            "victim_min_acceptable_y": min_victim_y
        }


class FlashbotsBundleRelay:
    """Simulates Searcher-to-Builder MEV Relay (Flashbots / Jito Bundles)."""

    def __init__(self, builder_tip_share: float = 0.90):
        self.builder_tip_share = builder_tip_share

    def construct_bundle(
        self,
        target_tx_hash: str,
        arbitrage_revenue: float,
        gas_cost: float,
        is_private_mempool: bool = True
    ) -> Dict[str, any]:
        """Constructs an atomic searcher bundle with builder bribe and revert protection."""
        gross_profit = arbitrage_revenue - gas_cost
        if gross_profit <= 0:
            return {
                "status": "ABORTED_UNPROFITABLE",
                "bribe": 0.0,
                "net_searcher_profit": 0.0
            }

        bribe_amount = gross_profit * self.builder_tip_share
        net_profit = gross_profit - bribe_amount

        return {
            "status": "INCLUDED_IN_BLOCK",
            "private_channel": is_private_mempool,
            "target_tx": target_tx_hash,
            "bundle_txs": [
                f"tx_arb_{target_tx_hash[:6]}",
                f"tx_coinbase_bribe_{bribe_amount:.4f}"
            ],
            "bribe_to_builder": bribe_amount,
            "net_searcher_profit": net_profit,
            "revert_protection": True
        }


# Self-Check Verification Suite
def run_neuron_tests():
    # 1. Test Uniswap v3 Tick Math & Liquidity Invariants
    p_current = 2000.0
    p_lower = 1500.0
    p_upper = 2500.0
    sqrt_p = math.sqrt(p_current)
    sqrt_pa = math.sqrt(p_lower)
    sqrt_pb = math.sqrt(p_upper)

    amount0_in = 1.0  # 1 ETH
    amount1_in = 2000.0  # 2000 USDC
    L = UniswapV3Math.get_liquidity_for_amounts(sqrt_p, sqrt_pa, sqrt_pb, amount0_in, amount1_in)
    assert L > 0, "Liquidity calculation failed"

    a0, a1 = UniswapV3Math.get_amounts_for_liquidity(sqrt_p, sqrt_pa, sqrt_pb, L)
    assert a0 <= amount0_in + 1e-9, "Token 0 amount overflow"
    assert a1 <= amount1_in + 1e-9, "Token 1 amount overflow"

    tick = UniswapV3Math.price_to_tick(p_current)
    recovered_p = UniswapV3Math.tick_to_price(tick)
    assert abs(recovered_p - p_current) / p_current < 0.0001, "Tick conversion precision error"

    # 2. Test Impermanent Loss & Leverage Multiplier
    il_v2_50pct = ImpermanentLossCalculator.il_v2(1.5)  # +50% price change in v2
    assert -0.025 < il_v2_50pct < -0.015, f"V2 IL calculation out of expected range: {il_v2_50pct}"

    il_v3_50pct = ImpermanentLossCalculator.il_v3(2000.0, 3000.0, 1500.0, 2500.0)
    assert il_v3_50pct < il_v2_50pct, "V3 concentrated IL must be more severe outside range"

    cap_eff = ImpermanentLossCalculator.capital_efficiency(1500.0, 2500.0)
    assert cap_eff > 1.0, "Capital efficiency multiplier must exceed 1.0"

    # 3. Test Flash Loan Arbitrage Engine
    # Pool A: 1000 X, 2200000 Y (Price Y/X = 2200, 1 X buys 2200 Y -> Y is cheaper)
    # Pool B: 1000 X, 2000000 Y (Price Y/X = 2000, 1 X buys 2000 Y -> Y is more expensive)
    pool_a = CPMMConstantProductPool(1000.0, 2200000.0, 0.003)
    pool_b = CPMMConstantProductPool(1000.0, 2000000.0, 0.003)

    opt_borrow, net_prof = FlashLoanArbitrageEngine.optimize_arbitrage_input(pool_a, pool_b, 0.0009)
    assert opt_borrow > 0, "Should identify profitable flash loan borrow size"
    assert net_prof > 0, f"Net arbitrage profit must be positive, got {net_prof}"

    # 4. Test Toxic Sandwich Attack & Slippage Defense
    pool_target = CPMMConstantProductPool(1000.0, 2000000.0, 0.003)
    victim_amount = 10.0  # 10 ETH buy
    loose_slippage = 0.02  # 2% slippage tolerance

    # Sandwich succeeds on loose slippage
    res_loose = SandwichAttackEngine.simulate_sandwich(pool_target, victim_amount, loose_slippage, frontrun_in_x=5.0)
    assert res_loose["success"] is True, "Sandwich should extract MEV with loose slippage"
    assert res_loose["attacker_profit_x"] > 0, "Attacker should gain profit"
    assert res_loose["victim_slippage_pct"] > 0, "Victim should suffer price slippage"

    # Sandwich fails / reverts on tight adaptive slippage (0.05%)
    res_tight = SandwichAttackEngine.simulate_sandwich(pool_target, victim_amount, 0.0005, frontrun_in_x=5.0)
    assert res_tight["victim_reverted"] is True or res_tight["success"] is False, "Tight slippage must protect victim"

    # 5. Test Flashbots Relay & Builder Bribe
    relay = FlashbotsBundleRelay(builder_tip_share=0.90)
    bundle = relay.construct_bundle("0xdeadbeef12345678", arbitrage_revenue=1.5, gas_cost=0.1, is_private_mempool=True)
    assert bundle["status"] == "INCLUDED_IN_BLOCK"
    assert math.isclose(bundle["bribe_to_builder"], 1.4 * 0.90, rel_tol=1e-5)
    assert math.isclose(bundle["net_searcher_profit"], 1.4 * 0.10, rel_tol=1e-5)
    assert bundle["revert_protection"] is True

    print("  [OK] Neuron N048 Invariants Verified: Uniswap v3 Math, IL Calculus, Flash Loan Arb, Sandwich Defense, & Flashbots Relay.")


if __name__ == "__main__":
    run_neuron_tests()
```

---

## 🛡️ Invariant Ringkas (Operational Rules)
1. **Concentrated Capital Efficiency Tradeoff**: Uniswap v3 melipatgandakan fee income sebesar $\eta = 1/(1-\sqrt{P_a/P_b})$, namun mempercepat risiko *impermanent loss* dan *out-of-range abandonment* secara proporsional.
2. **Strict Flash Loan Invariant**: Seluruh eksekusi arbitrase pinjaman kilat wajib memvalidasi `balanceAfter >= balanceBefore + fee + minProfit` dalam satu transaksi atomik untuk menjamin *zero capital risk*.
3. **Private Mempool Default for Large Swaps**: Seluruh transaksi berukuran signifikan wajib dirutekan melalui RPC privat (Flashbots Protect / Jito Relay) guna mengeliminasi eksploitasi *sandwich attack* dan *toxic frontrunning* di mempool publik.
4. **Dynamic Adaptive Slippage**: Tetapkan `amountOutMin` berbasis kedalaman likuiditas dan volatilitas tick terkini, bukan persentase statis.
