---
name: distributed-systems
description: High-precision engineering reference for distributed invariants, consensus protocols, transaction patterns (SAGA, Outbox, 2PC), and resilient traffic control algorithms.
---

# Distributed Systems Architecture & Empirical Invariants

Designing distributed systems requires treating network partitions, partial failures, asynchronous clock drifts, and concurrent mutations as unavoidable ground realities.

---

## 1. Core Distributed Invariants & Guarantees

### A. The CAP & PACELC Theorems
- **CAP Theorem (Brewer / Gilbert & Lynch)**: In the presence of a network Partition ($P$), a distributed data store must trade off between Consistency ($C$, linearizability / single-copy consistency) and Availability ($A$, every non-failing node returns a non-error response without guarantee of latest data).
  - **CP Systems** (e.g., Raft, etcd, ZooKeeper): Reject or stall writes/reads when a majority quorum cannot be established to avoid split-brain or stale states.
  - **AP Systems** (e.g., Cassandra, DynamoDB with eventual consistency): Accept reads/writes on available partitions, resolving divergence later (e.g., Last-Write-Wins, CRDTs, Vector Clocks).
- **PACELC Theorem (Abadi)**: Extends CAP by defining trade-offs during normal operations:
  - If there is a **P**artition: trade off **A**vailability vs **C**onsistency.
  - **E**lse (normal state): trade off **L**atency vs **C**onsistency.
  - Classification Examples:
    - **PC/EC** (e.g., Spanner, CockroachDB): Prefers consistency during partition, and consistency over latency in normal operation.
    - **PA/EL** (e.g., DynamoDB default, Cassandra): Prefers availability during partition, and low latency over strong consistency in normal operation.
    - **PC/EL** (e.g., MongoDB primary writes): Consistent under partition, low latency under normal execution.

### B. Idempotency Keys (At-Least-Once to Exactly-Once Semantics)
- **Problem**: Network timeouts or retries cause duplicate execution of non-idempotent operations (e.g., payment charging, inventory deduction).
- **Architecture**:
  1. Client generates unique `Idempotency-Key` (UUIDv4 or cryptographic hash of deterministic payload).
  2. Server attempts atomic insert of key into an idempotency table or distributed key-value store with `STATUS = PROCESSING` and a TTL.
  3. If unique constraint violation occurs:
     - If `PROCESSING`: Return `409 Conflict` or poll until finished.
     - If `COMPLETED`: Return cached response directly without re-executing business logic.
  4. On successful execution: Store final response and set `STATUS = COMPLETED` inside the same database transaction.
- **SQL Invariant Pattern**:
```sql
-- Atomic acquisition & result retrieval
INSERT INTO idempotency_records (key, status, response_body, created_at, expires_at)
VALUES ($1, 'PROCESSING', NULL, NOW(), NOW() + INTERVAL '5 minutes')
ON CONFLICT (key) DO NOTHING;
```

### C. Transactional Outbox Pattern (Dual-Write Problem Resolution)
- **Problem**: Writing to a local database and publishing a message to a broker (Kafka/RabbitMQ) across network boundaries cannot be atomically committed without distributed transactions.
- **Invariant Solution**:
  1. Business entity mutation and event creation are written to the **same local database transaction** (in the `outbox` table).
  2. An asynchronous worker process (CDC via Debezium/WAL reader or polling relay) tails the outbox table and publishes events to the broker.
  3. The broker receives events with **at-least-once delivery guarantee**. Consumers must implement idempotency.
- **Data Flow**:
```
[Client] -> (Begin Tx) -> [Update State & INSERT INTO outbox] -> (Commit Tx)
                                   |
                         (CDC / Polling Relay)
                                   v
                             [Event Broker] -> [Downstream Consumers]
```

---

## 2. Distributed Transactions & Consistency Workflows

### A. SAGA Pattern (Long-Running Distributed Transactions)
Replaces ACID transactions with a sequence of local transactions where each step updates data within a single service. If a step fails, compensating transactions are executed in reverse order.

