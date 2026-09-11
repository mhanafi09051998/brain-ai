---
name: meteora-dlmm-automated-market-making
description: Production-grade automated market making (AMM) and dynamic liquidity provision for Meteora DLMM on Solana, covering bin distribution algorithms, dynamic fee harvesting, out-of-range rebalancing, and emergency liquidity protection.
---

# Meteora DLMM Automated Market Making (AMM) Handbook

High-precision, quantitative liquidity provision and automated execution invariants for Meteora Dynamic Liquidity Market Maker (DLMM) pools on Solana.

---

## 1. Mathematical Foundation & Discrete Bin Mechanics

Meteora DLMM organizes liquidity into discrete price bins with zero slippage inside each individual bin.

```
       Token X Liquidity                Active Bin                 Token Y Liquidity
     [100% Token X Reserve]          [Token X + Token Y]        [100% Token Y Reserve]
 --------------------------------------------------------------------------------------
 ... | Bin (i-2) | Bin (i-1) |          Bin (i)          | Bin (i+1) | Bin (i+2) | ...
 --------------------------------------------------------------------------------------
           <-- Lower Prices                                       Higher Prices -->
```

### A. Discrete Bin Price Invariant
$$P(i) = \left(1 + \frac{\text{bin\_step}}{10000}\right)^i$$
* $\text{bin\_step}$: Integer in basis points ($1\text{ bp} = 0.01\%$).
* Price at bin $i$ grows exponentially with base $(1 + \text{bin\_step}/10000)$.
* Conversion between human price $P_{\text{ui}}$ and integer bin index $i$:
  $$i = \text{round}\left( \frac{\ln(P_{\text{ui}} \times 10^{\text{dec}_Y - \text{dec}_X})}{\ln(1 + \text{bin\_step}/10000)} \right)$$

---

## 2. Liquidity Distribution Strategies

Selecting the optimal shape depends on the market regime and token volatility profile:

```
    [Spot / Uniform]             [Curve / Gaussian]              [Bid-Ask / Volatile]
        ┌─────┐                        ┌───┐                     ┌───┐         ┌───┐
     ┌──┴─────┴──┐                   ┌─┴───┴─┐                   │   │ ┌─────┐ │   │
  ┌──┴───────────┴──┐             ┌──┴───────┴──┐                │   └─┴─────┴─┘   │
  └─── Active Bin ──┘             └── Active Bin ──┘             └── Active Bin ───┘
(Ranging / Sideways)           (Pegged / High TVL Memes)       (High Volatility Breakouts)
```

| Strategy Preset | Bin Distribution Shape | Ideal Market Regime | Capital Efficiency |
| :--- | :--- | :--- | :--- |
| **Spot** | Uniform flat distribution across $[i_{\text{active}} - N, i_{\text{active}} + N]$ | Sideways consolidation / Ranging | Moderate ($5\text{x} - 20\text{x}$) |
| **Curve** | Gaussian normal distribution centered on $i_{\text{active}}$ | Correlated pairs / High conviction hold | Maximum ($50\text{x} - 500\text{x}$) |
| **Bid-Ask** | Inverted parabola (deep liquidity at outer wings) | Wildly volatile breakouts, sniper capture | Dynamic Fee Optimizer |
| **Single-Sided Ask** | 100% Token X in bins $[i_{\text{active}} + 1, i_{\text{active}} + M]$ | Automated DCA take-profit on pump | High Yield Exit |
| **Single-Sided Bid** | 100% Token Y (SOL/USDC) in $[i_{\text{active}} - M, i_{\text{active}} - 1]$ | Buy-the-dip DCA limit accumulation | Deep Fill Discount |

---

## 3. Dynamic Fee Capture & Volatility Accumulator

Meteora calculates dynamic swap fees using an on-chain volatility accumulator $v_a$:

$$f_{\text{swap}} = f_{\text{base}} + A \cdot \left(\frac{v_a \cdot \text{bin\_step}}{10000}\right)^2$$

