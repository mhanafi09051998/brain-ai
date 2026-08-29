# Neuron N031: Modern Data Architecture & Hybrid Search (PostgreSQL 17, pgvector HNSW, Drizzle ORM, SQLite WAL)

Prinsip rancang bangun arsitektur data modern, komputasi hybrid search (BM25 + Dense Vectors), migrasi skema bebas downtime, ketahanan koneksi transaksional ACID, dan eksekusi query sub-10 milidetik:

- **Kategori:** Modern Data Engineering, Vector Databases & High-Performance Storage
- **Tanggal Sintesis:** 2026-08-24
- **Status:** Active Operational Invariant
- **Synaptic Links:** [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N011`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N011_mechanical_sympathy_perf.md), [`N012`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N012_deep_search_and_graph_rag.md), [`N013`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N013_deep_storage_and_distributed_db.md)

---

## 🔍 1. Hybrid Search Architecture: PostgreSQL 17 + pgvector HNSW + BM25

Arsitektur pencarian modern mengkombinasikan kekuatan *Lexical/Exact Match* (BM25 / Full-Text Search) dengan *Semantic/Conceptual Match* (Dense Vector Embedding) dalam satu mesin basis data terpadu tanpa fragmentasi infrastruktur (eliminasi kompleksitas sinkronisasi Elasticsearch/Pinecone eksternal).

### A. Vector Indexing: HNSW (Hierarchical Navigable Small World)
1. **Parameter HNSW di pgvector**:
   - `m` (Maksimum link dua arah per node): Default 16 (rekomendasi: $16 \le m \le 64$). Semakin tinggi $m$, semakin tinggi akurasi recall dan penggunaan RAM.
   - `ef_construction` (Ukuran dynamic candidate list saat index build): Default 64 (rekomendasi: $128 \le \text{ef\_construction} \le 256$) untuk recall $\ge 98\%$.
   - `hnsw.ef_search` (Ukuran dynamic candidate list saat querying runtime): Default 40. Sesuaikan per query via `SET LOCAL hnsw.ef_search = 100;` saat membutuhkan high-precision recall.

2. **Distance Operators & Normalisasi**:
   - Cosine Distance (`<=>`): $1 - \frac{u \cdot v}{\|u\|_2 \|v\|_2}$. Ideal untuk unnormalized embeddings (mis. OpenAI `text-embedding-3`).
   - Inner Product (`<#>`): $-(u \cdot v)$. Sangat cepat untuk vektor yang telah di-*L2-normalized* unit length.
   - L2 Squared Distance (`<->`): $\|u - v\|_2^2$.

```sql
-- Inisialisasi pgvector dan indeks HNSW di PostgreSQL 17
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    tsv_content TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    embedding VECTOR(1536) NOT NULL
);

-- Indeks HNSW Vektor dengan Cosine Distance
CREATE INDEX idx_documents_embedding_hnsw 
ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 24, ef_construction = 128);

-- Indeks GIN untuk Lexical BM25 / Full-Text Search
CREATE INDEX idx_documents_tsv 
ON documents USING gin (tsv_content);
```

---

### B. Reciprocal Rank Fusion (RRF) Invariant
Menggabungkan dua daftar ranking independen (Dense Vector dan Sparse BM25) tanpa memerlukan kalibrasi normalisasi skor absolut (yang rentan terhadap distribusi nilai tak seimbang).

$$\text{RRF\_Score}(d) = \sum_{m \in \{\text{dense}, \text{sparse}\}} \frac{w_m}{k + r_m(d)}$$

- $r_m(d) \in [1, N]$: Urutan peringkat dokumen $d$ pada metode $m$.
- $k$: Konstanta penstabil / smoothing (standar: $k = 60$). Mencegah dokumen berperingkat 1 mendominasi dokumen yang konsisten di peringkat atas pada kedua metode.
- $w_m$: Bobot relatif ($w_{\text{dense}} = 0.6, w_{\text{sparse}} = 0.4$).

```sql
-- Single-Roundtrip Hybrid RRF Query (PostgreSQL CTE)
WITH dense_search AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> $1::vector) AS rank
    FROM documents
    ORDER BY embedding <=> $1::vector
    LIMIT 50
),
sparse_search AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank_cd(tsv_content, plainto_tsquery('english', $2)) DESC) AS rank
    FROM documents
    WHERE tsv_content @@ plainto_tsquery('english', $2)
    LIMIT 50
)
SELECT 
    d.id,
    d.content,
    d.metadata,
    COALESCE(1.0 / (60 + ds.rank), 0.0) * 0.6 + 
    COALESCE(1.0 / (60 + ss.rank), 0.0) * 0.4 AS rrf_score
FROM documents d
LEFT JOIN dense_search ds ON d.id = ds.id
LEFT JOIN sparse_search ss ON d.id = ss.id
WHERE ds.id IS NOT NULL OR ss.id IS NOT NULL
ORDER BY rrf_score DESC
LIMIT 10;
```

---

## 🛠️ 2. Zero-Bloat Schema Migrations: Drizzle ORM Invariants

Drizzle ORM dipilih karena arsitekturnya yang **Zero-Overhead, Type-Safe, dan Direct SQL Dialect Mapping** (tanpa active-record memory bloat, tanpa runtime query parsing engine raksasa layaknya Prisma).

### A. Drizzle Schema Declaration
```typescript
import { pgTable, bigserial, text, jsonb, customType, index } from "drizzle-orm/pg-core";
import { sql } from "drizzle-orm";

// Custom type-safe pgvector field definition
const vector1536 = customType<{ data: number[]; driverData: string }>({
  dataType() {
    return "vector(1536)";
  },
  toDriver(value: number[]): string {
    return JSON.stringify(value);
  },
  fromDriver(value: string): number[] {
    return JSON.parse(value);
  },
});

export const documents = pgTable("documents", {
  id: bigserial("id", { mode: "number" }).primaryKey(),
  content: text("content").notNull(),
  metadata: jsonb("metadata").$type<Record<string, unknown>>().default({}),
  embedding: vector1536("embedding").notNull(),
}, (table) => ({
  hnswIdx: index("idx_docs_hnsw").using("hnsw", table.embedding.asc().op("vector_cosine_ops")),
}));
```

### B. Invarian Zero-Downtime Safe Migration
1. **No Exclusive Table Locks**:
   - Jangan pernah menambahkan kolom `NOT NULL` tanpa default value pada tabel produksi besar dalam 1 langkah (PostgreSQL 11+ mendukung default konstan tanpa rewrite tabel, tetapi `NOT NULL` tanpa default memicu full table scan/lock).
   - Selalu buat indeks secara concurrently: `CREATE INDEX CONCURRENTLY` untuk mencegah penolakan write transaksi aktif.
2. **Lock Timeout Guarding**:
   - Setiap script migrasi DDL wajib diawali dengan batasan timeout lock untuk mencegah lock-queue starvation:
     ```sql
     SET lock_timeout = '2s';
     SET statement_timeout = '30s';
     ```
3. **Expand-and-Contract Pattern (Dual-Writing)**:
   - Tahap 1 (*Expand*): Tambahkan kolom baru (nullable). Update ORM untuk menulis ke kolom lama dan kolom baru (*dual-write*).
   - Tahap 2 (*Backfill*): Migrasi data lama secara asynchronous bertahap (*batched cursor chunk* $N=1000$).
   - Tahap 3 (*Contract*): Alihkan pembacaan ke kolom baru, hentikan penulisan kolom lama, lalu `DROP COLUMN` secara aman.

---

## ⚡ 3. ACID-Resilient Connection Pooling & Concurrency

### A. PostgreSQL Connection Sizing (Little's Law)
Koneksi basis data adalah proses berbobot berat (*heavyweight fork process*) yang mengkonsumsi $\approx 5\text{--}10\text{ MB RAM}$ dan memicu context-switching CPU jika jumlah koneksi aktif melebihi kapasitas thread core.

$$\text{Optimal Pool Size} = (\text{CPU Cores} \times 2) + \text{Effective Spindle / SSD Concurrency}$$

- **PgBouncer Invariants**:
  - Gunakan mode `pool_mode = transaction` untuk OLTP web application throughput maksimal.
  - Hindari session-level prepared statement collision pada transaction mode (gunakan generic parameter query protocol atau client-side unnamed prepared statements).
  - Batasi pooler client timeout: `query_timeout = 10s`, `client_idle_timeout = 60s`.

---

### B. SQLite WAL (Write-Ahead Logging) Engine Invariants
Untuk embedded, edge, atau standalone microservices (seperti MojoLoker & Zolu internal services), SQLite dengan konfigurasi WAL mode memberikan performa transaksional ekstrem ($\ge 50{,}000\text{ reads/sec}$, sub-1ms).

```sql
-- Konfigurasi Wajib SQLite WAL High-Performance
PRAGMA journal_mode = WAL;          -- Memungkinkan Concurrent Readers + 1 Concurrent Writer
PRAGMA synchronous = NORMAL;        -- Menjamin ACID durability dengan fsync optimal saat WAL checkpoint
PRAGMA busy_timeout = 5000;         -- 5 detik retry otomatis saat ada lock contention (mencegah SQLITE_BUSY)
PRAGMA cache_size = -64000;         -- Alokasi 64 MB RAM cache (nilai negatif = KiB)
PRAGMA temp_store = MEMORY;         -- Simpan temporary table & sorting index di RAM
PRAGMA mmap_size = 268435456;       -- 256 MB Memory-Mapped I/O untuk zero-copy page reads
PRAGMA foreign_keys = ON;           -- Enforce relational constraint integrity
```

- **Single-Writer Multi-Reader Rule**:
  - Reader tidak pernah memblokir Writer; Writer tidak pernah memblokir Reader.
  - Pastikan WAL file (`.db-wal`) tidak membengkak melebihi batas: jadwalkan `PRAGMA wal_autocheckpoint = 1000;` atau passive checkpointing `PRAGMA wal_checkpoint(PASSIVE);`.

---

## 🚀 4. Sub-10ms Transactional Query Optimization

1. **Covering Indexes & Index-Only Scans**:
   - Manfaatkan klausa `INCLUDE` pada PostgreSQL B-tree index untuk menyertakan payload kolom yang sering dibaca sehingga menghindari akses heap disk page (*Zero Heap Fetch*):
     ```sql
     CREATE INDEX idx_users_active_lookup 
     ON users (status, created_at DESC) 
     INCLUDE (id, username, email);
     ```
2. **Partial Indexes for Hot Partitions**:
   - Hindari pengindeksan data usang (*cold records* / soft-deleted records):
     ```sql
     CREATE INDEX idx_orders_unprocessed 
     ON orders (created_at) 
     WHERE status = 'PENDING';
     ```
3. **Disable JIT for Ultra-Fast OLTP**:
   - JIT Compilation di PostgreSQL menambah kompilasi query overhead $\sim 5\text{--}15\text{ ms}$. Untuk query OLTP sub-10ms, pastikan `jit = off` di parameter connection pooler.
4. **Batched Mutations**:
   - Gunakan multi-row insert berparameter tunggal (`INSERT ... VALUES (...), (...)`) atau PostgreSQL `UNNEST` array parameter untuk throughput insert $> 10{,}000\text{ rows/sec}$.

---

## 💻 Pure Python Runnable Implementation (Stdlib Zero-Dependency)

Implementasi deterministik algoritma Reciprocal Rank Fusion (RRF), komputasi Cosine/L2/Inner-Product distance, dan verifikasi SQLite WAL multi-reader/writer:

```python
"""
Neuron N031: Modern Data Architecture & Hybrid Search Invariant Suite
Standard Library Pure Python - Self-Checking Executable Model
"""

import sys
import math
import sqlite3
import tempfile
import os
import threading
import time
from typing import List, Dict, Tuple, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# ==========================================
# 1. Vector Distance Metric Calculators
# ==========================================
def vector_cosine_distance(u: List[float], v: List[float]) -> float:
    dot = sum(a * b for a, b in zip(u, v))
    norm_u = math.sqrt(sum(a * a for a in u))
    norm_v = math.sqrt(sum(b * b for b in v))
    if norm_u == 0.0 or norm_v == 0.0:
        return 1.0
    cosine_sim = dot / (norm_u * norm_v)
    return 1.0 - max(-1.0, min(1.0, cosine_sim))

def vector_l2_squared_distance(u: List[float], v: List[float]) -> float:
    return sum((a - b) ** 2 for a, b in zip(u, v))

def vector_inner_product(u: List[float], v: List[float]) -> float:
    return -sum(a * b for a, b in zip(u, v))  # Negative for ascending ranking order

# ==========================================
# 2. Reciprocal Rank Fusion (RRF) Engine
# ==========================================
def reciprocal_rank_fusion(
    dense_ranks: List[int],    # List of doc_ids ordered by vector similarity
    sparse_ranks: List[int],   # List of doc_ids ordered by BM25/FTS score
    k: int = 60,
    w_dense: float = 0.6,
    w_sparse: float = 0.4
) -> List[Tuple[int, float]]:
    scores: Dict[int, float] = {}
    
    # Process Dense Ranks
    for rank_idx, doc_id in enumerate(dense_ranks, start=1):
        rrf_val = w_dense / (k + rank_idx)
        scores[doc_id] = scores.get(doc_id, 0.0) + rrf_val
        
    # Process Sparse Ranks
    for rank_idx, doc_id in enumerate(sparse_ranks, start=1):
        rrf_val = w_sparse / (k + rank_idx)
        scores[doc_id] = scores.get(doc_id, 0.0) + rrf_val
        
    # Sort descending by fused RRF score
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_docs

# ==========================================
# 3. SQLite WAL High-Concurrency Verification
# ==========================================
def verify_sqlite_wal_engine() -> Dict[str, Any]:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    results = {"readers_success": 0, "writer_success": 0, "wal_verified": False}
    try:
        # Initial connection: Setup WAL & Schemas
        conn = sqlite3.connect(db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("CREATE TABLE records (id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT, val REAL);")
        conn.execute("CREATE INDEX idx_records_val ON records (val);")
        
        # Verify journal mode is WAL
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0].upper()
        results["wal_verified"] = (mode == "WAL")
        conn.close()

        # Concurrency Test: 4 Readers + 1 Writer simultaneously
        def reader_task(reader_id: int):
            c = sqlite3.connect(db_path, timeout=5.0)
            c.execute("PRAGMA busy_timeout = 5000;")
            for _ in range(50):
                cur_r = c.cursor()
                cur_r.execute("SELECT COUNT(*), AVG(val) FROM records WHERE val >= 0;")
                _ = cur_r.fetchone()
                time.sleep(0.001)
            c.close()
            results["readers_success"] += 1

        def writer_task():
            c = sqlite3.connect(db_path, timeout=5.0)
            c.execute("PRAGMA busy_timeout = 5000;")
            for i in range(100):
                c.execute("INSERT INTO records (payload, val) VALUES (?, ?);", (f"item_{i}", float(i * 1.5)))
                c.commit()
                time.sleep(0.001)
            c.close()
            results["writer_success"] += 1

        threads = []
        for i in range(4):
            t = threading.Thread(target=reader_task, args=(i,))
            threads.append(t)
        t_writer = threading.Thread(target=writer_task)
        threads.append(t_writer)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

    finally:
        for ext in ["", "-wal", "-shm"]:
            p = db_path + ext
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    return results

# ==========================================
# Invariant Test Suite Execution
# ==========================================
def run_all_invariants():
    print("==================================================")
    print("  Neuron N031: Modern Data Architecture Invariant Suite")
    print("==================================================")

    # 1. Test Distance Metrics
    u = [1.0, 2.0, 3.0]
    v = [1.0, 2.0, 3.0]
    cos_dist = vector_cosine_distance(u, v)
    l2_dist = vector_l2_squared_distance(u, v)
    assert math.isclose(cos_dist, 0.0, abs_tol=1e-6), "Identical vectors must have cosine distance 0"
    assert math.isclose(l2_dist, 0.0, abs_tol=1e-6), "Identical vectors must have L2 squared distance 0"
    print("  [✓] Vector Distance Metrics: Cosine & L2-Squared verified.")

    # 2. Test Hybrid RRF Search
    # Document 101 ranks #1 in Dense, #3 in Sparse
    # Document 102 ranks #2 in Dense, #1 in Sparse
    # Document 103 ranks #10 in Dense, #2 in Sparse
    dense_results = [101, 102, 104, 105, 103]
    sparse_results = [102, 103, 101, 106, 107]
    fused = reciprocal_rank_fusion(dense_results, sparse_results, k=60, w_dense=0.6, w_sparse=0.4)
    top_doc, top_score = fused[0]
    assert top_doc in (101, 102), f"Top doc should be high rank on both sets, got {top_doc}"
    assert len(fused) == 7, "Total unique docs should be 7"
    print(f"  [✓] Hybrid Search RRF: Fused rank #1 doc={top_doc} (score={top_score:.5f}).")

    # 3. Test SQLite WAL Concurrency
    wal_res = verify_sqlite_wal_engine()
    assert wal_res["wal_verified"], "SQLite journal_mode must be WAL"
    assert wal_res["readers_success"] == 4, "All 4 concurrent readers must succeed"
    assert wal_res["writer_success"] == 1, "Writer must complete 100 transactions without lock error"
    print(f"  [✓] SQLite WAL Concurrency: 4 Readers + 1 Writer passed without lock contention.")

    print("--------------------------------------------------")
    print("  ALL N031 MODERN DATA STORAGE INVARIANTS SATISFIED [PASS]")
    print("==================================================")

if __name__ == "__main__":
    run_all_invariants()
```
