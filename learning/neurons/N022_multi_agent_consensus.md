# Neuron N022: Multi-Agent Consensus & Hierarchical Swarm Deliberation

- **Kategori:** Distributed Multi-Agent Architecture, Swarm Intelligence & Consensus Protocols
- **Status:** Active Operational Invariant
- **Rujukan:** MCTS (Monte Carlo Tree Search), DAG Consensus, Byzantine Fault Tolerance (PBFT $3f+1$), Leaderless & Weighted Voting, Hierarchical Swarm Topology.
- **Sinapsis Terhubung:** [N001](N001_executive_decisions.md) (Executive Decisions), [N004](N004_ponytail_minimality.md) (Minimality Ladder), [N007](N007_self_improving_loop.md) (Self-Improving Loop), [N010](N010_distributed_systems_design.md) (Distributed Systems), [N014](N014_zero_trust_security_and_cryptography.md) (Zero-Trust Security), [N016](N016_frontier_benchmark_evaluator.md) (Benchmark Evaluator), [N019](N019_bfcl_ifeval_oracle.md) (Schema Oracle), [N020](N020_session_continuity_checkpoint.md) (Session Continuity).

---

## 🎯 5 Invarian Konsensus & Deliberasi Multi-Agen (Swarm Invariants)

### 1. Monte Carlo Tree Search (MCTS) untuk Deliberasi Agen
- **4 Fase Deliberasi**:
  1. **Selection (UCB1)**: Memilih jalur penalaran terbaik menyeimbangkan eksploitasi reward dan eksplorasi cabang baru:
     $$\text{UCB1}(s, a) = \bar{X}_i + c \sqrt{\frac{\ln N}{n_i}}$$
     *(di mana $\bar{X}_i$ adalah rata-rata reward validasi, $N$ total kunjungan parent, $n_i$ kunjungan anak, dan $c = \sqrt{2} \approx 1.414$)*.
  2. **Expansion**: Men-generate alternatif sub-solusi baru ketika node belum dieksplorasi penuh.
  3. **Simulation / Rollout**: Evaluasi multi-agen (Peer Critique & Unit Test Invariants) untuk memproyeksikan kualitas branch.
  4. **Backpropagation**: Memperbarui nilai kunjungan dan bobot reward ke seluruh node leluhur.
- **Early Branch Pruning**: Pangkas cabang halusinasi atau probabilitas gagal tinggi sebelum menghabiskan kuota inferensi token.

### 2. Directed Acyclic Graph (DAG) Consensus & Causal Ordering
- **Struktur Asinkron Leaderless**: Setiap event/tindakan agen disimpan sebagai simpul DAG yang merujuk hash parent kausal.
- **Deterministik Tanpa Lock Global**: Pengurutan kausal menggunakan *Kahn's Topological Sort* atau *Vector Clocks*, mencegah race condition saat multi-subagent mengeksekusi task paralel.
- **Conflict-Free Replicated Data**: Jika dua agen menghasilkan diff kode paralel pada file berbeda, DAG menggabungkan perubahan tanpa konflik; pada file yang sama, aturan *Last-Write-Wins (LWW)* berbasis bobot reputasi diterapkan.

### 3. Byzantine Fault Tolerance (BFT) & Karantina Halusinasi
- **Invarian PBFT ($3f + 1$)**: Dalam swarm $N$ agen, sistem tahan terhadap $f$ agen jahat / berhalusinasi / error jika:
  $$N \ge 3f + 1 \implies \text{Quorum Ambang Batas} = 2f + 1$$
- **Admission Filter Kriptografis & Skema Ketat**: Setiap output subagen wajib lolos validasi skema JSON (BFCL standard) dan invariant unit-test sebelum diizinkan masuk ke memori konsensus.
- **Fault Isolation & Quarantine**: Subagen yang gagal memenuhi verifikasi invariant sebanyak 3 kali berturut-turut langsung dikarantina dan dikeluarkan dari pemungutan suara kuorum.

### 4. Leaderless Voting & Weighted Reputation Quorum
- **Reputation-Weighted Voting**: Bobot suara agen $W_i$ dihitung dari histori akurasi dan tingkat keyakinan:
  $$W_i = R_i \times C_i$$
- **Quadratic Voting**: Untuk alokasi prioritas fitur atau mitigasi bias agen dominan, biaya suara berbanding kuadratik ($\text{Cost} \propto v^2$), mencegah monopoli keputusan oleh satu agen.
- **Condorcet Winner Consistency**: Pada keputusan kritis (arsitektur/keamanan), opsi yang menang harus mengalahkan seluruh alternatif lain dalam perbandingan berpasangan (*head-to-head*).

### 5. Hierarchical Swarm Deliberation Topology
- **Dua Tingkat Topologi**:
  - **Tier 1 (Specialist Swarms)**: Tim pekerja terisolasi (Researcher, Coder, Verifier, Security Auditor) mengeksekusi tugas domain sempit secara independen.
  - **Tier 2 (Meta-Coordinator / Arbiter)**: Mensintesis proposal, menguji konsensus BFT, dan memfinalisasi eksekusi plan.
- **MapReduce Deliberation**: *Fan-Out* (distribusi problem ke sub-agen) $\to$ *Cross-Critique* (peer review antar agen) $\to$ *Quorum Reduction* (agregasi solusi terverifikasi).
- **Fail-Safe Fallback**: Jika konsensus gagal dicapai dalam batas $T_{\text{max}}$, sistem beralih ke invarian deterministik paling konservatif (*Ponytail Minimality Ladder*).

