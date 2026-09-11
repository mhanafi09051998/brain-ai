---
name: telegram-bot-architecture
description: Production-grade Telegram bot engineering reference covering long polling vs webhook invariants, offset synchronization, anti-spam loop guards, age-gating stale updates, strict MarkdownV2/HTML character escaping, 4096-character safe chunking, and PM2 crash-loop resilience.
---

# Telegram Bot Architecture & Production Runtime Engineering

An empirical, battle-tested engineering reference for building, deploying, and maintaining high-reliability Telegram bots on Linux VPS environments. Covers network lifecycle guarantees, offset synchronization invariants, anti-crash loop guards, text formatting security, and graceful shutdown protocols.

---

## 1. Telegram Bot Lifecycle & Ingestion Architecture

### A. Long Polling vs. Webhook Trade-offs

| Dimension | Long Polling (`getUpdates`) | Webhook (`setWebhook`) |
| :--- | :--- | :--- |
| **Ingress Requirement** | Zero public ingress. Operates behind NAT, firewalls, and private subnets. | Requires public IPv4/IPv6, valid public domain, and reverse proxy (Nginx, Caddy, Cloudflare). |
| **TLS/SSL Overhead** | None. Standard outbound HTTPS client to `api.telegram.org`. | Mandatory TLS 1.2+ with trusted CA or pinned self-signed certificate. |
| **Concurrency Model** | Single active consumer per bot token (`instances: 1` in PM2 `fork` mode). | Multi-instance horizontally scalable across stateless web servers / serverless workers. |
| **Latency** | Polling reset delay (~50–300ms overhead on new request cycle). | Real-time push (0–50ms ingress latency from Telegram MTProto edge). |
| **Failure Modes** | Network socket timeout (`ETIMEDOUT`, `ECONNRESET`), polling conflicts (`409 Conflict`). | Endpoint delivery backpressure, unacknowledged retry storms (Telegram retries for ~24 hours on non-200). |
| **Recommended Scope** | Background processors, internal dev/staging, bots with $< 100\text{ req/s}$, private tools. | High-volume production bots ($> 100\text{ req/s}$), multi-tier microservices, low-latency applications. |

### B. Long Polling Invariants & Offset Synchronization

1. **The Offset Invariant**:
   - Telegram update delivery requires passing an integer `offset`:
     $$\text{offset} = \text{last\_processed\_update\_id} + 1$$
   - Querying with `offset = X` acknowledges all updates with $\text{update\_id} < X$ to Telegram's backend, permanently removing them from the server queue.
2. **Single-Instance Polling Lock**:
   - Telegram allows **strictly one active `getUpdates` connection per token**.
   - Running duplicate bot instances simultaneously results in alternating `409 Conflict: terminated by other getUpdates request` errors, stalling both processes.
   - **Rule**: Never run long polling in PM2 `cluster` mode (`exec_mode: 'cluster'`). Always use `exec_mode: 'fork'` with `instances: 1`.
3. **Webhook Cleanup on Mode Switch**:
   - If a bot previously registered a webhook, calling `getUpdates` will fail with `409 Conflict: can't use getUpdates method while webhook is active`.
   - **Startup Invariant**: Always execute `deleteWebhook({ drop_pending_updates: false })` before initiating a long polling loop.

```typescript
// Production Long Polling Loop with Strict Offset Confirmation
import { Bot } from 'grammy';

const bot = new Bot(process.env.BOT_TOKEN!);

async function bootstrapPolling() {
  // Clear any existing webhook before starting long polling
  await bot.api.deleteWebhook({ drop_pending_updates: false });

  await bot.start({
    drop_pending_updates: false,
    allowed_updates: ['message', 'callback_query', 'my_chat_member'],
    onStart: (botInfo) => {
      console.log(`[BOOT] Poller active for @${botInfo.username}`);
    }
  });
}
```

### C. Webhook Ingress & Secret Validation

When deploying via Webhooks, the ingress HTTP handler must:
1. **Validate Secret Header**: Check `X-Telegram-Bot-Api-Secret-Token` against a configured cryptographic secret to reject unauthorized HTTP requests.
2. **Acknowledge Fast (Strict 200 OK)**: Send HTTP `200 OK` response immediately within $< 5000\text{ms}$. If internal processing is heavy, push the update to an internal worker queue (Redis / BullMQ) and return `200 OK` immediately to prevent Telegram retry loops.

