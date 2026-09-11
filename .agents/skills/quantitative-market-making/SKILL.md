---
name: quantitative-market-making
description: Comprehensive quantitative market making and concentrated liquidity engineering guide covering DLMM mechanics, bin step mathematics, capital efficiency, inventory risk & LVR management, automated volatility-aware rebalancing, Jupiter routing execution, and deterministic PnL accounting.
---

# Quantitative Market Making & Concentrated Liquidity Engineering Handbook

High-precision, empirical mathematical models, algorithmic execution strategies, and on-chain architecture for quantitative market making on concentrated liquidity protocols (Meteora DLMM, Raydium CLMM, Orca Whirlpools).

---

## 1. Concentrated Liquidity & DLMM Mechanics

### A. Discrete Bin Step Mathematics

Meteora DLMM discretizes continuous price space into distinct, sequential price bins. Each bin corresponds to an exact, invariant price level determined by the pool's configured `bin_step`.

#### 1. Price from Bin ID Invariant
$$P(i) = \left(1 + \frac{\text{bin\_step}}{10000}\right)^i \times 10^{\text{decimals}_X - \text{decimals}_Y}$$

Where:
* $i \in \mathbb{Z}$: Signed integer bin index (positive or negative).
* $\text{bin\_step} \in \mathbb{N}^+$: Basis point step size ($1 \text{ bp} = 0.01\% = 10^{-4}$).
* $\text{decimals}_X, \text{decimals}_Y$: Base token ($X$) and quote token ($Y$) native decimal places.
* $P(i)$: Price of 1 base unit of token $X$ denominated in token $Y$.

#### 2. Bin ID from Target Price
$$i(P) = \left\lfloor \frac{\ln\left(P \times 10^{\text{decimals}_Y - \text{decimals}_X}\right)}{\ln\left(1 + \frac{\text{bin\_step}}{10000}\right)} \right\rceil$$

Where $\lfloor \cdot \rceil$ denotes round-to-nearest integer.

```typescript
export interface PoolConfig {
  binStep: number;        // e.g. 10 bps (0.10%) -> binStep = 10
  decimalsX: number;      // Base token decimals (e.g. SOL = 9)
  decimalsY: number;      // Quote token decimals (e.g. USDC = 6)
}

export function getPriceFromBinId(binId: number, config: PoolConfig): number {
  const stepRatio = 1 + config.binStep / 10_000;
  const rawPrice = Math.pow(stepRatio, binId);
  const decimalFactor = Math.pow(10, config.decimalsX - config.decimalsY);
  return rawPrice * decimalFactor;
}

export function getBinIdFromPrice(price: number, config: PoolConfig): number {
  const stepRatio = 1 + config.binStep / 10_000;
  const decimalFactor = Math.pow(10, config.decimalsY - config.decimalsX);
  const rawPrice = price * decimalFactor;
  return Math.round(Math.log(rawPrice) / Math.log(stepRatio));
}
```

---

### B. Active Bin Tracking & Reserve Composition

Inside a DLMM pool, all trading activity occurs strictly against the **active bin** ($i_{\text{active}}$).

```
                      Price Increasing --->
  [ 100% Token X ] ... [ 100% X ] | [ Mixed X + Y ] | [ 100% Y ] ... [ 100% Token Y ]
      Bin (i - 2)        Bin (i - 1)    Active Bin (i)    Bin (i + 1)      Bin (i + 2)
```

#### Composition Rules:
1. **Bins Below Active Bin ($i < i_{\text{active}}$)**:
   * Holds $100\%$ Token X (Base token).
   * Token Y reserves = $0$.
   * As price falls below bin $i$, traders bought all token Y and deposited token X.
2. **Active Bin ($i = i_{\text{active}}$)**:
   * Holds both Token X and Token Y simultaneously.
   * Total value inside active bin: $V(i) = R_X(i) \cdot P(i) + R_Y(i)$.
   * Swaps within active bin execute with **zero price slippage** at the constant rate $P(i_{\text{active}})$.
