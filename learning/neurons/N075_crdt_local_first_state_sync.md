# N075: Conflict-Free Replicated Data Types (CRDT), Causal Vector Clocks & Merkle DAG Local-First Sync

- **Category:** Distributed Systems & Local-First Architecture
- **Date:** 2026-08-27
- **Status:** Active Operational Invariant

---

## 🎯 Core Invariants & Mathematical Framework

### 1. Join Semi-Lattice Formulations for State-based CRDTs (CvRDT)
A state-based Conflict-Free Replicated Data Type is defined as a bounded join semi-lattice $(\mathcal{S}, \sqcup, \le, \bot)$ where $\mathcal{S}$ is the state space, $\sqcup: \mathcal{S} \times \mathcal{S} \to \mathcal{S}$ is the merge operator, and $\bot \in \mathcal{S}$ is the bottom element.
- **Algebraic Semi-Lattice Invariants:**
  $$\forall x, y, z \in \mathcal{S}:$$
  $$\text{Associativity:} \quad (x \sqcup y) \sqcup z = x \sqcup (y \sqcup z)$$
  $$\text{Commutativity:} \quad x \sqcup y = y \sqcup x$$
  $$\text{Idempotence:} \quad x \sqcup x = x$$
- **Induced Partial Order & Monotonic Inflation:**
  $$x \le y \iff x \sqcup y = y, \quad \forall x, y \in \mathcal{S}: x \le x \sqcup y$$
  Every state transition $s \to s'$ generated locally must satisfy $s \le s'$ (monotonic growth). Convergence across any arbitrary asynchronous replication topology is guaranteed without distributed locks: $\lim_{t \to \infty} s_i(t) = \bigsqcup_{k \in \mathcal{R}} s_k(0)$.

### 2. Causal Vector Clocks & Concurrency Invariant
In a cluster of $N$ replicas $\mathcal{R} = \{r_1, r_2, \dots, r_N\}$, a vector clock is a vector $V \in \mathbb{N}^N$:
- **Causal Dominance & Concurrency:**
  $$V_a \le V_b \iff \forall k \in \mathcal{R}, \; V_a[k] \le V_b[k]$$
  $$V_a < V_b \iff (V_a \le V_b) \land (\exists k \in \mathcal{R}, \; V_a[k] < V_b[k]) \quad (a \text{ causally preceded } b)$$
  $$V_a \parallel V_b \iff \neg(V_a \le V_b) \land \neg(V_2 \le V_1) \quad (a \text{ and } b \text{ are strictly concurrent})$$
- **State Merging:** $(V_a \sqcup V_b)[k] = \max(V_a[k], V_b[k])$ for all $k \in \mathcal{R}$.

### 3. Observed-Remove Set (OR-Set) with Unique Causal Dots
To allow an element to be added, removed, and re-added concurrently without resurrection bugs or race conditions, each addition is tagged with a globally unique causal dot $d = (r, c) \in \mathcal{R} \times \mathbb{N}$.
- **State Structure:** $\sigma = (A, R)$, where $A, R \subseteq \mathcal{E} \times (\mathcal{R} \times \mathbb{N})$ ($A$ is Add-set, $R$ is Remove-set).
- **Observed Elements Predicate:**
  $$E(\sigma) = \{ e \in \mathcal{E} \mid \exists d: (e, d) \in A \land (e, d) \notin R \}$$
- **State Join ($\sqcup$):**
  $$(A_1, R_1) \sqcup (A_2, R_2) = (A_1 \cup A_2, R_1 \cup R_2)$$
- **Causal Remove Rule:** Removing $e$ at replica $r$ adds all currently observed dots of $e$ ($\{d \mid (e, d) \in A\}$) into $R$. A concurrent addition at replica $r'$ produces a distinct dot $d' \notin R$, ensuring add-wins semantics under concurrent mutations without losing updates.

### 4. Merkle DAG Local-First Synchronization Engine
In a local-first peer-to-peer network, state transitions are structured as an immutable directed acyclic graph (DAG) of content-addressed nodes.
- **Node Hash Invariant:**
  $$H(u) = \text{SHA256}\left(\text{Payload}(u) \;\|\; \text{Sort}\left(\bigcup_{p \in \text{Parents}(u)} H(p)\right)\right)$$
- **Delta-Sync Protocol:** Peers exchange only root hashes. If $H_{\text{root}}^A = H_{\text{root}}^B$, state is synchronized in $\mathcal{O}(1)$. If divergent, peers recursively traverse mismatched child hashes down to the common ancestor, exchanging only the symmetric set difference $\Delta(A, B) = \text{Nodes}(A) \triangle \text{Nodes}(B)$ in $\mathcal{O}(|\Delta| \log N)$ network frames.

---

## 💻 Zero-Dependency Production Implementation