| Criterion | Orchestration-Based SAGA | Choreography-Based SAGA |
| :--- | :--- | :--- |
| **Control Flow** | Central orchestrator directs sub-services via explicit command/reply. | Decentralized; services react to domain events published by peers. |
| **Coupling** | Services coupled to orchestrator contract; orchestrator knows full workflow. | Low coupling; services only subscribe to specific events. |
| **Complexity** | Centralized state machine logic; easy to inspect, trace, and debug. | Emergent workflow; cyclic dependencies and tracing become complex at scale. |
| **Failure Handling** | Orchestrator coordinates compensations deterministically. | Each service must listen to failure events and trigger local compensations. |
| **Best Fit** | Complex, multi-step workflows with strict branching logic (e.g., checkout/booking). | Simple workflows (2-4 steps) with independent event lifecycles. |

#### Invariants of Compensating Transactions:
1. **Semantic Rollback**: Compensations do not restore binary state; they apply a logical undo (e.g., issue refund instead of un-writing payment row).
2. **Pivot Transactions**: The go/no-go step. Once the pivot transaction commits, subsequent steps **must** succeed (retry until success; no further compensation allowed).
3. **Idempotency & Commutativity**: Every compensation must be safe to execute multiple times upon worker retries.

### B. Two-Phase Commit (2PC) & Failure Modes
- **Protocol Flow**:
  1. **Prepare Phase**: Coordinator sends `PREPARE` to all participants. Participants lock local resources, write to undo/redo logs, and vote `YES` or `NO`.
  2. **Commit Phase**: If all vote `YES`, coordinator writes `COMMIT` to its WAL and broadcasts `COMMIT`. If any vote `NO` or timeout occurs, coordinator broadcasts `ABORT`.
- **Failure Modes & Blocking Nature**:
  - **Coordinator Failure during Commit Phase**: If the coordinator crashes after participants vote `YES`, participants remain in an **in-doubt / blocked state**, holding exclusive locks indefinitely. They cannot unilaterally abort or commit without risking inconsistency.
  - **Split-Brain & Partitions**: In the event of network partitions, 2PC blocks until communication is restored.
  - **Performance**: High latency and lock contention degrade throughput linearly with participant count ($O(N)$ synchronous lock duration).
- **Rule**: Avoid 2PC in distributed microservices; prefer Eventual Consistency, Outbox, and SAGA patterns.

---

## 3. Distributed Consensus: Raft Invariants

Raft achieves consensus across $N$ nodes by electing a single distinguished leader and granting it full authority to manage replicated logs. Fault tolerance: tolerates $F$ node failures where $N = 2F + 1$ (Quorum $Q = \lfloor N/2 \rfloor + 1$).

### A. Leader Election Invariants
1. **Term Monotonicity**: Terms act as logical clocks. Nodes only accept RPCs with `term >= currentTerm`. Stale terms force nodes to revert to Follower.
2. **Randomized Election Timeouts**: Followers wait a randomized timeout (e.g., 150ms–300ms) before transitioning to Candidate to prevent split-vote deadlocks.
3. **Majority Vote Quorum**: A candidate becomes leader only upon receiving votes from a strict majority ($> N/2$) for a single term. Each node grants at most one vote per term (First-Come-First-Served).
4. **Election Restriction (Up-to-Date Log)**: A follower denies vote if candidate's log is less up-to-date:
   - Higher last log term wins.
   - If terms are equal, longer log (larger last log index) wins.

### B. Log Replication & Safety Invariants
1. **Log Matching Property**:
   - If two entries in different logs have the same index and term, they store the same command.
   - If two entries in different logs have the same index and term, their logs are identical in all preceding entries.
2. **Leader Completeness Invariant**: If a log entry is committed in a given term, that entry will be present in the logs of the leaders for all higher-numbered terms.
3. **State Machine Safety**: If a server has applied a log entry at a given index to its state machine, no other server will ever apply a different log entry for the same index.
4. **Overwriting Follower Conflicts**: The leader never overwrites its own entries. It forces follower logs to duplicate its own by finding the latest matching entry and overwriting all diverging entries.