* **Surge Capture**: During high-frequency volatility (e.g., meme breakout or dump), $f_{\text{swap}}$ surges dynamically up to $10\% - 25\%$, compensating LPs for impermanent loss.
* **Fee Extraction Rule**: LP fees must be harvested periodically or auto-compounded when:
  $$\text{Unclaimed Fees (USD)} > \text{Network Tx Gas Cost} \times 10$$

---

## 4. Production SDK Integration (@meteora-ag/dlmm)

```typescript
import DLMM, { StrategyType } from "@meteora-ag/dlmm";
import { Connection, Keypair, PublicKey, sendAndConfirmTransaction } from "@solana/web3.js";
import BN from "bn.js";

async function openOptimizedDlmmPosition(
  connection: Connection,
  keypair: Keypair,
  poolAddress: PublicKey,
  totalXAmount: BN,
  totalYAmount: BN,
  binRangeDelta: number = 30 // 30 bins below and above active bin
) {
  const dlmmPool = await DLMM.create(connection, poolAddress);
  const activeBin = await dlmmPool.getActiveBin();

  const minBinId = activeBin.binId - binRangeDelta;
  const maxBinId = activeBin.binId + binRangeDelta;

  const newPositionKeypair = Keypair.generate();

  // Create position with Spot distribution strategy
  const createPositionTx = await dlmmPool.initializePositionAndAddLiquidityByStrategy({
    positionPubKey: newPositionKeypair.publicKey,
    user: keypair.publicKey,
    totalXAmount,
    totalYAmount,
    strategy: {
      maxBinId,
      minBinId,
      strategyType: StrategyType.SpotBalanced,
    },
  });

  return await sendAndConfirmTransaction(connection, createPositionTx, [keypair, newPositionKeypair]);
}
```

---

## 5. Out-of-Range Auto-Rebalancing Invariant

When price drifts entirely outside the position's bin range, liquidity becomes 100% single-sided and stops generating swap fees.

```
                   [Price Drifts Out of Active Bins]
                                  |
               [Trigger: (Current Bin < Min) or (Current Bin > Max)]
                                  |
               [Action: Claim All Fees + Remove Liquidity]
                                  |
               [Re-quote Active Bin & Re-center Bins around New Price]
                                  |
               [Atomic Re-deposit with Safe Slippage Invariant]
```

### Rebalancing Invariants
1. **Drift Threshold**: Do NOT rebalance on transient 1-second price wicks. Rebalance only when price stays out of range for $>T_{\text{drift}}$ (e.g., 30–60 seconds).
2. **Fee-to-IL Hurdle**: Rebalancing crystallizes impermanent loss. Only execute rebalance if:
   $$\sum \text{Earned Fees} > \Delta \text{Impermanent Loss} + \text{Slippage Cost}$$

---

## 6. Atomic Emergency Liquidity Extraction (Dump Circuit Breaker)

If on-chain forensic monitors detect an insider wallet dump or massive sell wall:

```typescript
async function emergencyDrainDlmmPosition(
  dlmmPool: DLMM,
  positionPubKey: PublicKey,
  userKeypair: Keypair
) {
  // Remove 100% of remaining liquidity and claim accrued fees in a single atomic transaction
  const removeLiquidityTx = await dlmmPool.removeLiquidity({
    position: positionPubKey,
    user: userKeypair.publicKey,
    binIds: [], // Empty array = remove all active bins
    bps: new BN(10_000), // 100% of position liquidity
    shouldClaimFee: true,
  });

  // Execute via Jito MEV tip bundle for immediate sub-second block inclusion
  return await submitViaJitoBundle(removeLiquidityTx, userKeypair);
}
```

---

## 7. Operational Safety Checklist
- [ ] **Pool Step Check**: Verified pool `bin_step` matches the expected volatility (e.g., 100–200 bps for volatile memecoins, 1–10 bps for stable pairs).
- [ ] **Dynamic Fee Parameter Check**: Verified `base_fee_bps` and `variable_fee_control` are active.
- [ ] **Automated Fee Compounding**: Set cron schedule for fee harvesting.
- [ ] **Stop-Loss Bin Level**: Configured automated withdrawal trigger if token dumps past safety threshold bin.