```typescript
// Fast Webhook Ingress with Secret Token Verification (Express / Node.js HTTP)
import express from 'express';
import { Bot, webhookCallback } from 'grammy';

const app = express();
const bot = new Bot(process.env.BOT_TOKEN!);
const WEBHOOK_SECRET = process.env.TELEGRAM_WEBHOOK_SECRET!;

app.use(express.json());

app.post('/api/telegram-webhook', (req, res, next) => {
  const incomingSecret = req.header('X-Telegram-Bot-Api-Secret-Token');
  if (incomingSecret !== WEBHOOK_SECRET) {
    console.warn(`[SECURITY] Unauthorized webhook request rejected. IP: ${req.ip}`);
    return res.status(403).json({ error: 'Unauthorized' });
  }
  return webhookCallback(bot, 'express')(req, res, next);
});
```

---

## 2. Anti-Spam, Loop Guards & PM2 Protection

### A. The Stale Updates Crash-Loop (The "Post-Downtime Avalanche")

- **The Problem**: If a bot experiences downtime (e.g., server maintenance, power outage, crash for 4 hours), Telegram queues all incoming updates. Upon restart, the bot attempts to process thousands of queued updates in a few seconds. This causes:
  1. Instant triggering of Telegram outgoing rate limits (`429 Too Many Requests`).
  2. Outdated commands executing against stale database states.
  3. Memory exhaustion leading to immediate process crash, triggering a PM2 infinite restart loop.
- **The Invariant**: Discard or selectively filter updates older than a defined threshold ($\Delta t_{\text{max}} \approx 60\text{--}120\text{ seconds}$).

```typescript
// Age-Gating Middleware: Purge Stale Updates on Startup / Spike
const MAX_UPDATE_AGE_SECONDS = 120; // 2 minutes

bot.use(async (ctx, next) => {
  const messageDate = ctx.message?.date ?? ctx.callbackQuery?.message?.date;
  
  if (messageDate) {
    const currentUnixTime = Math.floor(Date.now() / 1000);
    const age = currentUnixTime - messageDate;

    if (age > MAX_UPDATE_AGE_SECONDS) {
      console.warn(`[AGE-GATE] Skipped stale update (ID: ${ctx.update.update_id}, Age: ${age}s)`);
      return; // Drop execution silently
    }
  }

  await next();
});
```

### B. Multi-Tier Rate Limiting (Global & Per-User)

Telegram enforces strict platform-level rate limits:
- **Per User / Private Chat**: Max $1\text{ message/second}$.
- **Per Group Chat**: Max $20\text{ messages/minute}$.
- **Global Broadcast / Outgoing**: Max $30\text{ messages/second}$ across all chats.

#### In-Memory Sliding Window Rate Limiter
```typescript
interface RateLimitRecord {
  timestamps: number[];
}

export class SlidingWindowRateLimiter {
  private store: Map<number, RateLimitRecord> = new Map();
  private readonly maxRequests: number;
  private readonly windowMs: number;

  constructor(maxRequests: number, windowMs: number) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;

    // Periodic cleanup of dormant keys every 5 minutes
    setInterval(() => this.cleanup(), 5 * 60 * 1000).unref();
  }

  public isRateLimited(userId: number): boolean {
    const now = Date.now();
    const record = this.store.get(userId) ?? { timestamps: [] };

    // Filter out timestamps outside the sliding window
    record.timestamps = record.timestamps.filter((ts) => now - ts < this.windowMs);

    if (record.timestamps.length >= this.maxRequests) {
      return true; // Rate limit exceeded
    }

    record.timestamps.push(now);
    this.store.set(userId, record);
    return false;
  }

  private cleanup(): void {
    const now = Date.now();
    for (const [userId, record] of this.store.entries()) {
      record.timestamps = record.timestamps.filter((ts) => now - ts < this.windowMs);
      if (record.timestamps.length === 0) {
        this.store.delete(userId);
      }
    }
  }
}

// Global user limiter: 5 commands per 10 seconds
export const userCommandLimiter = new SlidingWindowRateLimiter(5, 10_000);
```

### C. Inline Button Callback Debounce & Deduplication

Users rapidly double-tapping inline keyboard buttons causes duplicate operations (e.g., double payments, multiple job submissions).

```typescript
const callbackDebounceCache = new Set<string>();

bot.on('callback_query:data', async (ctx, next) => {
  const dedupeKey = `${ctx.from.id}:${ctx.callbackQuery.data}`;

  if (callbackDebounceCache.has(dedupeKey)) {
    // Acknowledge immediately to dismiss Telegram client spinner
    await ctx.answerCallbackQuery({ text: 'Processing already in progress...' });
    return;
  }

  callbackDebounceCache.add(dedupeKey);
  // Auto-expire debounce key after 2 seconds
  setTimeout(() => callbackDebounceCache.delete(dedupeKey), 2000);

  try {
    await next();
  } finally {
    // Always answer callback query to clear button loading animation
    await ctx.answerCallbackQuery().catch(() => {});
  }
});
```

