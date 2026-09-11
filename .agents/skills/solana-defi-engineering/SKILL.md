---
name: solana-defi-engineering
description: High-precision guide for Solana DeFi systems engineering, covering account model invariants, PDAs, ATAs, Meteora DLMM pool mechanics, Jupiter swap aggregation, dynamic compute budgeting, priority fees, and idempotent transaction lifecycles.
---

# Solana DeFi Engineering Handbook

High-precision, empirical architectural specifications and engineering invariants for building high-throughput, deterministic DeFi applications on Solana.

---

## 1. Solana Runtime & Account Model Invariants

### A. Account Model & Storage Invariants
* **Account Structure**: Every account contains `lamports`, `data` (byte buffer), `owner` (Program ID owning the account), `executable` (bool), and `rent_epoch`.
* **Modification Rules**:
  * Only the account's `owner` program can write to `data` or deduct `lamports`.
  * Anyone can credit `lamports` to any account.
  * System Program is the initial owner of all standard keypair accounts.
* **Rent Exemption**: All accounts maintained on-chain must hold `lamports >= Rent::minimum_balance(data_len)`. Any transaction reducing lamports below rent exemption without zeroing out data and lamports (account closure) fails.
* **Account Deserialization Safety**: Always verify `account.owner == expected_program_id` and check account discriminator / data length before interpreting bytes.

### B. Program Derived Addresses (PDAs)
* **Mathematical Invariant**: PDAs are points that fall **off** the Ed25519 elliptic curve ($y^2 = x^3 + 486662x^2 + x$). They have no private key and can only be signed for by the owning program using `invoke_signed`.
* **Derivation**:
  ```typescript
  import { PublicKey } from "@solana/web3.js";

  const [pda, canonicalBump] = PublicKey.findProgramAddressSync(
    [Buffer.from("vault"), poolAddress.toBuffer(), tokenMint.toBuffer()],
    programId
  );
  ```
* **PDA Invariants & Pitfalls**:
  1. **Canonical Bump Enforcement**: Always store and verify the canonical bump (highest valid bump 255..0 returned by `findProgramAddressSync`). Never accept arbitrary bumps from client input without validation to prevent address aliasing exploits.
  2. **CPI Signing**: When calling other programs (e.g., token transfers), provide the exact seed slice + bump:
     ```rust
     let seeds = &[
         b"vault".as_ref(),
         pool.key().as_ref(),
         token_mint.key().as_ref(),
         &[canonical_bump],
     ];
     let signer_seeds = &[&seeds[..]];
     token::transfer(
         CpiContext::new_with_signer(token_program.to_account_info(), cpi_accounts, signer_seeds),
         amount,
     )?;
     ```

### C. Associated Token Accounts (ATAs) & Token Standards
* **SPL Token vs Token-2022**:
  * Standard SPL Token: `TokenkegQfeZyiNpF5225SCqdozxmNxv474up7c523wd7` (Fixed 165-byte account layout).
  * Token-2022 (Extensions): `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb` (Variable length layout with type-length-value extension headers for transfer fees, confidential transfers, transfer hooks).
* **ATA Derivation**:
  ```typescript
  import { getAssociatedTokenAddressSync, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID } from "@solana/spl-token";

  const userAta = getAssociatedTokenAddressSync(
    mintPublicKey,
    walletPublicKey,
    true, // allowOwnerOffCurve (must be true if owner is a PDA)
    tokenProgramId // TOKEN_PROGRAM_ID or TOKEN_2022_PROGRAM_ID
  );
  ```
* **Idempotent Initialization**: Always prepend `createAssociatedTokenAccountIdempotentInstruction` rather than standard `createAssociatedTokenAccountInstruction` to avoid transaction rollback if the ATA was initialized concurrently in the same slot.
* **Precision Invariant**: Never handle token balances using floating-point math. Always use `u64` / `u128` (BN/BigInt in JS) representing raw base units:
  $$\text{Raw Units} = \lfloor \text{UI Amount} \times 10^{\text{decimals}} \rfloor$$

---

## 2. Liquidity Pool Mechanics: Meteora DLMM & Concentrated Liquidity

