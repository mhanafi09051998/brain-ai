# N068: Storage Engine Internals, LSM vs B-Link Trees, CDC Streaming & Hybrid Search

- **Kategori:** Storage Engine Internals, Event Streaming & Vector IR
- **Tanggal Sintesis:** 2026-08-27
- **Status:** Active Operational Invariant

---

## 🎯 Core Invariants & Mathematical Formulations

### 1. LSM-Tree Leveled Compaction vs B-Link Tree Concurrency
- **LSM-Tree Write Path & Amplification Formulations:**
  - Sequential append to WAL $\to$ Concurrent SkipList MemTable.
  - Flush MemTable to Immutable L0 SSTable when size $M \ge M_{\text{max}}$ (e.g. 64MB).
  - Bloom Filter bit allocation formula for target false positive probability $p$:
    $$m = -\frac{n \ln p}{(\ln 2)^2}, \quad k = \frac{m}{n} \ln 2$$
  - **Leveled Compaction Invariant:** Level $L_i$ size limit $C(L_i) = T^i \cdot C(L_0)$ (amplification factor $T \approx 10$). $L_0$ allows overlapping ranges; $L_1 \dots L_k$ maintain strictly disjoint key ranges.
  - Trade-off Bounds: Space Amplification $\text{SA} \approx 1.11$, Write Amplification $\text{WA} = O(T \cdot L)$, Read Amplification $\text{RA} = O(L)$ (with Bloom filter per SSTable).
- **B-Link Tree (Lehman-Yao Algorithm):**
  - High-key and right-link sibling pointers on internal and leaf pages.
  - Invariant: A search traversing a node being split does not lock or block; if target key $> \text{high\_key}$, concurrent reader follows `right_link` horizontally. Eliminates parent read-latching deadlocks.

```
LSM-Tree Flush & Compaction Flow:
[ MemTable (RAM) ] -> [ WAL (Disk) ]
        | (Flush)
 [ Level 0 SSTables (Overlapping) ]
        | (Compaction: Merge Sort)
 [ Level 1 SSTables (Disjoint: [A-D], [E-H], [I-M]) ]
        | (Compaction)
 [ Level 2 SSTables (Disjoint: 10x capacity) ]
```

### 2. Database WAL Streaming Internals (PostgreSQL & SQLite)
- **PostgreSQL Logical Decoding:**
  - WAL Stream identified by 64-bit Log Sequence Number ($\text{LSN}$).
  - Invariant: Replication slot holds catalog snapshot and prevents vacuum/WAL recycling until `confirmed_flush_lsn` is acknowledged by consumer.
- **SQLite WAL Concurrency:**
  - Append-only WAL frames indexed via `-shm` (Shared Memory hash table).
  - Invariant: Readers lock maximum committed transaction frame index $N_{\text{max}}$ at read start; writer appends frames without blocking concurrent snapshot readers.

### 3. Real-Time Change Data Capture (CDC) & Outbox Pattern
- **CDC Pipeline:** `Postgres WAL / SQLite WAL` $\to$ `Debezium Connector` $\to$ `Redpanda / NATS JetStream`.
- **Transactional Outbox Invariant:**
  - Application writes business state and outbox events in a single local ACID transaction:
    $$\text{BEGIN} \to \text{INSERT INTO orders} \to \text{INSERT INTO outbox_events} \to \text{COMMIT}$$
  - CDC tails `outbox_events` via WAL stream, guaranteeing exactly-once delivery semantics without dual-write inconsistency.

### 4. Hybrid Search: pgvector HNSW + BM25 Reciprocal Rank Fusion (RRF)
- **HNSW Graph Invariant:** Multi-layer geometric skip graph. Layer assignment follows exponential decay $P(l) = e^{-l \cdot m_L}$ with $m_L = 1/\ln(M)$. Greedy search on upper layers, bounded beam search (`efSearch`) on Layer 0.
- **BM25 Invariant:**
  $$\text{BM25}(D, Q) = \sum_{q \in Q} \text{IDF}(q) \cdot \frac{f(q, D) \cdot (k_1 + 1)}{f(q, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$
- **Reciprocal Rank Fusion (RRF) Formula:**
  $$\text{RRF\_Score}(d) = \sum_{m \in \{\text{vector}, \text{bm25}\}} \frac{1}{k + r_m(d)}, \quad \text{where } k \approx 60$$

```sql
-- Hybrid Vector + BM25 Search with Reciprocal Rank Fusion (RRF)
WITH vector_search AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> :query_embedding) AS rank
    FROM documents
    ORDER BY embedding <=> :query_embedding LIMIT 50
),
bm25_search AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank_cd(to_tsvector('english', content), plainto_tsquery('english', :query_text)) DESC) AS rank
    FROM documents
    WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :query_text) LIMIT 50
)
SELECT COALESCE(v.id, b.id) AS doc_id,
       COALESCE(1.0 / (60 + v.rank), 0.0) + COALESCE(1.0 / (60 + b.rank), 0.0) AS rrf_score
FROM vector_search v
FULL OUTER JOIN bm25_search b ON v.id = b.id
ORDER BY rrf_score DESC LIMIT 20;
```

---

## 🔍 Root Cause Analysis & Failure Mode Guards

| Failure Mode | Root Cause | Engineering Guard & Invariant |
| :--- | :--- | :--- |
| **LSM Write Stall / Freeze** | Flush thread lag or excessive L0 file accumulation ($> 20$ files) triggers compaction backpressure. | **Dynamic Ingestion Throttling:** Introduce token bucket write rate-limiter when $L_0$ count exceeds threshold; allocate dedicated background compaction workers. |
| **WAL Slot Disk Exhaustion** | Stalled CDC consumer prevents Postgres WAL recycling, consuming 100% disk space. | **Slot Safety Rail:** Set `max_slot_wal_keep_size = 64GB`. Auto-invalidate stale replication slots when disk capacity drops below safety threshold. |
| **HNSW Recall Degradation** | High volume of `UPDATE` / `DELETE` operations creates disconnected graph tombstones. | **Concurrent Reindexing:** Run periodic `REINDEX INDEX CONCURRENTLY` and configure vacuum thresholds for vector tables. |
| **CDC Duplicate Stream Processing** | Network reconnect re-emits unacknowledged CDC events to consumer. | **Idempotency Key Verification:** Consumers enforce unique `(lsn, tx_id, op_id)` deduplication filter window. |

---

## 🔒 Execution Discipline (Ponytail YAGNI & Single Root Fix)
1. **Zero-Overengineering:** Use native PostgreSQL WAL logical replication and pgvector before introducing external search clusters (Elasticsearch/Milvus).
2. **Single Root Fix:** Prevent dual-write race conditions at the architectural source via Transactional Outbox + CDC streaming.
3. **Strict Boundary:** Maintain file length $< 300$ lines.