```python
"""
N075: CRDT Local-First State Engine with Vector Clocks, OR-Set, LWW-Set, & Merkle DAG Sync.
Pure Python standard library implementation with zero external dependencies.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
import hashlib
import json
import time

class VectorClock:
    """Vector clock implementing strict causal ordering and lattice join."""
    def __init__(self, clock: Optional[Dict[str, int]] = None):
        self.clock: Dict[str, int] = dict(clock) if clock else {}

    def tick(self, replica_id: str) -> "VectorClock":
        self.clock[replica_id] = self.clock.get(replica_id, 0) + 1
        return self

    def get(self, replica_id: str) -> int:
        return self.clock.get(replica_id, 0)

    def merge(self, other: "VectorClock") -> "VectorClock":
        keys = set(self.clock.keys()) | set(other.clock.keys())
        merged = {k: max(self.clock.get(k, 0), other.clock.get(k, 0)) for k in keys}
        return VectorClock(merged)

    def is_causally_before(self, other: "VectorClock") -> bool:
        """Returns True iff self < other."""
        keys = set(self.clock.keys()) | set(other.clock.keys())
        less_equal = all(self.clock.get(k, 0) <= other.clock.get(k, 0) for k in keys)
        strictly_less = any(self.clock.get(k, 0) < other.clock.get(k, 0) for k in keys)
        return less_equal and strictly_less

    def is_concurrent_with(self, other: "VectorClock") -> bool:
        """Returns True iff self || other."""
        return not self.is_causally_before(other) and not other.is_causally_before(self) and self.clock != other.clock

class ORSet:
    """Observed-Remove Set (CvRDT) with causal dot tagging."""
    def __init__(self, replica_id: str):
        self.replica_id = replica_id
        self.counter = 0
        # Dot: (replica_id, counter)
        self.add_set: Set[Tuple[Any, Tuple[str, int]]] = set()
        self.remove_set: Set[Tuple[Any, Tuple[str, int]]] = set()

    def add(self, element: Any) -> Tuple[str, int]:
        self.counter += 1
        dot = (self.replica_id, self.counter)
        self.add_set.add((element, dot))
        return dot

    def remove(self, element: Any) -> Set[Tuple[str, int]]:
        # Find all currently observed dots for this element
        observed_dots = {dot for elem, dot in self.add_set if elem == element}
        for dot in observed_dots:
            self.remove_set.add((element, dot))
        return observed_dots

    def read(self) -> Set[Any]:
        active = self.add_set - self.remove_set
        return {elem for elem, _ in active}

    def merge(self, other: "ORSet") -> "ORSet":
        merged = ORSet(self.replica_id)
        merged.counter = max(self.counter, other.counter)
        merged.add_set = self.add_set | other.add_set
        merged.remove_set = self.remove_set | other.remove_set
        return merged

class LWWElementSet:
    """Last-Write-Wins Element-Set with hybrid timestamp tie-breaking."""
    def __init__(self):
        # element -> (timestamp, is_deleted)
        self.entries: Dict[str, Tuple[float, int, bool]] = {}
        self._seq = 0

    def add(self, element: str, ts: Optional[float] = None) -> None:
        self._seq += 1
        t = ts if ts is not None else time.time()
        self._update(element, t, self._seq, is_deleted=False)

    def remove(self, element: str, ts: Optional[float] = None) -> None:
        self._seq += 1
        t = ts if ts is not None else time.time()
        self._update(element, t, self._seq, is_deleted=True)

    def _update(self, element: str, ts: float, seq: int, is_deleted: bool) -> None:
        if element in self.entries:
            cur_ts, cur_seq, _ = self.entries[element]
            if (ts, seq) <= (cur_ts, cur_seq):
                return
        self.entries[element] = (ts, seq, is_deleted)

    def read(self) -> Set[str]:
        return {k for k, (_, _, deleted) in self.entries.items() if not deleted}

    def merge(self, other: "LWWElementSet") -> "LWWElementSet":
        res = LWWElementSet()
        all_keys = set(self.entries.keys()) | set(other.entries.keys())
        for k in all_keys:
            e1 = self.entries.get(k)
            e2 = other.entries.get(k)
            if e1 and e2:
                res.entries[k] = e1 if (e1[0], e1[1]) >= (e2[0], e2[1]) else e2
            else:
                res.entries[k] = e1 if e1 else e2  # type: ignore
        return res

@dataclass
class MerkleNode:
    payload: str
    parents: List[str] = field(default_factory=list)
    node_id: str = field(init=False)

    def __post_init__(self):
        canonical = json.dumps({"payload": self.payload, "parents": sorted(self.parents)}, sort_keys=True)
        self.node_id = hashlib.sha256(canonical.encode()).hexdigest()

class MerkleDAGSync:
    """Content-addressed Merkle DAG delta-reconciliation for local-first sync."""
    def __init__(self):
        self.nodes: Dict[str, MerkleNode] = {}
        self.heads: Set[str] = set()

    def append(self, payload: str) -> str:
        parents = sorted(list(self.heads))
        node = MerkleNode(payload=payload, parents=parents)
        self.nodes[node.node_id] = node
        # Update heads: remove parents, add new node
        self.heads.difference_update(parents)
        self.heads.add(node.node_id)
        return node.node_id

    def get_root_hash(self) -> str:
        canonical_heads = sorted(list(self.heads))
        return hashlib.sha256(",".join(canonical_heads).encode()).hexdigest()

    def reconcile_missing_nodes(self, peer_dag: "MerkleDAGSync") -> List[MerkleNode]:
        """Calculates minimal symmetric diff of missing nodes to transmit."""
        missing_ids = set(peer_dag.nodes.keys()) - set(self.nodes.keys())
        return [peer_dag.nodes[nid] for nid in missing_ids]

    def ingest_delta(self, delta_nodes: List[MerkleNode]) -> None:
        for node in delta_nodes:
            self.nodes[node.node_id] = node
        # Recompute heads
        all_parents = {p for n in self.nodes.values() for p in n.parents}
        self.heads = set(self.nodes.keys()) - all_parents

if __name__ == "__main__":
    # 1. Vector Clock Causal Verification
    v1 = VectorClock().tick("A").tick("A")
    v2 = VectorClock().tick("A").tick("B")
    assert v1.is_concurrent_with(v2), "V1 and V2 must be concurrent"
    v3 = v1.merge(v2).tick("A")
    assert v1.is_causally_before(v3) and v2.is_causally_before(v3), "V3 must dominate V1 and V2"

    # 2. OR-Set Causal Add-Remove Verification
    replica_a = ORSet("node-A")
    replica_b = ORSet("node-B")
    replica_a.add("file.txt")
    replica_b.add("file.txt")
    # Replica A removes observed file.txt locally
    replica_a.remove("file.txt")
    # Merge A and B -> B's concurrent addition dot survives remove from A
    merged = replica_a.merge(replica_b)
    assert "file.txt" in merged.read(), "Concurrent add must survive independent remove"

    # 3. LWW-Set Deterministic Convergence
    lww1 = LWWElementSet()
    lww2 = LWWElementSet()
    lww1.add("doc1", ts=100.0)
    lww2.remove("doc1", ts=105.0)
    m_lww = lww1.merge(lww2)
    assert "doc1" not in m_lww.read(), "Higher timestamp remove must win"

    # 4. Merkle DAG Delta Synchronization
    dag1 = MerkleDAGSync()
    dag2 = MerkleDAGSync()
    h1 = dag1.append("Commit 1: Init")
    dag2.nodes[h1] = dag1.nodes[h1]
    dag2.heads = {h1}

    # Concurrent branches
    dag1.append("Branch 1: Feature A")
    dag2.append("Branch 2: Bugfix B")
    assert dag1.get_root_hash() != dag2.get_root_hash(), "Root hashes must diverge on branch"

    delta_for_1 = dag1.reconcile_missing_nodes(dag2)
    dag1.ingest_delta(delta_for_1)
    delta_for_2 = dag2.reconcile_missing_nodes(dag1)
    dag2.ingest_delta(delta_for_2)

    assert dag1.get_root_hash() == dag2.get_root_hash(), "Merkle DAGs must achieve identical root hash"
    print("Self-Check Passed: CRDT & Merkle DAG Invariants Verified.")
```