### A. Meteora DLMM (Dynamic Liquidity Market Maker) Architecture
* **Discrete Price Bins**: Liquidity is distributed across discrete bins. Each bin has a unique integer index $i$ and a fixed price $P(i)$:
  $$P(i) = \left(1 + \frac{\text{bin\_step}}{10000}\right)^i$$
  * $\text{bin\_step}$: Expressed in basis points ($1 \text{ bp} = 0.01\% = 10^{-4}$).
  * Within a single bin, swaps experience **zero price slippage** (pure constant price swap $Y = P \cdot X$).
* **Active Bin ($i_{\text{active}}$)**:
  * Contains both Token X and Token Y reserves.
  * Bins below active bin ($i < i_{\text{active}}$) hold 100% Token X.
  * Bins above active bin ($i > i_{\text{active}}$) hold 100% Token Y.
* **Liquidity Distribution Shapes**:
  * **Spot (Uniform)**: Flat distribution centered around active bin. Standard for ranging sideways assets.
  * **Curve (Gaussian/Concentrated)**: Concentrated bell curve around active price for high capital efficiency on correlated/pegged pairs (e.g., LSTs, stablecoins).
  * **Bid-Ask (Inverse / Volatile)**: Deeper liquidity further from current price to capture high volatility spikes.

### B. Dynamic Fee Engine & Fee Extraction
* **Dynamic Fee Formula**: Total swap fee rate $f_{\text{total}}$ is dynamically calculated per swap:
  $$f_{\text{total}} = f_{\text{base}} + f_{\text{variable}}$$
  $$f_{\text{variable}} = A \cdot \left(\frac{v_a \cdot \text{bin\_step}}{10000}\right)^2$$
  * $f_{\text{base}}$: Configured static base fee.
  * $v_a$: Volatility accumulator tracking short-term price velocity across bins.
  * $A$: Protocol variable fee scaling parameter.
* **Rounding Invariant**:
  * Fee extraction and pool reserve updates must strictly round **against** the swapper and **in favor** of the pool reserves (Floor on output, Ceil on fees).
  * Unclaimed LP fees accumulate proportionally to pool bin shares:
    $$\Delta \text{Fee}_X = \text{Fee}_{\text{bin}, X} \times \frac{\text{User Share}}{\text{Total Bin Liquidity}}$$

---

## 3. Jupiter Aggregator & Swap Routing Architecture

### A. Routing & Slippage Optimization
* **Routing Topology**: Jupiter queries liquidity quotes across all on-chain AMMs (Meteora DLMM, Raydium CLMM/CPMM, Orca Whirlpools, OpenBook) executing direct, multi-hop, or split-route paths.
* **Slippage Bounds Calculation**:
  * For ExactIn swaps:
    $$\text{MinAmountOut} = \lfloor \text{QuoteAmountOut} \times (1 - \text{SlippageBps} / 10000) \rfloor$$
  * Hard enforcement inside swap instruction data guarantees atomicity: if final output $< \text{MinAmountOut}$, entire transaction aborts.

### B. Dynamic Compute Unit (CU) Budgeting
Every Solana transaction defaults to a limit of 200,000 CUs per instruction (max 1.4M CUs per transaction). Over-requesting CUs reduces block scheduler prioritization; under-requesting triggers `ComputationalBudgetExceeded`.