---

## 4. Rate Limiting & Load Shedding Algorithms

Protecting distributed services from cascading failures and thundering herds requires strict traffic shaping and adaptive admission control.

### A. Rate Limiting Algorithms Comparison

| Algorithm | Mechanism | Burst Tolerance | Memory / Overhead | Smoothness |
| :--- | :--- | :--- | :--- | :--- |
| **Token Bucket** | Tokens added at constant rate $R$ up to capacity $C$. Request consumes $k$ tokens. | Allows burst up to capacity $C$. | $O(1)$ space (stores `last_updated_time`, `token_count`). | High; absorbs bursts immediately, throttles sustained loads. |
| **Leaky Bucket** | Requests enter FIFO buffer of size $B$ and drain at fixed rate $R$. Overflow drops. | Buffers burst up to $B$, but enforces constant egress rate. | $O(B)$ memory (if buffering) or $O(1)$ (as leaky metering). | Perfect smoothness; removes traffic spikiness completely. |
| **Fixed Window Counter** | Counts requests in fixed time interval $[t, t+\Delta]$. Resets counter at boundary. | Vulnerable to $2\times$ burst at window boundaries. | $O(1)$ space (counter + timestamp). | Low; bursty traffic at window edges. |
| **Sliding Window Log** | Stores timestamp of every request in sorted set. Removes expired timestamps. | Zero boundary burst anomaly; exact rate limit enforcement. | $O(N)$ space where $N$ is request volume. High memory cost. | High precision. |
| **Sliding Window Counter** | Blends previous window count and current window count based on elapsed time weight: $\text{Count} = C_{\text{curr}} + C_{\text{prev}} \times (1 - \frac{t - t_{\text{curr}}}{\Delta})$. | Minimal boundary burst; smooth transition. | $O(1)$ space (stores 2 counters + current window timestamp). | High balance between memory efficiency and accuracy. |

### B. Load Shedding & Concurrency Invariants
1. **Rate Limiting vs Load Shedding**:
   - Rate limiting protects based on **client identity / quotas** (external rate).
   - Load shedding protects based on **server health & capacity** (internal queue saturation, CPU, p99 latency).
2. **Little's Law Invariant**: $L = \lambda \cdot W$ (Concurrency = Throughput $\times$ Latency).
   - When latency $W$ increases due to downstream stalls, maintaining constant concurrency limit $L$ forces throughput $\lambda$ to throttle, preventing queue exhaustion.
3. **Adaptive Concurrency Limits (CoDel / TCP Vegas principle)**:
   - Dynamically adjust max concurrent in-flight requests (In-Flight Limits) by measuring min round-trip latency ($\text{RTT}_{\text{min}}$) vs moving average latency ($\text{RTT}_{\text{current}}$).
   - If $\text{RTT}_{\text{current}} > 1.2 \times \text{RTT}_{\text{min}}$, decrease concurrency limit; otherwise probe upward.
4. **Admission Control Invariant**:
   - Reject unviable requests immediately at the edge / API gateway with `HTTP 429 Too Many Requests` (rate limited) or `HTTP 503 Service Unavailable` with `Retry-After` header. Never queue indefinitely.

---

## 5. Empirical Operational Checklist for Production
1. **Network is Unreliable**: Every RPC must have explicit connection timeouts, request deadlines (context timeout propagation), and jittered exponential backoff retries.
2. **Clock Drift Invariant**: Never rely on physical system wall-clock timestamps for causality or absolute ordering; use Logical Clocks (Lamport, Vector Clocks) or TrueTime (synchronized bounded uncertainty with commit-wait).
3. **Zero Partial Writes**: Guarantee atomicity across storage boundaries using Idempotency Keys + Transactional Outbox.
4. **Fast Failure over Slow Hanging**: Configure circuit breakers (e.g., fail-fast after consecutive error thresholds) to isolate cascading degraded dependencies.
