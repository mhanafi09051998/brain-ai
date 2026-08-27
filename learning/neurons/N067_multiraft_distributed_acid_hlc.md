# N067: Multi-Raft Partitioning, Distributed ACID Transactions & HLC Consensus

- **Kategori:** Distributed Systems, Distributed Consensus & Storage Engines
- **Tanggal Sintesis:** 2026-08-27
- **Status:** Active Operational Invariant

---

## 🎯 Core Invariants & Mathematical Formulations

### 1. Multi-Raft Key-Range Partitioning & Dynamic Split/Merge
- **Lexicographical Key Range:** Key space is partitioned into contiguous disjoint intervals $\mathcal{R}_i = [K_{\text{start}}, K_{\text{end}})$.
- **Independent Raft Group:** Every range $\mathcal{R}_i$ operates as an isolated Raft consensus group sharing physical node resources.
- **Atomic Range Split Algorithm:**
  1. Detect size/load breach: Range size $S(\mathcal{R}_i) \ge S_{\text{threshold}}$ (e.g., 64MB).
  2. Propose `SplitCommand(RangeID, SplitKey, NewRangeID, NewPeerIDs)` as an internal Raft log entry.
  3. On commit and state machine apply: Parent range updates right bound to $K_{\text{split}}$; Child range initializes with $[K_{\text{split}}, K_{\text{end}})$ using identical replicated state snapshot.
  4. Invariant: No write to $[K_{\text{split}}, K_{\text{end}})$ is acknowledged by the parent after split log commit index.

```
[ Node 1 ]       [ Node 2 ]       [ Node 3 ]
+-------------+  +-------------+  +-------------+
| Raft R1 (L) |->| Raft R1 (F) |->| Raft R1 (F) | (Range 1: [a-m))
| Raft R2 (F) |<-| Raft R2 (L) |->| Raft R2 (F) | (Range 2: [m-z))
+-------------+  +-------------+  +-------------+
```

### 2. Distributed ACID Transactions (2PC over Multi-Raft / Percolator Model)
- **Primary vs Secondary Intent Locks:**
  - Write transaction writes inline intent locks: $\text{Lock}(k, T_{\text{tx}}, \text{primary\_ref})$.
  - $\text{Tx}$ status is bound strictly to the state of its Primary Lock.
- **Two-Phase Commit Protocol over Raft:**
  - **Phase 1 (Prewrite):** Write locks & tentative MVCC values to all participant ranges via Raft consensus.
  - **Phase 2 (Commit):** 
    1. Commit Primary Lock by writing `CommitRecord(T_commit)` at $T_{\text{commit}} > T_{\text{read}}$.
    2. Asynchronously commit secondary locks. If reader sees secondary lock, it inspects the primary lock's commit status.
- **Deadlock Avoidance (Wound-Wait):**
  - If $\text{Tx}_A$ (timestamp $T_A$) requests lock held by $\text{Tx}_B$ ($T_B$):
    $$\text{Action} = \begin{cases} \text{Wound}(\text{Tx}_B) & \text{if } T_A < T_B \text{ (older transaction preempts younger)} \\ \text{Wait} & \text{if } T_A > T_B \text{ (younger waits)} \end{cases}$$

### 3. Hybrid Logical Clocks (HLC) & Strict Serializability
- **HLC Structure:** Tuple $(l_i, c_i)$ where $l_i$ is physical component and $c_i$ is logical counter.
- **HLC Invariant:** For any causally related events $e_1 \to e_2 \implies \text{HLC}(e_1) < \text{HLC}(e_2)$, bounded by physical clock drift $|l_i - \text{pt}_i| \le \epsilon_{\text{max}}$.
- **State Transition Equations:**
  - **Local Event:**
    $$l_i' = \max(l_i, \text{pt}_i), \quad c_i' = \begin{cases} c_i + 1 & \text{if } l_i' = l_i \\ 0 & \text{otherwise} \end{cases}$$
  - **Receive Message $(l_m, c_m)$:**
    $$l_i' = \max(l_i, l_m, \text{pt}_i), \quad c_i' = \begin{cases} \max(c_i, c_m) + 1 & \text{if } l_i' = l_i = l_m \\ c_i + 1 & \text{if } l_i' = l_i \\ c_m + 1 & \text{if } l_i' = l_m \\ 0 & \text{otherwise} \end{cases}$$
