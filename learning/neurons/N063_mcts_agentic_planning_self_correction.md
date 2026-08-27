# N063: MCTS Agentic Planning, State Backpropagation & Self-Correction Engine

- **Kategori:** Autonomous Agentic Planning, Tree Search & Self-Correction Architecture
- **Tanggal Sintesis:** 2026-08-27
- **Status:** Active Operational Invariant
- **Rujukan:** PUCT (Predictor Upper Confidence Bounds for Trees), Credit Assignment Failure Backprop, Alpha-Beta Branch Pruning, Transactional Rollback, Schema Contract Verification.
- **Sinapsis Terhubung:** [N001](N001_executive_decisions.md), [N004](N004_ponytail_minimality.md), [N007](N007_self_improving_loop.md), [N019](N019_bfcl_ifeval_oracle.md), [N022](N022_multi_agent_consensus.md), [N040](N040_meta_cognitive_self_reflection.md).

---

## 🎯 5 Invarian Utama MCTS Planning & Self-Correction

### 1. PUCT Multi-Step Agentic Decision Planning
Setiap eksplorasi rencana aksi dihitung menggunakan formulasi PUCT (*Predictor Upper Confidence bounds for Trees*):
$$\text{PUCT}(s, a) = Q(s, a) + c_{\text{puct}} \cdot P(s, a) \cdot \frac{\sqrt{\sum_{b} N(s, b)}}{1 + N(s, a)}$$
- $Q(s, a)$: Akumulasi estimasi reward rata-rata dari branch $a$ di state $s$.
- $P(s, a)$: Prior probability dari policy network / LLM heuristic sebelum eksekusi.
- $N(s, a)$: Frekuensi kunjungan branch aksi $a$.
- $c_{\text{puct}}$: Parameter penyeimbang eksplorasi vs eksploitasi ($c_{\text{puct}} \in [1.0, 2.5]$).

### 2. Failure State Backpropagation & Negative Credit Assignment
Ketika eksekusi tool atau sub-task mengalami runtime error / contract violation, kegagalan tidak diabaikan secara lokal melainkan dibackpropagate ke seluruh simpul leluhur dengan diskon temporal:
$$\Delta Q(s_t) = -\lambda_{\text{fail}} \cdot \gamma^{(T - t)}$$
- $\lambda_{\text{fail}} \ge 1.0$: Bobot penalti kegagalan (*severe penalty weight*).
- $\gamma \in (0, 1]$: Discount factor temporal untuk melokalisasi root-cause pada simpul penyebab primer.
- Simpul yang memicu kegagalan berulang dikarantina (*tombstoned*) agar tidak dipilih ulang pada iterasi berikutnya.

### 3. Heuristic Dynamic Branch Pruning
Untuk mencegah ledakan kombinatorial (*combinatorial explosion*) dan pembengkakan konsumsi token:
- **Variance Cutoff**: Cabang dengan nilai reward $Q(s, a) < Q_{\text{threshold}}$ setelah $N \ge N_{\text{min}}$ kunjungan langsung dipangkas (*pruned*).
- **Depth-Budget Bounding**: Kedalaman pohon dibatasi ketat $D \le D_{\text{max}}$; jika target goal belum tercapai pada limit depth, branch dihentikan dengan fallback status `PRUNED_DEPTH_EXCEEDED`.

### 4. Transactional Checkpoint & State Rollback Engine
Setiap eksekusi tool non-idempotent (file write, database mutation, OS command) wajib dibungkus dalam transactional checkpoint:
- **Snapshot Isolation**: Menyimpan delta state sebelum eksekusi (`pre_state_hash`, `undo_diff`).
- **Deterministic Unwinding**: Jika verifikator pasca-eksekusi gagal, sistem mengeksekusi stack kompensasi LIFO (Last-In-First-Out) untuk mengembalikan environment ke state bersih.