---

## 3. Message Formatting & Character Escaping

Telegram supports `HTML` and `MarkdownV2`. Choosing the wrong format or omitting strict escaping is the #1 cause of `400 Bad Request: can't parse entities` in production.

### A. HTML vs MarkdownV2 Comparison

- **MarkdownV2**: Requires escaping **18 special characters** anywhere outside code blocks:
  `_`, `*`, `[`, `]`, `(`, `)`, `~`, `` ` ``, `>`, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`
  *Failure Mode*: A single unescaped period (`.`) or hyphen (`-`) in dynamic database text crashes the request.
- **HTML (Recommended Standard)**: Only requires escaping **3 characters** in dynamic text insertions: `&`, `<`, `>`.

### B. High-Precision Escaping Implementations

```typescript
// Strict Escaping Utility for Dynamic Data Injection

/**
 * Escapes characters for HTML parse mode.
 * Use when injecting user strings into HTML-formatted Telegram messages.
 */
export function escapeHTML(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/**
 * Escapes characters for MarkdownV2 parse mode.
 * Required for all dynamic text inserted outside formatting delimiters.
 */
export function escapeMarkdownV2(text: string): string {
  return text.replace(/([_*\[\]()~`>#+\-=|{}.!\\])/g, '\\$1');
}

/**
 * Escapes dynamic text inside MarkdownV2 code blocks (``` and `).
 * Inside code blocks, only '`' and '\' need escaping.
 */