```typescript
import {
  Connection,
  TransactionMessage,
  VersionedTransaction,
  ComputeBudgetProgram,
  PublicKey,
} from "@solana/web3.js";

async function buildOptimalTransaction(
  connection: Connection,
  payer: PublicKey,
  instructions: any[],
  priorityFeeMultiplier: number = 1.15
): Promise<VersionedTransaction> {
  // 1. Fetch recent blockhash
  const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash("confirmed");

  // 2. Build test message with placeholder compute budget
  const testInstructions = [
    ComputeBudgetProgram.setComputeUnitLimit({ units: 1_400_000 }),
    ...instructions,
  ];
  
  const testMessage = new TransactionMessage({
    payerKey: payer,
    recentBlockhash: blockhash,
    instructions: testInstructions,
  }).compileToV0Message();

  const testTx = new VersionedTransaction(testMessage);

  // 3. Simulate transaction to obtain empirical CU usage
  const simulation = await connection.simulateTransaction(testTx, {
    replaceRecentBlockhash: true,
    sigVerify: false,
  });

  if (simulation.value.err) {
    throw new Error(`Simulation failed: ${JSON.stringify(simulation.value.err)}`);
  }

  const unitsConsumed = simulation.value.unitsConsumed || 200_000;
  // Apply 15% safety buffer for state-dependent branch changes
  const optimalCuLimit = Math.min(Math.ceil(unitsConsumed * 1.15), 1_400_000);

  // 4. Calculate dynamic priority fee based on writable accounts
  const writableAccounts = testMessage.accountKeys
    .filter((_, idx) => testMessage.isAccountWritable(idx))
    .map(key => key.toBase58());

  const prioritizationFees = await connection.getRecentPrioritizationFees({
    lockedWritableAccounts: writableAccounts.map(k => new PublicKey(k)),
  });

  const medianPriorityFee = prioritizationFees.length > 0
    ? prioritizationFees.map(f => f.prioritizationFee).sort((a, b) => a - b)[Math.floor(prioritizationFees.length / 2)]
    : 10_000; // fallback microLamports per CU

  const optimalUnitPrice = Math.max(Math.ceil(medianPriorityFee * priorityFeeMultiplier), 1000);

  // 5. Assemble final optimized instructions
  const finalInstructions = [
    ComputeBudgetProgram.setComputeUnitLimit({ units: optimalCuLimit }),
    ComputeBudgetProgram.setComputeUnitPrice({ microLamports: optimalUnitPrice }),
    ...instructions,
  ];

  const finalMessage = new TransactionMessage({
    payerKey: payer,
    recentBlockhash: blockhash,
    instructions: finalInstructions,
  }).compileToV0Message();

  return new VersionedTransaction(finalMessage);
}
```

---

## 4. Robust Transaction Submission & Execution Lifecycle

```
[Build Tx] -> [Simulate & Estimate CU] -> [Sign with Keypair]
                                                |
                      +-------------------------+
                      |
                      v
      [Submit to RPC / Jito Engine] <--------------+ (Retry Interval: 500-1000ms)
                      |                            |
                      v                            |
          [Poll getSignatureStatuses]              |
                      |                            |
         +------------+------------+               |
         |                         |               |
   [Status: Confirmed]   [Not Confirmed Yet] ------+
         |                         | (If currentBlockHeight > lastValidBlockHeight)
         v                         v
     [Success]            [Blockhash Expired] -> [Re-quote & Re-sign]
```

### A. Blockhash Expiration & Replay Protection Invariant
* **Validity Window**: A recent blockhash is valid for exactly 151 slots (~60 to 90 seconds).
* **Uniqueness / Idempotency**: A signed transaction is uniquely identified by its signature. Within the lifetime of its blockhash, it can be executed at most once.
* **Rebroadcasting Rule**: When retrying unconfirmed transactions, do **not** re-sign or change blockhash if still within `lastValidBlockHeight`. Re-sending identical bytes prevents double execution.

### B. High-Reliability Submission Engine

```typescript
import { Connection, VersionedTransaction } from "@solana/web3.js";

interface SendAndConfirmOptions {
  maxRetries?: number;
  retryIntervalMs?: number;
  commitment?: "processed" | "confirmed" | "finalized";
}

async function sendAndConfirmTransactionEmpirical(
  connection: Connection,
  signedTx: VersionedTransaction,
  lastValidBlockHeight: number,
  options: SendAndConfirmOptions = {}
): Promise<string> {
  const { retryIntervalMs = 800, commitment = "confirmed" } = options;
  const rawTx = signedTx.serialize();
  const signature = Buffer.from(signedTx.signatures[0]).toString("base64");
  const base58Sig = require("bs58").encode(signedTx.signatures[0]);

  let isConfirmed = false;
  const startTime = Date.now();

  // Non-blocking submission loop
  const submissionLoop = (async () => {
    while (!isConfirmed) {
      const currentBlockHeight = await connection.getBlockHeight(commitment);
      if (currentBlockHeight > lastValidBlockHeight) {
        throw new Error(`Transaction ${base58Sig} expired (current: ${currentBlockHeight}, validUntil: ${lastValidBlockHeight})`);
      }

      await connection.sendRawTransaction(rawTx, {
        skipPreflight: true,
        maxRetries: 0,
      }).catch(err => {
        // Ignore network drops on rebroadcasts
      });

      await new Promise(resolve => setTimeout(resolve, retryIntervalMs));
    }
  })();

  // Confirmation polling loop
  const confirmationLoop = (async () => {
    while (!isConfirmed) {
      const currentBlockHeight = await connection.getBlockHeight(commitment);
      if (currentBlockHeight > lastValidBlockHeight) {
        throw new Error(`Transaction ${base58Sig} expired before confirmation.`);
      }

      const { value: statuses } = await connection.getSignatureStatuses([base58Sig], {
        searchTransactionHistory: false,
      });

      const status = statuses[0];
      if (status) {
        if (status.err) {
          throw new Error(`Transaction failed on-chain: ${JSON.stringify(status.err)}`);
        }
        if (
          status.confirmationStatus === commitment ||
          (commitment === "confirmed" && status.confirmationStatus === "finalized")
        ) {
          isConfirmed = true;
          return base58Sig;
        }
      }

      await new Promise(resolve => setTimeout(resolve, 600));
    }
    return base58Sig;
  })();

  return await Promise.race([
    confirmationLoop,
    submissionLoop.then(() => base58Sig),
  ]);
}
```