3. **Bins Above Active Bin ($i > i_{\text{active}}$)**:
   * Holds $100\%$ Token Y (Quote token).
   * Token X reserves = $0$.
   * As price rises above bin $i$, traders bought all token X and deposited token Y.

#### Liquidity Distribution Topologies:
* **Spot (Uniform Distribution)**: $L_i = \text{constant}$ across $[i_{\text{min}}, i_{\text{max}}]$. Ideal for stable ranging markets and range-bound volatility.
* **Curve (Gaussian Concentration)**:
  $$L_i = L_0 \cdot \exp\left(-\frac{(i - i_{\text{active}})^2}{2\sigma^2}\right)$$
  Concentrates maximum liquidity within $\pm 2\sigma$ bins of the market price. Maximum capital efficiency for mean-reverting pairs.
* **Bid-Ask (Volatility Dampened)**:
  Asymmetric capital allocation where bid depth ($i < i_{\text{active}}$) and ask depth ($i > i_{\text{active}}$) are scaled by directional inventory risk.

---

### C. Concentrated Capital Efficiency vs Traditional CPMM

In a standard Constant Product Market Maker (CPMM $xy = k$), capital is distributed across $P \in (0, \infty)$. In concentrated liquidity / DLMM, capital is concentrated within a bounded interval $[P_a, P_b]$.

#### Capital Efficiency Multiplier ($\eta$):
$$\eta = \frac{1}{1 - \sqrt{\frac{P_a}{P_b}}}$$

For a symmetric range around current price $P_0$ spanning $\pm r\%$ ($P_a = P_0(1 - r)$, $P_b = P_0(1 + r)$):
$$\eta(r) = \frac{1}{1 - \sqrt{\frac{1 - r}{1 + r}}}$$

| Range Span ($\pm r$) | Price Bounds Ratio ($P_b / P_a$) | Capital Efficiency Multiplier ($\eta$) | Required Capital vs CPMM |
| :--- | :--- | :--- | :--- |
| $\pm 0.50\%$ | $1.010$ | **$201.0\times$** | $0.49\%$ |
| $\pm 1.00\%$ | $1.020$ | **$100.5\times$** | $0.99\%$ |
| $\pm 2.00\%$ | $1.041$ | **$50.5\times$** | $1.98\%$ |
| $\pm 5.00\%$ | $1.105$ | **$20.5\times$** | $4.87\%$ |
| $\pm 10.00\%$ | $1.222$ | **$10.5\times$** | $9.52\%$ |
| $\pm 20.00\%$ | $1.500$ | **$5.45\times$** | $18.35\%$ |

$$\text{Daily Fee Yield}_{\text{Concentrated}} \approx \eta \times \text{Daily Fee Yield}_{\text{CPMM}}$$

*High efficiency amplifies fee yield by $\eta$, but simultaneously amplifies rate of Impermanent Loss / Inventory Divergence by $\eta$.*

---

## 2. Inventory Risk & Impermanent Loss Management

### A. Concentrated Impermanent Loss Formulation

When price moves from entry price $P_0$ to current price $P_1$, the position value $V_{\text{LP}}(P_1)$ relative to holding the initial assets $V_{\text{HODL}}(P_1)$ defines Impermanent Loss ($\text{IL}$):

$$\text{IL}(k) = \frac{V_{\text{LP}}(P_1) - V_{\text{HODL}}(P_1)}{V_{\text{HODL}}(P_1)}$$

Where $k = \frac{P_1}{P_0}$.

For a concentrated liquidity position bounded in $[P_a, P_b]$ with $k_a = \frac{P_a}{P_0} < 1$ and $k_b = \frac{P_b}{P_0} > 1$:

#### 1. Inside Range ($P_a \le P_1 \le P_b$):
$$V_{\text{LP}}(P_1) = L \cdot \left( 2\sqrt{P_1} - \sqrt{P_a} - \frac{P_1}{\sqrt{P_b}} \right)$$
$$V_{\text{HODL}}(P_1) = L \cdot \left( \sqrt{P_0} - \sqrt{P_a} + P_1 \left( \frac{1}{\sqrt{P_0}} - \frac{1}{\sqrt{P_b}} \right) \right)$$
$$\text{IL}_{\text{conc}}(k) = \frac{2\sqrt{k} - \sqrt{k_a} - \frac{k}{\sqrt{k_b}} - \left( 1 - \sqrt{k_a} + k \left( 1 - \frac{1}{\sqrt{k_b}} \right) \right)}{1 - \sqrt{k_a} + k \left( 1 - \frac{1}{\sqrt{k_b}} \right)}$$

#### 2. Fully Out-of-Range ($P_1 > P_b$ or $P_1 < P_a$):
* If $P_1 \ge P_b$: 100% Token Y. Capital ceases earning fees; maximum upside participation capped at $P_b$.
* If $P_1 \le P_a$: 100% Token X. Capital holds depreciating asset without fee generation.

---

### B. Loss-Versus-Rebalancing (LVR) & Toxic Flow Separation

LVR represents the theoretical cost of offering liquidity to informed arbitrageurs who extract value before pool prices update.

$$\text{d}(\text{LVR}_t) = \frac{\sigma^2}{8} \cdot \eta \cdot V_t \, \text{d}t$$

Where:
* $\sigma$: Instantaneous asset volatility.
* $\eta$: Capital concentration factor.
* $V_t$: Mark-to-market position value.

#### Empirical Break-Even Invariant:
A concentrated market-making position is profitable if and only if:

$$\sum_{t=0}^T \text{FeeRevenue}_t > \int_0^T \text{d}(\text{LVR}_t) + \text{Gas}_{\text{tx}} + \text{SwapSlippage}_{\text{rebalance}}$$

$$\text{Required Minimum Fee Rate} \ge \frac{\sigma^2}{8} \cdot \frac{\text{Pool Volume}_{\text{Uninformed}}}{\text{Pool Volume}_{\text{Total}}}$$

---

### C. Inventory Skewing (Avellaneda-Stoikov Adaptation)

To avoid paying taker swap fees on rebalances, shift the center of your bin distribution relative to the market mid-price based on current inventory imbalance:

$$q = \frac{V_X - V_Y}{V_X + V_Y} \in [-1, 1]$$

#### Reservation Price / Target Mid-Bin Shift:
$$\Delta i_{\text{skew}} = -\text{round}\left(\kappa \cdot q \cdot \frac{\sigma^2}{\text{bin\_step}}\right)$$

Where:
* $q > 0$: Long Token X excess. $\Delta i_{\text{skew}} < 0 \implies$ Shift bins lower to quote cheaper asks and deeper bids, inducing organic market fills that sell off Token X.
* $q < 0$: Long Token Y excess. $\Delta i_{\text{skew}} > 0 \implies$ Shift bins higher to quote attractive bids, buying Token X organically.

```typescript
export function calculateInventorySkew(
  reserveXValueUSD: number,
  reserveYValueUSD: number,
  volatilityDaily: number,
  binStepBps: number,
  riskAversionKappa: number = 0.5
): number {
  const totalValue = reserveXValueUSD + reserveYValueUSD;
  if (totalValue === 0) return 0;

  // Normalized inventory imbalance [-1.0, 1.0]
  const q = (reserveXValueUSD - reserveYValueUSD) / totalValue;
  const binStepDecimal = binStepBps / 10_000;

  // Discrete bin offset
  const rawShift = -1 * riskAversionKappa * q * (Math.pow(volatilityDaily, 2) / binStepDecimal);
  return Math.round(rawShift);
}
```

---

### D. Single-Sided vs Balanced Liquidity Injection