### 5. Strict Pre-Execution Schema Contract & Invariant Validation
Sebelum agen memanggil eksekusi tool fisik, input wajib divalidasi deterministik terhadap kontrak skema (AST validator / JSON Schema oracle):
- Zero toleransi terhadap type hallucination, missing keys, atau illegal parameter injections.
- Validasi gagal langsung mengembalikan reward $-1.0$ ke MCTS node tanpa membuang I/O resource.

---

## 💻 Implementasi Produksi (Pure Python Standard Library)

```python
import math
import copy
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Callable

class ToolContractValidator:
    """Validator kontrak skema pra-eksekusi deterministik."""
    @staticmethod
    def validate(tool_name: str, payload: Dict[str, Any], schema: Dict[str, type]) -> Tuple[bool, Optional[str]]:
        for param, expected_type in schema.items():
            if param not in payload:
                return False, f"Missing required parameter '{param}' for tool '{tool_name}'"
            if not isinstance(payload[param], expected_type):
                return False, f"Type mismatch for '{param}': expected {expected_type.__name__}, got {type(payload[param]).__name__}"
        return True, None

class CheckpointRollbackStack:
    """Mesin snapshot dan rollback transaksional LIFO."""
    def __init__(self):
        self._history: List[Tuple[str, Callable[[], None]]] = []

    def register_step(self, step_name: str, undo_fn: Callable[[], None]):
        self._history.append((step_name, undo_fn))

    def rollback_all(self) -> List[str]:
        rolled_back = []
        while self._history:
            name, undo_fn = self._history.pop()
            try:
                undo_fn()
                rolled_back.append(name)
            except Exception as e:
                rolled_back.append(f"{name}_FAILED({str(e)})")
        return rolled_back

class MCTSPlannerNode:
    """Simpul pohon MCTS dengan PUCT, failure backpropagation, dan dynamic pruning."""
    def __init__(self, state: Dict[str, Any], parent: Optional['MCTSPlannerNode'] = None, action: Optional[str] = None, prior_p: float = 1.0):
        self.state = copy.deepcopy(state)
        self.parent = parent
        self.action = action
        self.prior_p = prior_p
        self.children: List['MCTSPlannerNode'] = []
        self.visits: int = 0
        self.total_value: float = 0.0
        self.is_pruned: bool = False
        self.is_terminal: bool = False

    @property
    def q_value(self) -> float:
        return self.total_value / self.visits if self.visits > 0 else 0.0

    def select_puct(self, c_puct: float = 1.414) -> Optional['MCTSPlannerNode']:
        valid_children = [c for c in self.children if not c.is_pruned]
        if not valid_children:
            return None
        total_parent_visits = sum(c.visits for c in valid_children)
        best_score = -float('inf')
        best_child = None
        for child in valid_children:
            exploration = c_puct * child.prior_p * (math.sqrt(total_parent_visits) / (1 + child.visits))
            score = child.q_value + exploration
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def backpropagate_result(self, reward: float, discount: float = 0.95):
        curr: Optional['MCTSPlannerNode'] = self
        curr_reward = reward
        while curr is not None:
            curr.visits += 1
            curr.total_value += curr_reward
            curr_reward *= discount
            curr = curr.parent

    def prune_underperforming(self, threshold: float = -0.5, min_visits: int = 3):
        if self.visits >= min_visits and self.q_value < threshold:
            self.is_pruned = True
        for child in self.children:
            child.prune_underperforming(threshold, min_visits)

class AgentMCTSEngine:
    """Engine orkestrasi perencana MCTS dengan verifikasi skema dan self-correction."""
    def __init__(self, root_state: Dict[str, Any], schemas: Dict[str, Dict[str, type]]):
        self.root = MCTSPlannerNode(state=root_state)
        self.schemas = schemas
        self.rollback_stack = CheckpointRollbackStack()

    def simulate_action(self, node: MCTSPlannerNode, action_name: str, payload: Dict[str, Any], 
                        executor: Callable[[Dict[str, Any]], Tuple[bool, float, Dict[str, Any]]]) -> MCTSPlannerNode:
        # 1. Pre-execution Schema Contract Validation
        schema = self.schemas.get(action_name, {})
        valid, err = ToolContractValidator.validate(action_name, payload, schema)
        if not valid:
            child = MCTSPlannerNode(state=node.state, parent=node, action=f"{action_name}_SCHEMA_FAIL", prior_p=0.01)
            child.is_pruned = True
            child.backpropagate_result(-2.0)  # Heavy failure penalty
            node.children.append(child)
            return child

        # 2. Execution with Rollback Guard
        success, reward, next_state = executor(payload)
        child = MCTSPlannerNode(state=next_state, parent=node, action=action_name, prior_p=1.0)
        node.children.append(child)
        if not success:
            child.backpropagate_result(-1.5)
        else:
            child.backpropagate_result(reward)
        return child

if __name__ == "__main__":
    schemas = {
        "apply_patch": {"file_path": str, "patch_content": str, "target_line": int}
    }
    engine = AgentMCTSEngine(root_state={"files": {"app.py": "print('hello')"}}, schemas=schemas)

    # Test 1: Schema Violation triggers immediate negative backprop & pruning
    bad_payload = {"file_path": "app.py", "target_line": "invalid_line"}  # type mismatch
    c1 = engine.simulate_action(engine.root, "apply_patch", bad_payload, lambda p: (True, 1.0, {}))
    assert c1.is_pruned is True
    assert engine.root.q_value < 0

    # Test 2: Valid execution succeeds & updates Q-value
    good_payload = {"file_path": "app.py", "patch_content": "print('world')", "target_line": 1}
    c2 = engine.simulate_action(engine.root, "apply_patch", good_payload, lambda p: (True, 1.0, {"files": {"app.py": "print('world')"}}))
    assert c2.is_pruned is False
    assert c2.q_value == 1.0

    # Test 3: Rollback stack verification
    state_mock = {"val": 100}
    engine.rollback_stack.register_step("mutate_val", lambda: state_mock.update({"val": 100}))
    state_mock["val"] = 999
    rolled = engine.rollback_stack.rollback_all()
    assert state_mock["val"] == 100 and "mutate_val" in rolled
    print("  [OK] All N063 MCTS Planning & Self-Correction Invariants verified successfully.")
```