- **Read Uncertainty Window Guard:**
  If reading node encounters version with timestamp $T_{\text{ver}} \in (T_{\text{read}}, T_{\text{read}} + \epsilon_{\text{max}}]$, transaction must perform **Read Restart** at $T_{\text{ver}}$ to prevent phantom reads under bounded clock skew.

### 4. Spanner-Style Read Leases & Quorum Fencing
- **Leader Read Lease:** Leader serves linearizable reads locally without Raft round-trip if valid lease interval $[T_{\text{start}}, T_{\text{expire}})$ is active.
- **Safe Lease Renewal Guard:**
  $$\Delta t_{\text{elapsed}} + 2\epsilon_{\text{max}} < \Delta_{\text{lease\_duration}}$$
- **Fencing Token Invariant:** Every election generates monotonic Term/Epoch $E$. Storage engine rejects any state mutation with $E_{\text{mutation}} < E_{\text{fenced}}$.

```rust
// HLC and Lease Guard Invariant
pub struct HlcClock {
    physical: u64,
    logical: u32,
    max_offset: u64,
}

impl HlcClock {
    pub fn update(&mut self, msg_phys: u64, msg_log: u32, now_phys: u64) -> (u64, u32) {
        assert!(now_phys + self.max_offset >= self.physical, "Clock drift exceeded bounds!");
        let max_phys = self.physical.max(msg_phys).max(now_phys);
        if max_phys == self.physical && max_phys == msg_phys {
            self.logical = self.logical.max(msg_log) + 1;
        } else if max_phys == self.physical {
            self.logical += 1;
        } else if max_phys == msg_phys {
            self.logical = msg_log + 1;
        } else {
            self.logical = 0;
        }
        self.physical = max_phys;
        (self.physical, self.logical)
    }
}
```

---

## 🔍 Root Cause Analysis & Failure Mode Guards

| Failure Mode | Root Cause | Engineering Guard & Invariant |
| :--- | :--- | :--- |
| **Zombie Leader Silent Overwrite** | Network partition isolates old leader; it continues accepting writes without quorum awareness. | **Monotonic Fencing Tokens:** Storage engine validates epoch $E_{\text{term}}$ on disk commit; writes with stale term fail with `StaleLeaderEpoch`. |
| **Linearizability Violation via Clock Skew** | Node NTP drift exceeds $\epsilon_{\text{max}}$, violating HLC causality guarantee. | **Hard Self-Eviction:** Node panics/aborts if $|pt_{\text{local}} - pt_{\text{NTP}}| > \epsilon_{\text{threshold}}$ (e.g. > 250ms). |
| **Cascading Range Split Storm** | Monotonically increasing sequential keys hit single range boundary repeatedly. | **Predictive Split Pre-allocation:** Pre-split hot ranges using exponential key distribution heuristics. |
| **Orphaned Write Intents** | Coordinator crashes after Phase 1 Prewrite, leaving uncommitted locks blocking reads. | **Deterministic Lock Resolution:** Readers resolve dangling locks by querying primary lock; primary status determines rollback/commit. |

---

## 🔒 Execution Discipline (Ponytail YAGNI & Single Root Fix)
1. **Zero-Overengineering:** Do not implement TrueTime atomic clocks if Hybrid Logical Clocks (HLC) with bounded uncertainty restart satisfy serializability.
2. **Single Root Fix:** Enforce consensus safety at the Range Lease engine level rather than patching read-path retry loops in application drivers.
3. **Strict Boundary:** Maintain file length $< 300$ lines.