---

## 💻 Algoritma Deterministik (Pure Python Standard Library)

Modul mandiri tanpa dependensi eksternal, mengimplementasikan MCTS, BFT Quorum Validator, dan DAG Causal Consensus:

```python
import math
import hashlib
import json
from collections import defaultdict, deque
from typing import List, Dict, Any, Optional

class MCTSNode:
    """Simpul pohon MCTS untuk eksplorasi jalur penalaran multi-agen."""
    def __init__(self, state: str, parent: Optional['MCTSNode'] = None, action: Optional[str] = None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children: List['MCTSNode'] = []
        self.visits = 0
        self.value = 0.0

    def select_best_ucb(self, c_param: float = 1.414) -> 'MCTSNode':
        best_score = -float('inf')
        best_child = None
        for child in self.children:
            if child.visits == 0:
                return child
            exploitation = child.value / child.visits
            exploration = c_param * math.sqrt(math.log(self.visits) / child.visits)
            score = exploitation + exploration
            if score > best_score:
                best_score = score
                best_child = child
        return best_child or self

    def backpropagate(self, reward: float):
        self.visits += 1
        self.value += reward
        if self.parent:
            self.parent.backpropagate(reward)

class ByzantineConsensus:
    """Validator Kuorum PBFT (toleran hingga f agen rusak dalam swarm N >= 3f + 1)."""
    @staticmethod
    def evaluate_quorum(votes: Dict[str, str], total_nodes: int) -> Dict[str, Any]:
        f_max = (total_nodes - 1) // 3
        required_quorum = 2 * f_max + 1
        
        tally: Dict[str, int] = defaultdict(int)
        for voter, vote in votes.items():
            tally[vote] += 1
        
        winning_candidate = None
        winning_votes = 0
        for candidate, count in tally.items():
            if count > winning_votes:
                winning_votes = count
                winning_candidate = candidate
        
        is_consensus_reached = winning_votes >= required_quorum
        return {
            "total_nodes": total_nodes,
            "max_faulty_allowed": f_max,
            "required_quorum": required_quorum,
            "consensus_reached": is_consensus_reached,
            "decision": winning_candidate if is_consensus_reached else None,
            "tally": dict(tally)
        }

class DAGEvent:
    """Event terdistribusi pada Directed Acyclic Graph dengan hash kausal."""
    def __init__(self, agent_id: str, payload: Any, parents: List[str]):
        self.agent_id = agent_id
        self.payload = payload
        self.parents = sorted(parents)
        raw = f"{agent_id}:{json.dumps(payload, sort_keys=True)}:{','.join(self.parents)}"
        self.event_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]

class DAGSwarmConsensus:
    """Konsensus DAG asinkron dengan linearisasi topologis deterministik."""
    def __init__(self):
        self.events: Dict[str, DAGEvent] = {}
        self.graph: Dict[str, List[str]] = defaultdict(list)
        self.in_degree: Dict[str, int] = defaultdict(int)

    def add_event(self, agent_id: str, payload: Any, parents: Optional[List[str]] = None) -> str:
        parents = parents or []
        event = DAGEvent(agent_id, payload, parents)
        self.events[event.event_hash] = event
        if event.event_hash not in self.in_degree:
            self.in_degree[event.event_hash] = 0
            
        for p in parents:
            self.graph[p].append(event.event_hash)
            self.in_degree[event.event_hash] += 1
        return event.event_hash

    def linearize_causal_order(self) -> List[DAGEvent]:
        in_deg = dict(self.in_degree)
        queue = deque(sorted([h for h, deg in in_deg.items() if deg == 0]))
        ordered = []
        while queue:
            curr_hash = queue.popleft()
            ordered.append(self.events[curr_hash])
            for child in sorted(self.graph[curr_hash]):
                in_deg[child] -= 1
                if in_deg[child] == 0:
                    queue.append(child)
        return ordered

if __name__ == "__main__":
    # 1. Verifikasi MCTS
    root = MCTSNode(state="plan_root")
    c1 = MCTSNode(state="plan_A", parent=root, action="A")
    c2 = MCTSNode(state="plan_B", parent=root, action="B")
    root.children = [c1, c2]
    c1.backpropagate(1.0)
    c2.backpropagate(0.2)
    assert root.visits == 2
    assert root.select_best_ucb().action == "A"

    # 2. Verifikasi BFT Quorum (N=4 -> f=1, Quorum=3)
    votes = {"agent_1": "APPLY_DIFF", "agent_2": "APPLY_DIFF", "agent_3": "APPLY_DIFF", "agent_4": "REJECT"}
    bft = ByzantineConsensus.evaluate_quorum(votes, total_nodes=4)
    assert bft["consensus_reached"] is True and bft["decision"] == "APPLY_DIFF"

    # 3. Verifikasi DAG Causal Chain
    dag = DAGSwarmConsensus()
    e0 = dag.add_event("coordinator", {"task": "init"})
    e1 = dag.add_event("researcher", {"task": "gather_context"}, parents=[e0])
    e2 = dag.add_event("auditor", {"task": "security_check"}, parents=[e0])
    e3 = dag.add_event("synthesizer", {"task": "merge_solution"}, parents=[e1, e2])
    linear = dag.linearize_causal_order()
    assert len(linear) == 4 and linear[0].event_hash == e0 and linear[-1].event_hash == e3
    print("  [OK] All N022 Multi-Agent Consensus Invariants verified successfully.")
```