---

## 🔍 Root Cause Analysis & Failure Mode Guards

| Failure Mode | Root Cause | Prevention & Algorithmic Guard |
| :--- | :--- | :--- |
| **Clock Skew Anomaly (LWW Overwrite)** | Unsynchronized physical clocks cause stale replica to overwrite newer state indefinitely. | Pair physical timestamps with monotonic logical sequences (Hybrid Logical Clocks, HLC) with drift ceiling checks ($|T_{\text{local}} - T_{\text{remote}}| \le \delta_{\text{max}}$). |
| **Tombstone Unbounded Explosion** | OR-Set remove sets grow indefinitely as elements are repeatedly mutated. | Causal compaction: Prune dots covered by the stable lower bound of cluster-wide Vector Clock frontier ($\min_{r \in \mathcal{R}} V[r]$). |
| **Silent Add-Wins Mutation Loss** | Concurrently added items overwritten by naive boolean presence flags. | Mandatory Causal Dot Tagging ($(r, c)$ pair per write); set subtraction retains unseen additions across network partitions. |
| **Merkle Sync Subtree Explosion** | High-frequency append streams create linear DAGs with high-overhead hash exchange. | Use Skip-Graph / Prolly Tree / B-Tree chunking over canonical byte boundaries to bound diff traversal to $\mathcal{O}(\log N)$. |
| **Split-Brain Convergence Stall** | Cyclic parent dependencies injected via malicious or malformed network frames. | Content-addressed topological sorting: Node rejection if $H(u)$ does not match canonical SHA256 of strictly ordered parent hashes. |

---

## 🔒 Execution Discipline & Operational Invariants
1. **Ponytail YAGNI:** Eliminate heavy consensus algorithms (Paxos/Raft) when causal CRDT lattices and Merkle DAGs provide partition-tolerant convergence without coordinators.
2. **Single Root Fix:** Treat replication divergence as a semi-lattice violation; enforce monotonic join operations rather than patching ad-hoc state reconcilers.
3. **Line Count Guard:** Strictly bounded under 300 lines with high mathematical density and zero external library dependencies.
