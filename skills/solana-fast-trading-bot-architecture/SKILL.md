---
name: solana-fast-trading-bot-architecture
description: High-frequency execution engine, Geyser gRPC streaming, Jito MEV bundle sniping, anti-sandwich protection, and automated copy-trading architecture for Solana DEXs and Telegram bots.
---

# Solana Fast Trading Bot Architecture Handbook

High-throughput, deterministic execution blueprints for sub-50ms DEX sniping, copy-trading, trailing-stop automation, and Telegram/CLI bot architecture on Solana.

---

## 1. High-Throughput Ingestion: Geyser gRPC vs JSON-RPC

Traditional HTTP/JSON-RPC polling introduces 400ms–1500ms latencies. High-frequency trading bots ingest raw validator block data directly via Yellowstone gRPC (Geyser plugin).

```
                      [Solana Validator Cluster]
                                  │ (Geyser Plugin)
                                  ▼
                     [Yellowstone gRPC Stream]
                                  │
          ┌───────────────────────┴───────────────────────┐
          ▼                                               ▼
  [Pump.fun / Raydium                             [Account Balance /
   New Pool Creation Event]                        Large Swap Event]
          │                                               │
          ▼                                               ▼
  [Forensic Safety Filter]                        [Copy-Trade Filter]
          │ (Pass $\ge 85$)                               │
          └───────────────────────┬───────────────────────┘
                                  ▼
                     [Transaction Builder Engine]
                                  │
                                  ▼
                   [Jito Block Engine Bundle (0-MEV)]
```

### Stream Filtering Invariant
* **Subscribe strictly by Account Owner / Program ID**: Filter only `Tokenkeg...`, `6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P` (Pump.fun), or `routeUGWgWzqBWFcrCfv8tritsqukccJPu3q5GPP3xS` (Raydium) to eliminate garbage CPU deserialization.

---

## 2. Zero-Latency Execution Pipeline & Jito Bundles

Public mempool transactions are vulnerable to MEV sandwich bots (front-run buy + back-run sell). Fast trading bots submit transactions privately via Jito Block Engine bundles.

```typescript
import {
  Connection,
  Keypair,
  PublicKey,
  SystemProgram,
  TransactionInstruction,
  TransactionMessage,
  VersionedTransaction,
} from "@solana/web3.js";
import axios from "axios";
import bs58 from "bs58";

const JITO_BLOCK_ENGINE_URL = "https://mainnet.block-engine.jito.wtf/api/v1/bundles";
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

export async function executeAtomicJitoSwap(
  connection: Connection,
  payer: Keypair,
  swapInstructions: TransactionInstruction[],
  tipLamports: number = 2_000_000 // 0.002 SOL
): Promise<string> {
  const { blockhash } = await connection.getLatestBlockhash("confirmed");

  // Pick random tip account to prevent load hot-spotting
  const tipAccount = new PublicKey(
    JITO_TIP_ACCOUNTS[Math.floor(Math.random() * JITO_TIP_ACCOUNTS.length)]
  );

  const tipInstruction = SystemProgram.transfer({
    fromPubkey: payer.publicKey,
    toPubkey: tipAccount,
    lamports: tipLamports,
  });

  const message = new TransactionMessage({
    payerKey: payer.publicKey,
    recentBlockhash: blockhash,
    instructions: [...swapInstructions, tipInstruction],
  }).compileToV0Message();

  const tx = new VersionedTransaction(message);
  tx.sign([payer]);

  const serializedTx = bs58.encode(tx.serialize());

  const response = await axios.post(JITO_BLOCK_ENGINE_URL, {
    jsonrpc: "2.0",
    id: 1,
    method: "sendBundle",
    params: [[serializedTx]],
  });

  if (response.data.error) {
    throw new Error(`Jito bundle rejected: ${JSON.stringify(response.data.error)}`);
  }

  return response.data.result;
}
```

---

## 3. Automated Trade Lifecycle & Position Management

```
    [Entry Executed]
           │
           ▼
    [Initialize Position State Machine]
           │
           ├───────────────────────────────┐
           ▼                               ▼
    [Monitor Price / PnL]           [Monitor Whale / Cluster Sells]
           │                               │
           ▼                               ▼
  ┌──────────────────────────────────────────────────┐
  │ Check Exit Triggers:                             │
  │  1. Take-Profit hit (e.g. +50%, +100%)           │
  │  2. Trailing-Stop hit (e.g. -15% from high watermark) │
  │  3. Hard Stop-Loss hit (e.g. -20% from entry)    │
  │  4. Dev / Insider dump detected on-chain         │
  └───────────────────────┬──────────────────────────┘
                          │ (Trigger Fired)
                          ▼
            [Instant Atomic Exit via Jito]
```

### Trailing-Stop Invariant Algorithm
```typescript
interface PositionState {
  tokenMint: string;
  entryPrice: number;
  highWaterMark: number;
  trailingStopPct: number; // e.g. 0.15 for 15%
  hardStopLossPct: number; // e.g. 0.20 for 20%
}

function evaluateExitTrigger(position: PositionState, currentPrice: number): {
  shouldExit: boolean;
  reason?: string;
} {
  // Update High Watermark
  if (currentPrice > position.highWaterMark) {
    position.highWaterMark = currentPrice;
  }

  // Hard Stop-Loss
  const pnlPct = (currentPrice - position.entryPrice) / position.entryPrice;
  if (pnlPct <= -position.hardStopLossPct) {
    return { shouldExit: true, reason: `HARD_STOP_LOSS (PnL: ${(pnlPct * 100).toFixed(2)}%)` };
  }

  // Trailing Stop from High Watermark
  const drawdownFromPeak = (position.highWaterMark - currentPrice) / position.highWaterMark;
  if (drawdownFromPeak >= position.trailingStopPct) {
    return { shouldExit: true, reason: `TRAILING_STOP (Peak Drawdown: ${(drawdownFromPeak * 100).toFixed(2)}%)` };
  }

  return { shouldExit: false };
}
```

---

## 4. Telegram & CLI Bot Architecture Invariants

1. **State Isolation**: User sessions, active open positions, and private keys must be strictly isolated. Private keys encrypted at rest using AES-256-GCM.
2. **Rate Limit & Concurrency**:
   * Outgoing Telegram notifications throttled to max 25 msg/sec to prevent `429 Too Many Requests`.
   * Trade execution runs asynchronously in worker threads / tokio tasks without blocking the Telegram message handler.
3. **MarkdownV2 Sanitization**: All token symbols, price numbers, and base58 transaction signatures must be strictly escaped when rendering Telegram messages.