```
Scenario A: Balanced Range [i_min < i_active < i_max]
Deposit: Required X + Required Y calculated from current active bin fraction.

Scenario B: Single-Sided Bid [i_max < i_active]
Deposit: 100% Token X. Limits risk to buying pullbacks (Limit Buy Grid).

Scenario C: Single-Sided Ask [i_min > i_active]
Deposit: 100% Token Y. Limits risk to selling rallies (Limit Sell Grid).
```

* **Zero-Slippage DCA Injection**: Injecting single-sided liquidity above or below active bin incurs **zero price impact** and earns dynamic swap fees while filling.

---

## 3. Automated Volatility-Aware Rebalancing Strategies

### A. Rebalancing Trigger Thresholds

```
                       [ Lower Bound ]      [ Active Price ]      [ Upper Bound ]
 Position Range:              |--------------------*--------------------|
 Rebalance Trigger:      [<-- Alert ]                               [ Alert -->]
 Threshold:          (i_active - i_min) <= 2 bins             (i_max - i_active) <= 2 bins
```

#### Deterministic Trigger Conditions:
1. **Range Boundary Breach**:
   $$|i_{\text{active}} - i_{\text{center}}| \ge \theta_{\text{threshold}} \cdot \frac{W_{\text{range}}}{2}$$
   Where $\theta_{\text{threshold}} \in [0.70, 0.90]$.
2. **Anti-Whipsaw Time Filter**:
   Active price must stay outside threshold for at least $\tau_{\text{confirm}}$ slots ($N \ge 15$ slots / ~6 seconds) to prevent rebalancing on temporary flash wick.
3. **Net Alpha Economic Gate**:
   $$\text{UnclaimedFees} - (\text{EstRebalanceSlippage} + \text{TxCosts}) > 0$$

---

### B. Dynamic Range Sizing via Realized Volatility

Never use static range widths. Adjust bin span dynamically based on rolling Parkinson / Close-to-Close Realized Volatility ($\sigma_{\text{realized}}$):

#### 1. Parkinson High-Low Volatility Estimator:
$$\sigma_{\text{Parkinson}} = \sqrt{\frac{1}{4 \ln 2 \cdot N} \sum_{k=1}^N \left(\ln \frac{H_k}{L_k}\right)^2}$$

#### 2. Volatility-Calibrated Bin Span ($W_{\text{bins}}$):
$$W_{\text{bins}} = \max\left(W_{\text{min}}, \left\lceil \frac{Z_\alpha \cdot \sigma_{\text{Parkinson}} \cdot \sqrt{\Delta t}}{\ln\left(1 + \frac{\text{bin\_step}}{10000}\right)} \right\rceil\right)$$

Where:
* $Z_\alpha$: Normal distribution coverage factor ($Z_{0.95} = 1.96$ for $95\%$ range retention).
* $\Delta t$: Expected rebalance holding horizon (e.g. 1 day = $1.0$).
* $W_{\text{min}}$: Minimum viable range width to prevent hyper-frequent rebalancing churn.

```typescript
export function computeOptimalBinRange(
  highPrices: number[],
  lowPrices: number[],
  binStepBps: number,
  coverageZ: number = 1.96,
  minBins: number = 10
): { halfWidthBins: number; totalBins: number } {
  const n = highPrices.length;
  if (n < 2) throw new Error("Insufficient candles for volatility estimation");

  let sumSquaredLogRatios = 0;
  for (let k = 0; k < n; k++) {
    const hlRatio = Math.log(highPrices[k] / lowPrices[k]);
    sumSquaredLogRatios += Math.pow(hlRatio, 2);
  }

  const parkinsonSigma = Math.sqrt(sumSquaredLogRatios / (4 * Math.log(2) * n));
  const stepRatio = Math.log(1 + binStepBps / 10_000);

  const halfWidth = Math.max(
    Math.ceil((coverageZ * parkinsonSigma) / stepRatio),
    Math.ceil(minBins / 2)
  );

  return {
    halfWidthBins: halfWidth,
    totalBins: halfWidth * 2 + 1,
  };
}
```

