---
name: solana-onchain-forensics-token-audit
description: Production-grade on-chain forensics, wallet clustering, bundle sniper detection, wash trading identification, and contract security auditing for Solana DEX tokens and memecoins.
---

# Solana On-Chain Forensics & Token Security Audit Handbook

High-precision, empirical specifications and analytical algorithms for deconstructing token distribution, detecting stealth dumps, auditing contract security, and identifying market manipulation on Solana DEXs.

---

## 1. Wallet Clustering & Sybil Graphing Invariants

Manipulated tokens rely on distributed sybil wallets to mask insider control. Forensic inspection tracks address creation and funding lineage.

```
                  [CEX / Bridge / Mixer]
                            |
                 [Funding Source Wallet]
               /           |           \
      (Tx 1 @ t0)     (Tx 2 @ t0+1s)   (Tx 3 @ t0+2s)
          /                |                \
    [Sniper A]        [Sniper B]        [Sniper C]
         \                 |                 /
          ===================================
          [Simultaneous Token Purchase Bundle]
```

### A. Funding Lineage & Cluster Detection Heuristics
1. **Parent Funding Entropy**:
   * Inspect the first 5 transactions of early buyer wallets.
   * If $>30\%$ of the initial buyer cohort received SOL from the identical parent address (or identical CEX withdrawal hot wallet within $<120\text{ seconds}$), mark the cohort as a **Coordinated Cabal Cluster**.
2. **Cluster Balance Invariant**:
   * Wallets funded with identical round amounts (e.g., exactly 1.00 SOL, 2.50 SOL, 0.50 SOL) in the same slot or block window are automated cluster nodes.
3. **Stealth Split Transfers (Dev Offloading)**:
   * Track token transfers from the deployer or top holders to secondary wallets with zero swap history.
   * If a non-DEX transfer occurs from a top holder to a fresh wallet followed by DEX sells, aggregate the balances into the parent's effective holding percentage.

---

## 2. Jito Bundle Sniper Deconstruction

Token launches on Pump.fun, Raydium CPMM, or Meteora are frequently sniped via Jito Block Engine bundles in block slot 0.

### Forensic Identification Rules
* **Atomic Block Slot Invariant**: Check if multiple buy transactions for the token exist within the exact same block slot ($N$) and share the identical Jito Tip transaction.
* **Effective Insider Supply Calculation**:
  $$\text{Supply}_{\text{insider}} = \text{Supply}_{\text{deployer}} + \sum_{k \in \text{Slot 0 Bundles}} \text{Supply}_k + \sum_{j \in \text{Cluster Wallets}} \text{Supply}_j$$
* **Rejection Boundary**:
  $$\text{If } \frac{\text{Supply}_{\text{insider}}}{\text{Total Supply}} > 0.15 \ (15\%) \implies \text{CRITICAL DUMP RISK (REJECT)}$$

---

## 3. Holder Concentration & Supply Entropy

```typescript
interface HolderDistribution {
  address: string;
  amount: bigint;
  percentage: number;
  isPoolOrBurn: boolean;
  isDevAffiliated: boolean;
}

function calculateHolderEntropy(holders: HolderDistribution[], totalSupply: bigint): {
  top10Percentage: number;
  giniCoefficient: number;
  isHighRisk: boolean;
} {
  // Filter out known DEX pools and burn addresses (e.g., 11111111111111111111111111111111, Raydium Vaults)
  const organicHolders = holders.filter(h => !h.isPoolOrBurn);
  const sorted = [...organicHolders].sort((a, b) => (b.amount > a.amount ? 1 : -1));

  const top10Sum = sorted.slice(0, 10).reduce((acc, h) => acc + h.amount, 0n);
  const top10Percentage = Number((top10Sum * 10000n) / totalSupply) / 100;

  // Gini coefficient calculation for holder inequality
  const n = sorted.length;
  if (n === 0) return { top10Percentage: 0, giniCoefficient: 1, isHighRisk: true };

  let cumulativeSum = 0n;
  let weightedSum = 0n;
  for (let i = 0; i < n; i++) {
    cumulativeSum += sorted[i].amount;
    weightedSum += sorted[i].amount * BigInt(i + 1);
  }

  const gini = Number((2n * weightedSum) / (BigInt(n) * cumulativeSum) - BigInt(n + 1)) / n;

  // High risk if top 10 holders control > 20% of organic supply
  const isHighRisk = top10Percentage > 20.0 || gini > 0.85;

  return { top10Percentage, giniCoefficient: gini, isHighRisk };
}
```