export function escapeMarkdownV2Code(text: string): string {
  return text.replace(/([\\`])/g, '\\$1');
}
```

### C. Safe Message Chunking (4096-Character Limit Invariant)

- **The Problem**: Telegram limits message text to **4096 UTF-16 code units** (1024 for photo captions). Slicing strings naively at character 4096 splits UTF-8 surrogate pairs (breaking emojis) and splits open HTML/Markdown entities (`<b>...`), resulting in parse errors.
- **The Solution**: Chunk text along newline/whitespace boundaries, maintaining balanced tag state.

```typescript
/**
 * Splits a long text message into safe chunks <= maxLength (default: 4000 to leave headroom).
 * Splits on line breaks or spaces where possible without breaking words or emojis.
 */
export function splitMessage(text: string, maxLength: number = 4000): string[] {
  if (text.length <= maxLength) return [text];

  const chunks: string[] = [];
  let remaining = text;

  while (remaining.length > 0) {
    if (remaining.length <= maxLength) {
      chunks.push(remaining);
      break;
    }

    // Attempt to split at the last newline within maxLength
    let splitIndex = remaining.lastIndexOf('\n', maxLength);

    // Fallback: split at the last space within maxLength
    if (splitIndex === -1 || splitIndex < maxLength * 0.5) {
      splitIndex = remaining.lastIndexOf(' ', maxLength);
    }

    // Hard fallback: split exactly at maxLength if no whitespace found
    if (splitIndex === -1 || splitIndex === 0) {
      splitIndex = maxLength;
    }

    const chunk = remaining.slice(0, splitIndex).trim();
    if (chunk.length > 0) {
      chunks.push(chunk);
    }

    remaining = remaining.slice(splitIndex).trim();
  }

  return chunks;
}
```

---

## 4. Background Service & Crash Resilience

### A. Telegram Network & API Error Classification

```typescript
import { GrammyError, HttpError } from 'grammy';

export async function handleBotError(error: unknown) {
  if (error instanceof GrammyError) {
    const { error_code, description, parameters } = error;

    switch (error_code) {
      case 400:
        console.error(`[TELEGRAM 400] Bad Request: ${description}`);
        break;
      case 403:
        // Bot was blocked by user or kicked from group
        console.warn(`[TELEGRAM 403] User blocked bot or removed from chat: ${description}`);
        // Action: Mark user as inactive in database to prevent future outbound message attempts
        break;
      case 429:
        // Rate limit exceeded
        const retryAfter = parameters?.retry_after ?? 5;
        console.warn(`[TELEGRAM 429] Rate limited. Must wait ${retryAfter}s`);
        await new Promise((resolve) => setTimeout(resolve, retryAfter * 1000));
        break;
      default:
        console.error(`[TELEGRAM API ERROR] Code ${error_code}: ${description}`);
    }
  } else if (error instanceof HttpError) {
    // Network connectivity issue to api.telegram.org
    console.error(`[NETWORK ERROR] Could not contact Telegram servers:`, error.message);
  } else {
    console.error(`[UNEXPECTED SYSTEM ERROR]`, error);
  }
}
```

### B. PM2 Configuration Standard for VPS Deployment

Save as `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [
    {
      name: 'telegram-bot-worker',
      script: 'dist/index.js',
      cwd: '/var/www/telegram-bot',
      // INVARIANT: Long polling MUST run in fork mode with 1 instance
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      watch: false,
      // Memory threshold protection
      max_memory_restart: '500M',
      // Anti-Crash-Loop Exponential Backoff
      exp_backoff_restart_delay: 1000,
      min_uptime: '10s',
      max_restarts: 15,
      // Graceful termination handling
      kill_timeout: 10000,
      env_production: {
        NODE_ENV: 'production'
      },
      error_file: '/var/log/pm2/telegram-bot-error.log',
      out_file: '/var/log/pm2/telegram-bot-out.log',
      merge_logs: true,
      time: true
    }
  ]
};
```

### C. Graceful Shutdown & Drain Invariant

When PM2 issues `pm2 stop` or during server reboot, `SIGINT` / `SIGTERM` signals are sent. The bot must:
1. Cease polling / webhook ingestion immediately.
2. Complete all in-flight database writes.
3. Close open database/Redis connections.
4. Terminate within the PM2 `kill_timeout` window ($10000\text{ms}$).

```typescript
// Graceful Termination Protocol
async function setupGracefulShutdown(bot: Bot) {
  let isShuttingDown = false;

  const handleSignal = async (signal: string) => {
    if (isShuttingDown) return;
    isShuttingDown = true;

    console.log(`[SHUTDOWN] Received ${signal}. Initiating graceful teardown...`);

    try {
      // 1. Stop Telegram ingestion loop
      if (bot.isInited()) {
        bot.stop();
        console.log('[SHUTDOWN] Telegram polling listener halted.');
      }

      // 2. Complete in-flight work & close resources
      // await db.disconnect();
      // await redis.quit();

      console.log('[SHUTDOWN] All resources cleanly flushed. Exiting.');
      process.exit(0);
    } catch (err) {
      console.error('[SHUTDOWN ERROR] Failure during drain:', err);
      process.exit(1);
    }
  };

  process.on('SIGINT', () => handleSignal('SIGINT'));
  process.on('SIGTERM', () => handleSignal('SIGTERM'));
}
```

---

## 5. End-to-End Production Bot Template (grammY + TypeScript)

```typescript
import { Bot, GrammyError, HttpError } from 'grammy';
import { escapeHTML, splitMessage } from './utils/formatters';
import { userCommandLimiter } from './utils/rateLimiter';

const bot = new Bot(process.env.BOT_TOKEN!);

// 1. Age-Gate Filter
bot.use(async (ctx, next) => {
  const date = ctx.message?.date ?? ctx.callbackQuery?.message?.date;
  if (date && Math.floor(Date.now() / 1000) - date > 120) {
    return; // Drop stale update
  }
  await next();
});

// 2. Anti-Spam Rate Limiter
bot.use(async (ctx, next) => {
  if (ctx.from && userCommandLimiter.isRateLimited(ctx.from.id)) {
    if (ctx.chat?.type === 'private') {
      await ctx.reply('⚠️ Slow down. Too many requests in a short time.');
    }
    return;
  }
  await next();
});

// 3. Command Handler with Safe HTML Formatting & Chunking
bot.command('status', async (ctx) => {
  const rawServerName = 'Prod-VPS-01 <Main>';
  const uptime = process.uptime();
  
  const formattedHtml = `<b>System Status</b>\n` +
    `Node: <code>${escapeHTML(rawServerName)}</code>\n` +
    `Uptime: <code>${uptime.toFixed(0)}s</code>\n` +
    `Memory: <code>${(process.memoryUsage().rss / 1024 / 1024).toFixed(2)} MB</code>`;

  const chunks = splitMessage(formattedHtml);
  for (const chunk of chunks) {
    await ctx.reply(chunk, { parse_mode: 'HTML' });
  }
});

// 4. Global Error Boundary
bot.catch((err) => {
  const ctx = err.ctx;
  console.error(`[GLOBAL HANDLER] Error processing update ${ctx.update.update_id}:`);
  const e = err.error;
  if (e instanceof GrammyError) {
    console.error('Error in request:', e.description);
  } else if (e instanceof HttpError) {
    console.error('Could not contact Telegram:', e);
  } else {
    console.error('Unknown error:', e);
  }
});

// 5. Bootstrap Runner
async function main() {
  await bot.api.deleteWebhook({ drop_pending_updates: false });
  
  process.on('SIGINT', () => bot.stop());
  process.on('SIGTERM', () => bot.stop());

  await bot.start({
    allowed_updates: ['message', 'callback_query'],
    onStart: (info) => console.log(`Bot running as @${info.username}`)
  });
}

main().catch((err) => {
  console.error('Fatal initialization error:', err);
  process.exit(1);
});
```
