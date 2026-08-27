# N069: Zero-Downtime Migrations, Expand-and-Contract & Dual-Write Cutover

- **Kategori:** Database Engineering, Zero-Downtime Schema Evolution & Distributed Migrations
- **Tanggal Sintesis:** 2026-08-27
- **Status:** Active Operational Invariant
- **Synaptic Links:** [`N013`](file:///D:/GEMINI-HANAFI/learning/neurons/N013_deep_storage_and_distributed_db.md), [`N031`](file:///D:/GEMINI-HANAFI/learning/neurons/N031_modern_data_storage_pgvector.md), [`N062`](file:///D:/GEMINI-HANAFI/learning/neurons/N062_distributed_consensus_and_saga.md)

---

## 🎯 1. The 6-Phase Expand-and-Contract Lifecycle

```
[Phase 0: S0] Old Schema V1 (Reads/Writes on Old Column/Table)
      │
      ▼ (Deploy 1: DDL Expand - Nullable/New Table, CREATE INDEX CONCURRENTLY)
[Phase 1: S1] Expanded Schema (Old + New Structures Coexist)
      │
      ▼ (Deploy 2: Enable Dual-Writing via DB Triggers or App-Level Writes)
[Phase 2: S2] Dual-Writing Active (Writes -> Old & New; Reads -> Old)
      │
      ▼ (Async Job: Keyset Pagination Backfilling with Adaptive Rate-Limiting)
[Phase 3: S3] Backfilled & Parity Validated (Old == New, Delta = 0)
      │
      ▼ (Deploy 3: Cutover Read Path to New Schema; Retain Dual-Write)
[Phase 4: S4] Read Switched (Reads -> New; Writes -> Old & New)
      │
      ▼ (Deploy 4: Cutover Write Path Exclusively to New Schema)
[Phase 5: S5] Write Switched (Reads/Writes -> New Only; Old Deprecated)
      │
      ▼ (Deploy 5: DDL Contract - Drop Triggers, Async Drop Old Column/Table)
[Phase 6: S6] Contracted Schema V2 (Clean Target Architecture)
```

---

## 📐 2. Core Mathematical & Algorithmic Invariants

### 2.1. Keyset Backfill & Adaptive Replication-Aware Rate Limiting
Eliminasi $O(N)$ table scans dengan monotonic keyset chunking. Jeda batch ($\delta_t$) beradaptasi secara eksponensial terhadap replication lag ($\Delta_{\text{repl}}$) dan write latency host:

$$\text{Chunk}_k = \{ r \in R \mid r.\text{id} > \max(\text{Chunk}_{k-1}.\text{id}) \text{ ORDER BY id ASC LIMIT } K \}$$

$$\delta_t = \delta_{\text{base}} \cdot \exp\left(\alpha \cdot \max\left(0, \Delta_{\text{repl}} - \tau_{\text{threshold}}\right)\right)$$

*Di mana $K$ adalah batch size (umumnya $1{,}000 - 5{,}000$), $\tau_{\text{threshold}}$ adalah target repl lag maksimal ($<100\text{ms}$), dan $\alpha$ adalah damping factor.*

### 2.2. Postgres Lock Starvation Guard & Safe Indexing
DDL migration tidak boleh memblokir transaksi OLTP. Setiap DDL wajib menyertakan timeout ketat:

```sql
-- Invariant: Mencegah lock queue saturation
SET lock_timeout = '2s';
SET statement_timeout = '10s';

-- Expand: Tambah kolom non-blocking (PostgreSQL >= 11 mendukung non-null default tanpa table rewrite)
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);

-- Safe Indexing: Non-blocking B-tree creation
CREATE INDEX CONCURRENTLY idx_users_full_name ON users (full_name);
```

### 2.3. Idempotent Dual-Write Trigger (Database Layer)
Menjamin sinkronisasi atomic baris aktif tanpa mendegradasi read performance:

```sql
CREATE OR REPLACE FUNCTION trg_sync_users_name()
RETURNS TRIGGER AS $$
BEGIN
    NEW.full_name := TRIM(CONCAT(COALESCE(NEW.first_name, ''), ' ', COALESCE(NEW.last_name, '')));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_users_dual_write
BEFORE INSERT OR UPDATE OF first_name, last_name ON users
FOR EACH ROW EXECUTE FUNCTION trg_sync_users_name();
```

---

## 🔍 3. Root Cause Analysis & Failure Mode Guards

| Failure Mode | Root Cause | Preventive Invariant |
| :--- | :--- | :--- |
| **Lock Starvation Cascade** | `ALTER TABLE` meminta `AccessExclusiveLock`, mengantre di belakang long-running read, memblokir seluruh koneksi baru. | Terapkan `lock_timeout = '2s'` + retry loop eksponensial. Jangan jalankan DDL dalam transaksi panjang. |
| **WAL Flooding & Replication Lag** | Backfill $100\text{M}$ baris menghasilkan lonjakan WAL tak terkendali, membuat replica disk choke dan snapshot stale. | Throttling adaptif berbasis `pg_stat_replication.replay_lag`. Lakukan `COMMIT` per chunk keyset. |
| **Silent Parity Drift** | Race condition saat update terjadi di antara fase backfill dan cutover. | Database triggers mengeksekusi di dalam transaksi yang sama. Verifikasi checksum via hash chunking sebelum cutover. |
| **Deployment Rollback Incompatibility** | Aplikasi versi $N-1$ crash karena kolom yang dibutuhkannya sudah dihapus sebelum seluruh pods di-deploy. | **Strict N-1 / N+1 Invariant**: Schema harus selalu kompatibel mundur dengan $N-1$ dan kompatibel maju dengan $N+1$. |

---

## ⚡ 4. Reference Engine: Production Keyset Backfiller (Python Async)

```python
"""Zero-downtime adaptive keyset backfiller with replication lag feedback."""
import asyncio
import time
from typing import Optional

class AdaptiveBackfillEngine:
    def __init__(self, db_pool, batch_size: int = 2000, max_lag_ms: float = 100.0):
        self.pool = db_pool
        self.batch_size = batch_size
        self.max_lag_ms = max_lag_ms
        self.base_delay = 0.01  # 10ms base sleep

    async def get_replication_lag_ms(self) -> float:
        async with self.pool.acquire() as conn:
            val = await conn.fetchval("""
                SELECT COALESCE(EXTRACT(EPOCH FROM MAX(replay_lag))*1000.0, 0.0)
                FROM pg_stat_replication;
            """)
            return float(val or 0.0)

    async def backfill_column(self, last_processed_id: int = 0) -> int:
        total_migrated = 0
        current_id = last_processed_id

        while True:
            t0 = time.monotonic()
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    rows = await conn.fetch("""
                        SELECT id, first_name, last_name 
                        FROM users 
                        WHERE id > $1 AND full_name IS NULL
                        ORDER BY id ASC LIMIT $2
                    """, current_id, self.batch_size)

                    if not rows:
                        break

                    # Batch update within chunk boundary
                    await conn.executemany("""
                        UPDATE users 
                        SET full_name = TRIM(CONCAT(COALESCE($2, ''), ' ', COALESCE($3, '')))
                        WHERE id = $1
                    """, [(r["id"], r["first_name"], r["last_name"]) for r in rows])

                    current_id = rows[-1]["id"]
                    total_migrated += len(rows)

            # Adaptive throttling based on replication lag
            lag = await self.get_replication_lag_ms()
            delay = self.base_delay
            if lag > self.max_lag_ms:
                # Exponential penalty backoff when replica is struggling
                delay = self.base_delay * (2.0 ** min(5, (lag / self.max_lag_ms)))

            await asyncio.sleep(delay)

        return total_migrated
```

---

## 🔒 5. Disiplin Eksekusi (Zero-Overengineering & Ponytail Invariants)

1. **No ORM Magic for High-Traffic DDL:** Jalankan DDL migrasi skema kritis melalui migration script raw SQL murni yang eksplisit, terisolasi, dan ber-timeout deterministik.
2. **Deterministic Parity Assertion:** Cutover membaca baru hanya boleh diaktifkan jika delta divergensi bernilai absolut 0:
   $$\Delta_{\text{divergence}} = \text{COUNT}(\{ r \in R \mid \text{Hash}(r.\text{new}) \neq \text{Hash}(\text{Transform}(r.\text{old})) \}) == 0$$
3. **Single Root Fix Discipline:** Eliminasi kegagalan skema di level basis data (triggers/constraints), bukan menambal race condition di lapisan web server.
4. **Clean File Limit:** Tetap padat, modular, dan $<300$ baris per file.