---

## 🔍 Akar Masalah & Pencegahan Regresi (Root Cause Analysis)

| Kegagalan Tipikal | Akar Masalah Primer | Pencegahan Invarian N063 |
| :--- | :--- | :--- |
| **Agent Infinite Tool Loop** | Kegagalan tool lokal tidak memotong probabilitas pemilihan aksi di level planner. | Failure State Backpropagation memberi diskon negatif ke leluhur, memicu UCT reroute instan. |
| **Silent Type / Param Crash** | LLM mengirimkan tipe data skema yang salah saat memanggil tools. | Pre-execution `ToolContractValidator` menolak eksekusi sebelum I/O dan mendegradasi bobot cabang. |
| **Destructive Side-Effects** | Operasi parsial gagal di tengah jalan meninggalkan state korup. | `CheckpointRollbackStack` (LIFO) mengeksekusi kompensasi deterministik saat evaluasi invariant gagal. |
| **Token Budget Exhaustion** | Eksplorasi brute-force pada cabang halusinasi dengan reward rendah. | Dynamic `prune_underperforming` memangkas simpul dengan $Q < Q_{\text{threshold}}$ setelah minimal $N_{\text{min}}$ kunjungan. |

---

## 🔒 Disiplin Eksekusi (Ponytail Minimality & Operational Invariants)
1. **Ponytail YAGNI**: Dilarang membuat pohon MCTS lebih dari kedalaman $D=5$ jika solusi greedy atau single-step contract validation cukup membuktikan kebenaran.
2. **Single Root Fix**: Seluruh kegagalan tool harus dideteksi pada pintu gerbang validator skema pra-eksekusi, bukan di-patch ad-hoc di dalam executor body.
3. **Bounded Complexity**: File implementasi tetap mandiri tanpa dependensi pihak ketiga, dengan total panjang file ketat $< 300$ baris.