### C. Jito MEV Bundle Submission (Sandwich Protection)
To bypass the public mempool / validator gossip and guarantee atomic execution without sandwich attacks:
1. Construct transaction without standard priority fees.
2. Append a direct Jito tip transfer instruction to one of the 8 active Jito tip accounts:
   * Tip amount: dynamic based on MEV competition (typically 0.001 - 0.01 SOL).
   ```typescript
   import { SystemProgram, PublicKey } from "@solana/web3.js";

   const JITO_TIP_ACCOUNTS = [
     "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5",
     "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
     "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY",
     "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
     "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh",
     "ADuUkR4vqLUMWXxW9gh6D6L8pWHLnjvnxKLQm3EDLphx",
     "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
     "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT",
   ];

   const tipAccount = new PublicKey(
     JITO_TIP_ACCOUNTS[Math.floor(Math.random() * JITO_TIP_ACCOUNTS.length)]
   );

   const tipInstruction = SystemProgram.transfer({
     fromPubkey: payerPublicKey,
     toPubkey: tipAccount,
     lamports: 1_000_000, // 0.001 SOL
   });
   ```
3. Submit bundle via JSON-RPC to Jito Block Engine endpoint (`/api/v1/bundles`).

---

## 5. Production Debugging & Program Error Decoders

### Common Anchor / Solana Error Codes

| Error Hex | Dec Code | Error Name | Root Cause & Resolution |
| :--- | :--- | :--- | :--- |
| `0x1` | 1 | `InsufficientFunds` | Account does not hold enough lamports for rent + fee + transfer. |
| `0x0` | 0 | `Custom(0)` / `LamportBalanceMismatch` | Sum of lamports before != sum of lamports after instruction execution. |
| `0x1770` | 6000 | `ConstraintSeeds` | PDA derivation mismatch between instruction seeds and provided account. |
| `0x1771` | 6001 | `ConstraintHasOne` / `SlippageExceeded` | Pool price moved beyond maximum allowable slippage limit. |
| `0x1772` | 6002 | `ConstraintAccountIsWritable` | Account passed as read-only but modified by program logic. |
| `0x1773` | 6003 | `ConstraintOwner` | Account owner mismatch (e.g., passing System Program account where Token Program is expected). |

---

## 6. Empirical Verification Checklist
- [ ] **Canonical PDA Check**: Every PDA derived using canonical bump; checked against seed constraints.
- [ ] **ATA Idempotency**: ATA creation uses idempotent instructions to avoid race conditions.
- [ ] **Safe Integer Math**: All swaps, shares, and fees use pure integer arithmetic with explicit rounding direction.
- [ ] **Compute Budget Header**: Instructions prefixed with explicit `setComputeUnitLimit` and `setComputeUnitPrice`.
- [ ] **Expiration Guard**: Transactions tracked against `lastValidBlockHeight` before re-issuing new signatures.
- [ ] **No Floating Point**: Token conversions strictly use discrete decimal scaling ($10^{\text{decimals}}$).