---

## 4. Wash Trading & Volume Manipulation Signatures

Scammers fabricate volume to rank on GMGN, DexScreener, and trending bots.

### Analytical Invariants
1. **Maker-to-Volume Ratio ($R_{mv}$)**:
   $$R_{mv} = \frac{\text{24h Trading Volume (USD)}}{\text{24h Unique Active Wallets}}$$
   * Healthy memecoin / token: $R_{mv} < \$500 - \$1,500$ per unique wallet.
   * Manipulated wash-trade: $R_{mv} > \$10,000$ per unique wallet (e.g., \$1M volume with 50 makers).
2. **Cyclic Self-Swapping**:
   * Token $A \to SOL \to \text{Wallet } B \to \text{Token } A$.
   * Zero net balance accumulation; high churn with single-block turnaround.
3. **Volume Decay Half-Life**:
   * Authentic organic tokens display long-tail power law volume decay.
   * Fake volume abruptly drops to near zero ($>85\%$ drop in $<15\text{ minutes}$) once trending spot is achieved.

---

## 5. Smart Contract & Token Extension Safety Invariants

### A. SPL Token Standard Invariants
* **Mint Authority**: Must be `null` / revoked. If `mint_authority != null`, deployer can inflate supply arbitrarily to 0.
* **Freeze Authority**: Must be `null` / revoked. If active, deployer can freeze user ATAs from selling (*Honeypot*).
* **LP Burn / Lock Verification**:
  * Raydium AMM: Pool LP token ATA must hold 0 or be burned to `11111111111111111111111111111111` / locked in verified locker (Streamflow, Uncx).
  * Meteora DLMM: Pool owner / creator LP bins must be verified non-withdrawable.

### B. Token-2022 Extension Exploit Vectors
When inspecting `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`:
* **Transfer Fee Extension**: Check `fee_basis_points` and `maximum_fee`. If fee basis points $> 100 \ (1\%)$ or mutable by authority without time-lock, flag as malicious.
* **Transfer Hook Extension**: Inspect the hook program. Malicious hook programs can intercept transfers and revert all DEX sell instructions while allowing buy instructions.
* **Permanent Delegate**: Must NOT be set. A permanent delegate can transfer or burn tokens from any wallet without signature.

---

## 6. Deterministic Heuristic Scoring Pipeline (0 - 100 Safety Score)

| Parameter | Safety Criteria | Weight |
| :--- | :--- | :--- |
| **Mint & Freeze Authority** | Both Revoked (`null`) | 25 pts |
| **LP Burn / Lock Status** | 100% Permanently Burned / Locked | 25 pts |
| **Holder Distribution** | Top 10 non-pool holders $< 15\%$ | 20 pts |
| **Cluster & Sniper Ratio** | Slot-0 bundle + cluster holdings $< 10\%$ | 15 pts |
| **Volume Organic Health** | $R_{mv} < \$1,500$ and $>300$ unique makers | 15 pts |

* **Execution Threshold**:
  * Score $\ge 85$: **APPROVED** for DLMM liquidity provision or trading.
  * Score $65 - 84$: **CAUTION** (Tight stop-loss, short duration).
  * Score $< 65$: **HARD REJECT** (Do not open DLMM pool, high risk of dump).
