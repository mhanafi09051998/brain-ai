# Neuron N051: Modern System Architecture, Resilience Engineering & Zero-Downtime DevOps Mastery

- **Kategori**: Distributed Systems, Resilience Engineering, Database Evolution & Zero-Downtime DevOps
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Mengeliminasi single point of failure (SPOF), data inconsistency (dual-write hazard), cascading outages, dan deployment downtime melalui integrasi Transactional Outbox + CDC, Resilience Primitives (Circuit Breaker, Bulkhead, Backpressure, Stripe Idempotency Key), Zero-Downtime Expand-and-Contract DB Migrations, Canary Traffic Routing, serta GitOps Zero-Trust Infrastructure & OpenTelemetry 4 Golden Signals.
- **Synaptic Links**: [`N001`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N001_executive_decisions.md), [`N002`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N002_vps_remote_ops.md), [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N007`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N007_self_improving_loop.md), [`N010`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N010_distributed_systems_design.md), [`N013`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N013_deep_storage_and_distributed_db.md), [`N028`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N028_autonomous_self_healing_chaos.md), [`N032`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N032_cloud_native_edge_infra.md)
- **Status**: Active Operational Invariant

---

## 1. Transactional Outbox Pattern & Change Data Capture (CDC)

Dalam sistem terdistribusi, **Dual-Write Anti-Pattern** (menulis ke database relasional lalu langsung mempublikasikan event ke message broker seperti Kafka/RabbitMQ dalam application code) adalah penyebab utama inkonsistensi data:
- Jika DB commit berhasil tetapi message broker crash/network timeout $\implies$ event hilang selamanya (*silent data loss*).
- Jika event terkirim tetapi DB commit gagal/rollback $\implies$ sistem downstream memproses event hantu (*phantom data*).

```
                      DUAL-WRITE ANTI-PATTERN (BAHAYA)
  [ Client ] ───► [ Service ] ───(1. Save DB)───► [ Database ] (Success)
                        │
                        └────────(2. Publish)───► [ Kafka Broker ] (FAIL / TIMEOUT)
                                                  (Data Inconsistent!)

               TRANSACTIONAL OUTBOX + CDC (ZERO INCONSISTENCY)
  [ Client ] ───► [ Service ] ───► [ Database (Single ACID Tx) ]
                                   ├─► [ Orders Table ]
                                   └─► [ Outbox Table ]
                                              │
                                              ▼ (Logical WAL Streaming)
                                   [ CDC Engine (Debezium) ]
                                              │
                                              ▼ (At-least-once)
                                   [ Message Broker (Kafka) ]
                                              │
                                              ▼
                                   [ Consumer Deduplication ] (Exactly-once semantics)
```

### A. Komponen Transactional Outbox
1. **Atomic Local Transaction**: State bisnis (`orders`, `payments`, `users`) dan event outbox (`outbox_events`) disimpan dalam transaksi ACID lokal tunggal pada database yang sama.
2. **Schema Outbox Minimal**:
   ```sql
   CREATE TABLE outbox_events (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       aggregate_type VARCHAR(64) NOT NULL,
       aggregate_id VARCHAR(128) NOT NULL,
       event_type VARCHAR(64) NOT NULL,
       payload JSONB NOT NULL,
       headers JSONB NOT NULL DEFAULT '{}',
       created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
       processed_at TIMESTAMPTZ NULL
   );
   CREATE INDEX idx_outbox_unprocessed ON outbox_events(created_at) WHERE processed_at IS NULL;
   ```
3. **Change Data Capture (CDC) Engine**: Membaca transaction log database secara asinkron (*PostgreSQL Logical Decoding / WAL2JSON / Debezium / MySQL binlog*) tanpa membebani query engine via polling.
4. **Consumer-Side Idempotent Deduplication**: Karena CDC menjamin *at-least-once delivery*, setiap consumer wajib memiliki tabel/cache deduplikasi berbasis `(message_id, consumer_group)` untuk memastikan semantik *exactly-once processing*.

---

## 2. Resilience Engineering: Cascading Outage Prevention

```
                     RESILIENCE DEFENSE STACK
                     
   Inbound Traffic ───► [ Token Bucket Rate Limiter ] ──(Exceeded?)──► 429 Too Many Requests
                               │ (Within quota)
                               ▼
                        [ Bulkhead Isolation ] ──────(Saturated?)─► 503 Overloaded
                               │ (Available slot)
                               ▼
                        [ Circuit Breaker ] ─────────(OPEN?)──────► Fast Fallback
                               │ (CLOSED / HALF-OPEN)
                               ▼
                        [ Idempotency Guard ] ───────(Duplicate?)─► Replay Cached Resp
                               │ (New Key)
                               ▼
                        [ Core Business Logic ]
```

### A. Circuit Breaker State Machine
Mencegah sistem membuang resource dengan terus memanggil downstream dependency yang sedang down:
- **CLOSED**: Seluruh request diteruskan ke downstream. Error dihitung dalam sliding window $W$. Jika error rate $\ge \theta_{\text{fail}}$ (misal 50%) atau latency $\ge L_{\text{slow}}$, state bertransisi ke **OPEN**.
- **OPEN**: Fail-fast seketika tanpa menyentuh downstream (mengembalikan error atau static fallback) selama durasi cooldown $T_{\text{sleep}}$. Setelah timeout, bertransisi ke **HALF-OPEN**.
- **HALF-OPEN**: Mengizinkan $N_{\text{trial}}$ request percobaan. Jika seluruh trial berhasil, kembali ke **CLOSED**; jika ada 1 trial gagal, kembali ke **OPEN**.

### B. Bulkhead Pattern (Isolasi Kompartemen)
- Memisahkan resource compute (thread pool, connection pool, semaphore) per downstream domain atau per tier tenant.
- Kerusakan total atau kelambatan pada satu downstream (misal: payment gateway lambat) tidak menghabiskan thread pool endpoint lain (misal: user login atau product catalog).

### C. Backpressure & Adaptive Load Shedding
- Mencegah memory ballooning dan queue saturation akibat ledakan traffic (*traffic spike*).
- **Token Bucket / Leaky Bucket**: Mengatur throughput rata-rata dan burstiness.
- **Queue CoDel / LIFO Shedding**: Saat queue latency melampaui SLA (misal $> 200\text{ms}$), buang request tertua atau tolak request baru dengan HTTP 429/503 daripada memperlambat seluruh antrean.

### D. Stripe-Standard Idempotency Keys
Standar industri untuk operasi non-idempotent (seperti `POST /v1/charges`):
1. **Header**: Klien mengirimkan header unik `Idempotency-Key: <UUID / Unique Hash>`.
2. **Payload Fingerprint**: Server menghitung SHA-256 hash dari `(HTTP Method, Path, Body)`.
3. **Atomic Lock & State Transition**:
   - Jika key belum ada: Simpan key dengan status `PROCESSING` dan hash payload dengan TTL (misal 24 jam).
   - Jika key ada dengan hash berbeda: Tolak seketika dengan `422 Unprocessable Entity` / `400 Bad Request` (deteksi penggunaan ulang key untuk payload berbeda).
   - Jika key ada dengan status `PROCESSING`: Kembalikan `409 Conflict` atau tunggu hingga transaksi pertama selesai (*concurrent request serialization*).
   - Jika key ada dengan status `RESOLVED`: Kembalikan response body dan status code yang telah dicache secara instan (*idempotent replay*).

---

## 3. Zero-Downtime Operations & Database Evolution

```
              EXPAND-AND-CONTRACT (PARALLEL RUN) MIGRATION
              
  Phase 1: EXPAND          Phase 2: DUAL-WRITE       Phase 3: BACKFILL
  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
  │ col: full_name│         │ col: full_name│◄─Write  │ col: full_name│
  │              │         │ col: first_name│◄─Write  │ col: first_name│◄──Async Copy
  │ col: first_name│(Null)   │ col: last_name │◄─Write  │ col: last_name │   Old -> New
  │ col: last_name │(Null)   └──────────────┘         └──────────────┘
  └──────────────┘
  
  Phase 4: READ SHIFT      Phase 5: STOP OLD WRITE   Phase 6: CONTRACT
  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
  │ col: full_name│(Unused) │ col: full_name│(Dead)   │              │
  │              │         │              │         │              │
  │ col: first_name│◄─Read   │ col: first_name│◄─R/W    │ col: first_name│◄─R/W
  │ col: last_name │◄─Read   │ col: last_name │◄─R/W    │ col: last_name │◄─R/W
  └──────────────┘         └──────────────┘         └──────────────┘
```

### A. Phased Database Evolution (Expand-and-Contract)
Dilarang keras melakukan `ALTER TABLE DROP/RENAME COLUMN` langsung pada database produksi aktif. Setiap perubahan skema wajib mengikuti 6 fase:
1. **Phase 1 (Expand)**: Tambahkan kolom baru bernilai nullable atau dengan default aman tanpa table lock.
2. **Phase 2 (Dual-Write)**: Update aplikasi untuk menulis ke kolom lama dan kolom baru secara bersamaan (atau via trigger DB).
3. **Phase 3 (Backfill)**: Jalankan background worker untuk memindahkan data historis dari kolom lama ke kolom baru dalam chunk kecil (misal $1000$ row/batch dengan sleep) agar tidak memicu lock contention atau replikasi lag.
4. **Phase 4 (Read Shift)**: Alihkan query pembacaan aplikasi ke kolom baru. Validasi konsistensi data.
5. **Phase 5 (Contract Writes)**: Hentikan seluruh penulisan ke kolom lama di kode aplikasi.
6. **Phase 6 (Contract Schema)**: Drop kolom lama secara aman (misal `ALTER TABLE ... DROP COLUMN` yang instant pada PostgreSQL modern).

### B. Canary Rollouts & Automated Rollback
```
  Traffic (100%) ───► [ Ingress Traffic Splitter ]
                             ├─── 95% ──► [ Stable Deployment v1.4.0 ]
                             └───  5% ──► [ Canary Deployment v1.5.0 ]
                                                │
                                                ▼ (Real-time Metric Probe)
                                         [ Prometheus / OTel ]
                                                │
                          (SLI Breach: Error > 0.5% OR Latency > 2x Baseline)
                                                │
                                                ▼
                                         [ AUTO-ROLLBACK ]
```
- **Traffic Phasing**: 1% $\to$ 5% $\to$ 25% $\to$ 50% $\to$ 100% dengan soaking time minimal 5–15 menit per fase.
- **Automated Rollback Oracles**:
  - Error rate spike: $\text{ErrorRate}_{\text{canary}} > \text{ErrorRate}_{\text{stable}} + 0.5\%$
  - Latency degradation: $p99_{\text{canary}} > 1.5 \times p99_{\text{stable}}$
  - System health crash: HTTP 500 / unhandled exceptions terdeteksi pada Canary $\implies$ Ingress langsung mematikan routing ke Canary dalam hitungan detik.

---

## 4. GitOps, Zero-Trust Infrastructure & OpenTelemetry

```
                 ZERO-TRUST WORKLOAD IDENTITY & TELEMETRY
                 
  [ Git Repository ] ──(Sync Loop)──► [ GitOps Engine (Argo/Flux) ] ──► [ Immutable Cluster ]
                                                                               │
  ┌────────────────────────────────────────────────────────────────────────────┴────────┐
  │ Workload Identity & Telemetry Mesh                                                  │
  │                                                                                     │
  │  [ Microservice A ] ───(mTLS / Short-Lived SPIRE SVID / OIDC Token)───► [ Microservice B ]
  │           │                                                                  │      │
  │           └───────────► [ W3C traceparent Context Propagation ] ─────────────┘      │
  │                                         │                                           │
  │                                         ▼                                           │
  │                         [ OpenTelemetry Collector ]                                 │
  │                         - Latency (p50, p90, p99)                                   │
  │                         - Traffic (RPS, Concurrency)                                │
  │                         - Errors (5xx, Exceptions)                                  │
  │                         - Saturation (CPU, Mem, Pool)                               │
  └─────────────────────────────────────────────────────────────────────────────────────┘
```

### A. GitOps & Immutable Infrastructure
- **Git Single Source of Truth**: Seluruh konfigurasi infrastruktur (K8s manifests, Caddyfile, Docker Compose, Terraform) didefinisikan secara deklaratif di Git.
- **Drift Reconciliation**: Engine otomatis mendeteksi deviasi manual (*drift*) dan mengembalikan konfigurasi cluster ke state yang didefinisikan di Git.
- **Immutable Artifacts**: Container image bersifat read-only (`readOnlyRootFilesystem: true`), non-root user, distroless base image, tanpa SSH daemon di container.

### B. Zero-Trust Workload Security
- **No Long-Lived Secrets**: Tidak ada API key atau password database statis yang disimpan dalam kode atau configmap.
- **Short-Lived Workload Identity**: Menggunakan OIDC token exchange (misal SPIFFE/SPIRE, AWS IAM Roles for Service Accounts / IRSA, Vault dynamic credentials) dengan masa berlaku $< 1$ jam.
- **Mutual TLS (mTLS)**: Enkripsi end-to-end antar-layanan dengan sertifikat X.509 yang dirotasi otomatis setiap 12–24 jam.

### C. OpenTelemetry 4 Golden Signals (Google SRE Standard)
1. **Latency**: Waktu yang dibutuhkan untuk melayani request. Wajib memisahkan latency request sukses vs request gagal.
2. **Traffic**: Beban permintaan pada sistem (RPS, I/O data rate, concurrent streams).
3. **Errors**: Tingkat kegagalan request, baik eksplisit (HTTP 5xx, DB connection failure) maupun implisit (HTTP 200 dengan empty body / degraded payload).
4. **Saturation**: Derajat utilisasi resource sistem yang paling terkendala (CPU utilization, RAM limit fraction, DB connection pool waiting queue depth, thread pool starvation).

### D. W3C Distributed Context Propagation
Setiap service hop wajib meneruskan header standar W3C:
```http
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
            (ver)-(       32-hex trace_id      )-( 16-hex parent_id )-(flags)
```

---

## 5. Implementasi Deterministik Python Standard Library

```python
"""
Neuron N051: Modern System Architecture, Resilience Engineering & Zero-Downtime DevOps Mastery.
Standard library only (math, time, hashlib, uuid, dataclasses, typing, collections). Zero external dependencies.
"""

import sys
import time
import math
import hashlib
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from collections import deque

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ============================================================================
# 1. Transactional Outbox Pattern & CDC Deduplication Engine
# ============================================================================

@dataclass
class OutboxEvent:
    id: str
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: Dict[str, Any]
    created_at: float
    processed_at: Optional[float] = None

class TransactionalOutboxManager:
    """
    Simulates Atomic Local Transactions (Entity + Outbox) and CDC Event Publishing
    with Consumer-Side Exactly-Once Idempotent Deduplication.
    """
    def __init__(self):
        self.entities_db: Dict[str, Dict[str, Any]] = {}
        self.outbox_table: Dict[str, OutboxEvent] = {}
        self.broker_messages: List[OutboxEvent] = []
        self.consumer_processed_events: set = set()

    def execute_transactional_write(self, aggregate_type: str, aggregate_id: str, 
                                     entity_data: Dict[str, Any], event_type: str, 
                                     event_payload: Dict[str, Any]) -> str:
        """Executes atomic DB write for both business data and outbox event."""
        # ACID atomic unit
        event_id = str(uuid.uuid4())
        event = OutboxEvent(
            id=event_id,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=event_payload,
            created_at=time.time(),
            processed_at=None
        )
        self.entities_db[aggregate_id] = entity_data
        self.outbox_table[event_id] = event
        return event_id

    def simulate_cdc_relay(self) -> int:
        """CDC Log Tailer captures unprocessed outbox rows and publishes to broker."""
        relayed_count = 0
        for event_id, event in list(self.outbox_table.items()):
            if event.processed_at is None:
                # Append to broker
                self.broker_messages.append(event)
                event.processed_at = time.time()
                relayed_count += 1
        return relayed_count

    def process_consumer_message(self, event: OutboxEvent, handler: Callable[[OutboxEvent], bool]) -> bool:
        """Consumer processes event with idempotent deduplication gate."""
        if event.id in self.consumer_processed_events:
            # Duplicate detected: skip processing without error
            return False
        success = handler(event)
        if success:
            self.consumer_processed_events.add(event.id)
        return success


# ============================================================================
# 2. Resilience Primitives: Circuit Breaker, Bulkhead, Backpressure
# ============================================================================

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    Sliding-Window Circuit Breaker with Failure Rate Threshold and Half-Open Trialing.
    """
    def __init__(self, failure_threshold_pct: float = 50.0, recovery_timeout_sec: float = 1.0, 
                 window_size: int = 10, half_open_trials: int = 3):
        self.failure_threshold_pct = failure_threshold_pct
        self.recovery_timeout_sec = recovery_timeout_sec
        self.window_size = window_size
        self.half_open_trials = half_open_trials
        
        self.state = CircuitState.CLOSED
        self.window: deque = deque(maxlen=window_size)
        self.last_state_change: float = time.time()
        self.half_open_successes: int = 0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        now = time.time()
        
        # State transition check from OPEN -> HALF_OPEN
        if self.state == CircuitState.OPEN:
            if now - self.last_state_change >= self.recovery_timeout_sec:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                self.half_open_successes = 0
            else:
                raise CircuitBreakerOpenException("Circuit is OPEN: fast-failing request")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as ex:
            self._on_failure()
            raise ex

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_successes += 1
            if self.half_open_successes >= self.half_open_trials:
                self.state = CircuitState.CLOSED
                self.window.clear()
                self.last_state_change = time.time()
        elif self.state == CircuitState.CLOSED:
            self.window.append(True)

    def _on_failure(self):
        now = time.time()
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.last_state_change = now
        elif self.state == CircuitState.CLOSED:
            self.window.append(False)
            if len(self.window) >= self.window_size:
                failures = self.window.count(False)
                fail_rate = (failures / len(self.window)) * 100.0
                if fail_rate >= self.failure_threshold_pct:
                    self.state = CircuitState.OPEN
                    self.last_state_change = now


class BulkheadFullException(Exception):
    pass

class Bulkhead:
    """Concurrency Isolation Guard to prevent resource starvation."""
    def __init__(self, max_concurrent_calls: int):
        self.max_concurrent_calls = max_concurrent_calls
        self.current_calls = 0

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        if self.current_calls >= self.max_concurrent_calls:
            raise BulkheadFullException(f"Bulkhead saturated: max {self.max_concurrent_calls} concurrent calls reached")
        self.current_calls += 1
        try:
            return func(*args, **kwargs)
        finally:
            self.current_calls -= 1


class TokenBucketRateLimiter:
    """Leaky Token Bucket for Backpressure and Rate Limiting."""
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.refill_rate = refill_rate_per_sec
        self.last_refill = time.time()

    def allow_request(self, tokens_required: float = 1.0) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        
        if self.tokens >= tokens_required:
            self.tokens -= tokens_required
            return True
        return False


# ============================================================================
# 3. Stripe-Standard Idempotency Key Engine
# ============================================================================

class IdempotencyState(Enum):
    PROCESSING = "PROCESSING"
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"

@dataclass
class IdempotencyRecord:
    key: str
    request_hash: str
    state: IdempotencyState
    response_code: Optional[int] = None
    response_body: Optional[Any] = None
    created_at: float = field(default_factory=time.time)

class StripeIdempotencyManager:
    """
    Standard Idempotency Manager:
    - Verifies SHA-256 payload integrity against key reuse mismatch (422)
    - Serializes concurrent in-flight requests (409 Conflict)
    - Instantly replays cached responses on identical duplicate requests
    """
    def __init__(self, ttl_sec: float = 86400.0):
        self.ttl_sec = ttl_sec
        self.records: Dict[str, IdempotencyRecord] = {}

    @staticmethod
    def compute_request_hash(method: str, path: str, body: str) -> str:
        data = f"{method.upper()}:{path}:{body}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def process(self, key: str, method: str, path: str, body: str, 
                handler: Callable[[], Tuple[int, Any]]) -> Tuple[int, Any, bool]:
        """
        Returns: (status_code, response_body, was_replayed)
        """
        now = time.time()
        req_hash = self.compute_request_hash(method, path, body)

        record = self.records.get(key)
        if record:
            # Check TTL
            if now - record.created_at > self.ttl_sec:
                del self.records[key]
                record = None

        if record:
            # 1. Payload Mismatch Guard
            if record.request_hash != req_hash:
                return (422, {"error": "Idempotency-Key already used with different request payload"}, False)
            
            # 2. In-Flight Concurrent Lock
            if record.state == IdempotencyState.PROCESSING:
                return (409, {"error": "Concurrent request in progress with same Idempotency-Key"}, False)
            
            # 3. Resolved Replay
            if record.state == IdempotencyState.RESOLVED:
                return (record.response_code or 200, record.response_body, True)

        # Register new in-flight lock
        new_record = IdempotencyRecord(
            key=key,
            request_hash=req_hash,
            state=IdempotencyState.PROCESSING,
            created_at=now
        )
        self.records[key] = new_record

        try:
            status_code, resp_body = handler()
            new_record.state = IdempotencyState.RESOLVED
            new_record.response_code = status_code
            new_record.response_body = resp_body
            return (status_code, resp_body, False)
        except Exception as ex:
            new_record.state = IdempotencyState.FAILED
            new_record.response_code = 500
            new_record.response_body = {"error": str(ex)}
            raise ex


# ============================================================================
# 4. Zero-Downtime Expand-and-Contract DB Migration Simulator
# ============================================================================

class MigrationPhase(Enum):
    PHASE_1_EXPAND = "EXPAND"
    PHASE_2_DUAL_WRITE = "DUAL_WRITE"
    PHASE_3_BACKFILL = "BACKFILL"
    PHASE_4_READ_SHIFT = "READ_SHIFT"
    PHASE_5_STOP_OLD_WRITE = "STOP_OLD_WRITE"
    PHASE_6_CONTRACT = "CONTRACT"

class ExpandContractSchemaManager:
    """
    Simulates phased online schema migration from `full_name` -> `(first_name, last_name)`
    without read/write downtime or locking.
    """
    def __init__(self):
        self.phase = MigrationPhase.PHASE_1_EXPAND
        # Database table simulation: id -> row dict
        self.rows: Dict[int, Dict[str, Any]] = {
            1: {"id": 1, "full_name": "Claudia Inovasi"},
            2: {"id": 2, "full_name": "Muhammad Hanafi"}
        }

    def write_user(self, user_id: int, full_name: str) -> None:
        """Application write path adapted to current migration phase."""
        first, *rest = full_name.split(" ", 1)
        last = rest[0] if rest else ""

        if self.phase in (MigrationPhase.PHASE_1_EXPAND,):
            # Old write only
            self.rows[user_id] = {"id": user_id, "full_name": full_name, "first_name": None, "last_name": None}
        elif self.phase in (MigrationPhase.PHASE_2_DUAL_WRITE, MigrationPhase.PHASE_3_BACKFILL, MigrationPhase.PHASE_4_READ_SHIFT):
            # Dual write to both old and new schema
            self.rows[user_id] = {"id": user_id, "full_name": full_name, "first_name": first, "last_name": last}
        elif self.phase in (MigrationPhase.PHASE_5_STOP_OLD_WRITE, MigrationPhase.PHASE_6_CONTRACT):
            # New write only
            self.rows[user_id] = {"id": user_id, "first_name": first, "last_name": last}

    def read_user_name(self, user_id: int) -> Tuple[str, str]:
        """Application read path adapted to current migration phase."""
        row = self.rows.get(user_id)
        if not row:
            raise KeyError("User not found")

        if self.phase in (MigrationPhase.PHASE_1_EXPAND, MigrationPhase.PHASE_2_DUAL_WRITE, MigrationPhase.PHASE_3_BACKFILL):
            # Read from legacy column
            full = row.get("full_name", "")
            parts = full.split(" ", 1)
            return (parts[0], parts[1] if len(parts) > 1 else "")
        else:
            # Read from new columns
            return (row.get("first_name", ""), row.get("last_name", ""))

    def execute_backfill_batch(self) -> int:
        """Asynchronously migrates legacy rows to new columns in safe chunks."""
        migrated = 0
        for row_id, data in self.rows.items():
            if data.get("first_name") is None and "full_name" in data and data["full_name"]:
                full = data["full_name"]
                first, *rest = full.split(" ", 1)
                data["first_name"] = first
                data["last_name"] = rest[0] if rest else ""
                migrated += 1
        return migrated


# ============================================================================
# 5. Canary Traffic Router with Automated Rollback Oracle
# ============================================================================

class CanaryRouter:
    """
    Weighted Canary Traffic Router with Automatic Circuit Rollback on Error SLI breach.
    """
    def __init__(self, canary_weight_pct: float = 5.0, error_threshold_pct: float = 1.0):
        self.canary_weight_pct = canary_weight_pct
        self.error_threshold_pct = error_threshold_pct
        self.stable_requests: List[bool] = []
        self.canary_requests: List[bool] = []
        self.is_rolled_back: bool = False

    def route_request(self, request_hash_int: int) -> str:
        """Routes request based on deterministic hash modulo."""
        if self.is_rolled_back:
            return "STABLE"
        slot = request_hash_int % 100
        return "CANARY" if slot < self.canary_weight_pct else "STABLE"

    def record_metric(self, target: str, is_success: bool) -> None:
        if target == "CANARY":
            self.canary_requests.append(is_success)
            self._evaluate_canary_health()
        else:
            self.stable_requests.append(is_success)

    def _evaluate_canary_health(self) -> None:
        if len(self.canary_requests) >= 10:
            failures = self.canary_requests.count(False)
            error_rate = (failures / len(self.canary_requests)) * 100.0
            if error_rate >= self.error_threshold_pct:
                self.is_rolled_back = True


# ============================================================================
# 6. OpenTelemetry Distributed Context & 4 Golden Signals
# ============================================================================

@dataclass
class TraceContext:
    version: str
    trace_id: str
    parent_id: str
    trace_flags: str

class W3CTraceContextPropagator:
    """Formats and parses standard W3C `traceparent` headers."""
    @staticmethod
    def generate(trace_id: Optional[str] = None) -> Tuple[TraceContext, str]:
        ver = "00"
        t_id = trace_id or uuid.uuid4().hex
        p_id = uuid.uuid4().hex[:16]
        flags = "01"
        header = f"{ver}-{t_id}-{p_id}-{flags}"
        return TraceContext(ver, t_id, p_id, flags), header

    @staticmethod
    def parse(header_value: str) -> Optional[TraceContext]:
        parts = header_value.strip().split("-")
        if len(parts) == 4 and len(parts[1]) == 32 and len(parts[2]) == 16:
            return TraceContext(parts[0], parts[1], parts[2], parts[3])
        return None


class GoldenSignalsCollector:
    """Collects and aggregates Google 4 Golden Signals: Latency, Traffic, Errors, Saturation."""
    def __init__(self):
        self.latencies_sec: List[float] = []
        self.request_count: int = 0
        self.error_count: int = 0
        self.current_concurrency: int = 0
        self.max_capacity: int = 100

    def record_call(self, latency: float, is_error: bool) -> None:
        self.latencies_sec.append(latency)
        self.request_count += 1
        if is_error:
            self.error_count += 1

    def compute_metrics(self) -> Dict[str, float]:
        n = len(self.latencies_sec)
        sorted_l = sorted(self.latencies_sec)
        p50 = sorted_l[int(n * 0.5)] if n > 0 else 0.0
        p99 = sorted_l[min(int(n * 0.99), n - 1)] if n > 0 else 0.0
        error_rate = (self.error_count / self.request_count) if self.request_count > 0 else 0.0
        saturation = self.current_concurrency / float(self.max_capacity)

        return {
            "traffic_total_requests": float(self.request_count),
            "error_rate_pct": error_rate * 100.0,
            "latency_p50_sec": p50,
            "latency_p99_sec": p99,
            "saturation_fraction": saturation
        }


# ============================================================================
# 7. Self-Contained Deterministic Verification Suite
# ============================================================================

def run_neuron_tests():
    """Runs all invariant verification tests for Neuron N051."""
    print("[*] Verifying Neuron N051: Modern Architecture, Resilience & Zero-Downtime DevOps...")

    # 1. Transactional Outbox + CDC Test
    outbox_mgr = TransactionalOutboxManager()
    evt_id = outbox_mgr.execute_transactional_write(
        aggregate_type="Order",
        aggregate_id="ord_1001",
        entity_data={"id": "ord_1001", "total": 250.0},
        event_type="OrderCreated",
        event_payload={"order_id": "ord_1001", "amount": 250.0}
    )
    assert evt_id in outbox_mgr.outbox_table, "Outbox table must contain event"
    assert len(outbox_mgr.broker_messages) == 0, "Broker must not have messages prior to CDC relay"
    
    relayed = outbox_mgr.simulate_cdc_relay()
    assert relayed == 1, "CDC relay must process 1 event"
    assert len(outbox_mgr.broker_messages) == 1, "Broker must now have 1 message"
    
    # Test Idempotent Consumer
    handler_executions = 0
    def dummy_handler(evt: OutboxEvent) -> bool:
        nonlocal handler_executions
        handler_executions += 1
        return True

    msg = outbox_mgr.broker_messages[0]
    res1 = outbox_mgr.process_consumer_message(msg, dummy_handler)
    res2 = outbox_mgr.process_consumer_message(msg, dummy_handler)  # duplicate
    assert res1 is True and res2 is False, "Duplicate event must be dropped by consumer gate"
    assert handler_executions == 1, "Handler must execute exactly once"

    # 2. Circuit Breaker Test
    cb = CircuitBreaker(failure_threshold_pct=50.0, recovery_timeout_sec=0.05, window_size=4, half_open_trials=2)
    def failing_fn(): raise RuntimeError("Downstream down")
    def passing_fn(): return "OK"

    # Trip the breaker
    for _ in range(2):
        try: cb.call(failing_fn)
        except RuntimeError: pass
    for _ in range(2):
        try: cb.call(failing_fn)
        except RuntimeError: pass

    assert cb.state == CircuitState.OPEN, "Circuit must be OPEN after exceeding failure threshold"

    # Fast fail in OPEN state
    try:
        cb.call(passing_fn)
        assert False, "Should have raised CircuitBreakerOpenException"
    except CircuitBreakerOpenException:
        pass

    # Wait for recovery timeout to test HALF_OPEN
    time.sleep(0.06)
    assert cb.call(passing_fn) == "OK"
    assert cb.state == CircuitState.HALF_OPEN
    assert cb.call(passing_fn) == "OK"
    assert cb.state == CircuitState.CLOSED, "Circuit must transition back to CLOSED after trial successes"

    # 3. Bulkhead Concurrency Guard Test
    bh = Bulkhead(max_concurrent_calls=2)
    bh.current_calls = 2
    try:
        bh.execute(passing_fn)
        assert False, "Should have raised BulkheadFullException"
    except BulkheadFullException:
        pass
    bh.current_calls = 0
    assert bh.execute(passing_fn) == "OK"

    # 4. Stripe Idempotency Key Manager Test
    idem = StripeIdempotencyManager()
    call_count = 0
    def charge_op():
        nonlocal call_count
        call_count += 1
        return (200, {"charge_id": "ch_999", "status": "paid"})

    # First call
    code1, body1, replayed1 = idem.process("key_abc", "POST", "/v1/charges", '{"amt":50}', charge_op)
    assert code1 == 200 and replayed1 is False and call_count == 1

    # Exact duplicate call -> instant replay without re-executing charge
    code2, body2, replayed2 = idem.process("key_abc", "POST", "/v1/charges", '{"amt":50}', charge_op)
    assert code2 == 200 and replayed2 is True and call_count == 1
    assert body2["charge_id"] == "ch_999"

    # Altered payload with same key -> 422 conflict
    code3, body3, replayed3 = idem.process("key_abc", "POST", "/v1/charges", '{"amt":100}', charge_op)
    assert code3 == 422 and "different request payload" in body3["error"]

    # 5. Phased Expand-and-Contract DB Migration Test
    mig_mgr = ExpandContractSchemaManager()
    
    # Phase 1: Expand
    mig_mgr.phase = MigrationPhase.PHASE_1_EXPAND
    mig_mgr.write_user(3, "Budi Santoso")
    assert mig_mgr.read_user_name(3) == ("Budi", "Santoso")

    # Phase 2: Dual Write & Phase 3: Backfill
    mig_mgr.phase = MigrationPhase.PHASE_2_DUAL_WRITE
    mig_mgr.write_user(4, "Dewi Lestari")
    mig_mgr.phase = MigrationPhase.PHASE_3_BACKFILL
    backfilled = mig_mgr.execute_backfill_batch()
    assert backfilled >= 2, "Backfill must migrate legacy rows"
    
    # Phase 4 & 5: Read Shift & Stop Old Write
    mig_mgr.phase = MigrationPhase.PHASE_4_READ_SHIFT
    assert mig_mgr.read_user_name(1) == ("Claudia", "Inovasi")
    mig_mgr.phase = MigrationPhase.PHASE_5_STOP_OLD_WRITE
    mig_mgr.write_user(5, "Eka Pratama")
    assert "full_name" not in mig_mgr.rows[5], "Legacy column must not be written in Phase 5"
    assert mig_mgr.read_user_name(5) == ("Eka", "Pratama")

    # 6. Canary Traffic Router & Automated Rollback Test
    canary = CanaryRouter(canary_weight_pct=10.0, error_threshold_pct=20.0)
    # Target canary routing
    assert canary.route_request(5) == "CANARY"
    assert canary.route_request(15) == "STABLE"

    # Trigger error SLI breach on Canary
    for _ in range(8): canary.record_metric("CANARY", True)
    for _ in range(3): canary.record_metric("CANARY", False)  # 3/11 = 27% error rate
    assert canary.is_rolled_back is True, "Canary must trigger automated rollback on SLI breach"
    assert canary.route_request(5) == "STABLE", "Post-rollback traffic must route 100% to STABLE"

    # 7. W3C Context Propagation & 4 Golden Signals Test
    ctx, header = W3CTraceContextPropagator.generate()
    parsed_ctx = W3CTraceContextPropagator.parse(header)
    assert parsed_ctx is not None and parsed_ctx.trace_id == ctx.trace_id

    metrics_collector = GoldenSignalsCollector()
    for lat in [0.010, 0.015, 0.020, 0.050, 0.200]:
        metrics_collector.record_call(lat, is_error=False)
    metrics_collector.record_call(0.300, is_error=True)
    
    metrics = metrics_collector.compute_metrics()
    assert metrics["traffic_total_requests"] == 6.0
    assert abs(metrics["error_rate_pct"] - (1/6 * 100.0)) < 1e-4
    assert metrics["latency_p50_sec"] > 0.0

    print("  [✓] Neuron N051 Invariants Verified: Transactional Outbox/CDC, Resilience, Idempotency, Expand-Contract DB, Canary, & OTel Signals.")

if __name__ == "__main__":
    run_neuron_tests()
```

---

## 6. Invarian Operasional & DevOps Guardrails

1. **Dual-Write Elimination Invariant**: Dilarang mempublikasikan distributed event langsung dari application logic tanpa *Transactional Outbox Pattern* atau CDC commit atomik.
2. **Mandatory Downstream Circuit Breaker**: Setiap remote RPC/HTTP dependency wajib dibungkus dengan *Circuit Breaker* dan *Bulkhead limit* untuk mencegah thread starvation dan cascading failures.
3. **Stripe Idempotency Gate**: Setiap mutasi resource yang menerima `Idempotency-Key` wajib memvalidasi hash payload (deteksi mismatch 422) dan mengembalikan cached response untuk duplikasi request.
4. **Zero-Lock Database Evolution**: Dilarang melakukan migrasi destruktif (drop/rename kolom) secara serentak; wajib melewati 6 fase *Expand-and-Contract* dengan background chunked backfilling.
5. **Automated Canary Rollback SLA**: Rollout produksi wajib memantau SLI error rate dan p99 latency secara real-time; deviasi $\ge 0.5\%$ pada error rate wajib memicu pembatalan otomatis dalam $< 30$ detik.
6. **Zero Static Credentials Invariant**: Seluruh workload antarlayanan wajib menggunakan token kriptografis jangka pendek (OIDC / SPIFFE-SPIRE / mTLS) dengan masa rotasi $< 24$ jam.
7. **W3C Distributed Tracing**: Setiap panggilan inter-service wajib menyertakan dan meneruskan header `traceparent` untuk korelasi distributed tracing end-to-end.