---

### C. Atomic Jupiter Rebalance Pipeline

```
  [1. Remove Liquidity] 
          │
          ▼
  [2. Claim All Fees]
          │
          ▼
  [3. Query Jupiter Quote] ──> Exact target token ratio (e.g. 50:50 at new mid-bin)
          │
          ▼
  [4. Execute Swap] ──────────> Direct route / Jito-guarded sandwich protection
          │
          ▼
  [5. Add Liquidity] ─────────> Re-centered dynamic DLMM range
```

```typescript
import { Connection, PublicKey, VersionedTransaction } from "@solana/web3.js";

export interface RebalanceParameters {
  userPublicKey: PublicKey;
  poolAddress: PublicKey;
  tokenMintX: PublicKey;
  tokenMintY: PublicKey;
  currentActiveBin: number;
  newHalfWidthBins: number;
  targetRatioX: number; // e.g. 0.50 for 50% Token X, 50% Token Y
  maxSlippageBps: number;
}

export async function fetchJupiterRebalanceRoute(
  inputMint: string,
  outputMint: string,
  amountRaw: string,
  slippageBps: number
) {
  const url = `https://quote-api.jup.ag/v6/quote?inputMint=${inputMint}&outputMint=${outputMint}&amount=${amountRaw}&slippageBps=${slippageBps}&onlyDirectRoutes=false`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Jupiter quote failed: ${response.statusText}`);
  }
  return await response.json();
}
```

---

## 4. Accurate PnL & Yield Accounting Engine

### A. True Baseline Capital Benchmarks

Never compute PnL purely against initial USD value. Proper quantitative market-making accounts for **Opportunity Cost** and **Divergence Alpha**.

```
                           Market Making Returns
                                    │
       ┌────────────────────────────┴────────────────────────────┐
       ▼                                                         ▼
[ HODL Benchmark ]                                     [ USD Static Benchmark ]
V_HODL(t) = X_0*P_X(t) + Y_0*P_Y(t)                   V_USD(0) = X_0*P_X(0) + Y_0*P_Y(0)
       │                                                         │
       └────────────────────────────┬────────────────────────────┘
                                    ▼
                      [ True Net Alpha PnL ]
           Alpha(t) = V_Position(t) + Fees(t) - V_HODL(t)
```

#### Benchmark Definitions:
1. **Current Total Portfolio Value ($V_{\text{Total}}(t)$)**:
   $$V_{\text{Total}}(t) = \left(R_X(t) \cdot P_X(t) + R_Y(t) \cdot P_Y(t)\right) + \sum \text{ClaimedFees}_{\text{USD}} + \text{UnclaimedFees}_{\text{USD}}$$
2. **HODL Baseline ($V_{\text{HODL}}(t)$)**:
   $$V_{\text{HODL}}(t) = X_0 \cdot P_X(t) + Y_0 \cdot P_Y(t)$$
3. **True Market Making Alpha ($\alpha_{\text{MM}}(t)$)**:
   $$\alpha_{\text{MM}}(t) = V_{\text{Total}}(t) - V_{\text{HODL}}(t) - \sum \text{GasExpenses} - \sum \text{RebalanceSlippageLoss}$$

* If $\alpha_{\text{MM}}(t) > 0$: Market maker outperformed buy-and-hold.
* If $\alpha_{\text{MM}}(t) < 0$: Fee yield failed to compensate for concentrated impermanent loss.

---

### B. Fee Growth Tracking & On-Chain Accumulator Accounting

In DLMM pools, fee growth is tracked globally per bin via monotonically increasing accumulator indices $f_{g, X}$ and $f_{g, Y}$:

#### Unclaimed Fee Calculation for Bin $i$:
$$\Delta \text{Fee}_X(i) = S_{\text{user}}(i) \times \left( f_{g, X}(i) - f_{\text{entry}, X}(i) \right)$$
$$\Delta \text{Fee}_Y(i) = S_{\text{user}}(i) \times \left( f_{g, Y}(i) - f_{\text{entry}, Y}(i) \right)$$

Where:
* $S_{\text{user}}(i)$: Liquidity shares owned by user in bin $i$.
* $f_{g, X}(i)$: Current cumulative fee growth per share for token X in bin $i$.
* $f_{\text{entry}, X}(i)$: Fee growth per share recorded at the moment of position deposit.

```typescript
export interface BinPositionLedger {
  binId: number;
  shares: bigint;
  feeGrowthCheckpointX: bigint;
  feeGrowthCheckpointY: bigint;
}

export function computeUnclaimedFees(
  position: BinPositionLedger,
  currentFeeGrowthX: bigint,
  currentFeeGrowthY: bigint,
  scaleDecimals: bigint = BigInt(1e12)
): { unclaimedX: bigint; unclaimedY: bigint } {
  const deltaGrowthX = currentFeeGrowthX - position.feeGrowthCheckpointX;
  const deltaGrowthY = currentFeeGrowthY - position.feeGrowthCheckpointY;

  const unclaimedX = (position.shares * deltaGrowthX) / scaleDecimals;
  const unclaimedY = (position.shares * deltaGrowthY) / scaleDecimals;

  return { unclaimedX, unclaimedY };
}
```

---

### C. Optimal Compounding Frequency & Gas Drag Optimization

Reinvesting claimed fees increases position principal, enabling compound yield. However, each compound transaction incurs network fees and potential swap drag.

#### Net Compounded Yield Model:
$$\text{APY}_{\text{net}}(n) = \left(1 + \frac{\text{APR}_{\text{gross}}}{n}\right)^n - 1 - \frac{n \cdot C_{\text{gas}}}{V_0}$$

Where:
* $\text{APR}_{\text{gross}}$: Annualized fee rate without compounding.
* $n$: Number of compounding events per year.
* $C_{\text{gas}}$: Fixed transaction fee per compound (in USD).
* $V_0$: Total position principal value (in USD).

#### Analytical Optimal Compounding Frequency ($n^*$):
$$n^* = \sqrt{\frac{V_0 \cdot \text{APR}_{\text{gross}} \cdot \ln(1 + \text{APR}_{\text{gross}})}{2 \cdot C_{\text{gas}}}}$$

```typescript
export function computeOptimalCompoundingFrequency(
  positionPrincipalUSD: number,
  grossApr: number,         // e.g. 0.85 for 85% APR
  gasCostPerCompoundUSD: number = 0.005 // Solana typical tx cost
): { optimalCompoundsPerYear: number; optimalIntervalHours: number } {
  if (positionPrincipalUSD <= 0 || grossApr <= 0 || gasCostPerCompoundUSD <= 0) {
    return { optimalCompoundsPerYear: 0, optimalIntervalHours: Infinity };
  }

  const numerator = positionPrincipalUSD * grossApr * Math.log(1 + grossApr);
  const denominator = 2 * gasCostPerCompoundUSD;
  const nStar = Math.sqrt(numerator / denominator);

  const compoundsPerYear = Math.max(1, Math.round(nStar));
  const intervalHours = (365.25 * 24) / compoundsPerYear;

  return {
    optimalCompoundsPerYear: compoundsPerYear,
    optimalIntervalHours: Number(intervalHours.toFixed(2)),
  };
}
```

---

## 5. Production Rebalancing Execution Engine

```typescript
import { PublicKey } from "@solana/web3.js";

export interface MarketState {
  currentActiveBin: number;
  activePrice: number;
  dailyRealizedVol: number;
  poolBinStepBps: number;
}

export interface PositionState {
  lowerBinId: number;
  upperBinId: number;
  reserveXAmount: number;
  reserveYAmount: number;
  unclaimedFeesUSD: number;
}

export interface RebalanceDecision {
  shouldRebalance: boolean;
  reason: "OUT_OF_BOUNDS" | "INVENTORY_SKEW_CRITICAL" | "PROFITABLE_RECENTER" | "HOLD";
  targetLowerBin: number;
  targetUpperBin: number;
  targetBinOffset: number;
}

export function evaluateRebalanceExecution(
  market: MarketState,
  position: PositionState,
  estimatedTxCostUSD: number = 0.05
): RebalanceDecision {
  const currentBin = market.currentActiveBin;
  const rangeWidth = position.upperBinId - position.lowerBinId;
  const midBin = (position.lowerBinId + position.upperBinId) / 2;
  const distanceFromMid = Math.abs(currentBin - midBin);

  // 1. Check Spatial Breach (> 80% from center to edge)
  const breachThreshold = (rangeWidth / 2) * 0.8;
  const isOutOfRange = currentBin < position.lowerBinId || currentBin > position.upperBinId;
  const isApproachingEdge = distanceFromMid >= breachThreshold;

  // 2. Compute dynamic volatility-adjusted range
  const stepRatio = Math.log(1 + market.poolBinStepBps / 10_000);
  const targetHalfWidth = Math.max(
    10,
    Math.ceil((1.96 * market.dailyRealizedVol) / stepRatio)
  );

  // 3. Compute inventory skew offset
  const totalVal = position.reserveXAmount * market.activePrice + position.reserveYAmount;
  const skewOffset = calculateInventorySkew(
    position.reserveXAmount * market.activePrice,
    position.reserveYAmount,
    market.dailyRealizedVol,
    market.poolBinStepBps
  );

  const targetCenterBin = currentBin + skewOffset;
  const targetLower = targetCenterBin - targetHalfWidth;
  const targetUpper = targetCenterBin + targetHalfWidth;

  if (isOutOfRange) {
    return {
      shouldRebalance: true,
      reason: "OUT_OF_BOUNDS",
      targetLowerBin: targetLower,
      targetUpperBin: targetUpper,
      targetBinOffset: skewOffset,
    };
  }

  if (isApproachingEdge) {
    // Economic validation: Fees collected must justify rebalance gas + slippage
    if (position.unclaimedFeesUSD > estimatedTxCostUSD * 3) {
      return {
        shouldRebalance: true,
        reason: "PROFITABLE_RECENTER",
        targetLowerBin: targetLower,
        targetUpperBin: targetUpper,
        targetBinOffset: skewOffset,
      };
    }
  }

  return {
    shouldRebalance: false,
    reason: "HOLD",
    targetLowerBin: position.lowerBinId,
    targetUpperBin: position.upperBinId,
    targetBinOffset: 0,
  };
}
```

---

## 6. Empirical Verification & Production Checklist

- [ ] **Bin Step Precision**: Bin prices derived using `Math.pow(1 + binStep / 10000, binId)` verified against on-chain pool state.
- [ ] **Decimal Scaling Guard**: Raw token unit calculations scaled strictly with $10^{\text{decimals}_X - \text{decimals}_Y}$. Never use raw unscaled UI floats.
- [ ] **Dynamic Fee Accrual Check**: Verified fee growth per share accumulators match on-chain bin checkpoints before and after withdraw instructions.
- [ ] **Anti-Whipsaw Filter**: Rebalance state triggers verified over a sliding window of $\ge 15$ slots to prevent sandwich / wick-induced repositioning.
- [ ] **LVR Viability Verification**: Historical pool fee earnings verified to exceed $\frac{\sigma^2}{8} \cdot \eta$ before deploying capital into tight ranges.
- [ ] **Atomic Swap Routing**: Rebalance swaps executed via Jupiter with strict `slippageBps` bounds and compute budget headers.
- [ ] **True PnL Reconciliation**: Yield reported against $V_{\text{HODL}}(t)$ rather than static initial USD value.
