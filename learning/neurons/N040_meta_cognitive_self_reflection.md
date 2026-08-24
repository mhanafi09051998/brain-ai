# Neuron N040: Meta-Cognitive Self-Reflection & Recursive Self-Correction

Prinsip arsitektur meta-kognisi otonom, refleksi rekursif, eksplorasi pohon pemikiran (*Tree-of-Thoughts / MCTS*), evaluasi kepastian epistemik (*epistemic vs aleatoric uncertainty*), dan guardrail anti-halusinasi nol-toleransi (*Zero-Hallucination Invariants*):

- **Kategori**: Autonomous Cognition, Meta-Reasoning, Algorithmic Verification & Epistemic Safety
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Mengeliminasi halusinasi model melalui pemantauan metakognitif internal, mengeksplorasi ruang hipotesis non-linear via Monte Carlo Tree Search (MCTS) dan Tree-of-Thoughts (ToT), mengoreksi kesalahan secara rekursif melalui loop Reflexion memori episodik, mengukur entropi semantik untuk kalibrasi keyakinan epistemik, dan menegakkan verifikasi kebenaran berbasis aksioma.
- **Synaptic Links**: [`N001`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N001_executive_decisions.md), [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N007`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N007_self_improving_loop.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N012`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N012_deep_search_and_graph_rag.md), [`N016`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N016_frontier_benchmark_evaluator.md), [`N019`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N019_bfcl_ifeval_oracle.md), [`N022`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N022_multi_agent_consensus.md)
- **Status**: Active Operational Invariant

---

## 1. Reflexion Loop & Verbal Reinforcement Learning Architecture

```
                               ┌────────────────────────┐
                               │     Task & Context     │
                               └───────────┬────────────┘
                                           │
                                           ▼
┌──────────────────┐           ┌────────────────────────┐
│ Episodic Memory  │──────────►│      Actor (LLM)       │
│ (Reflexion Bank) │           │ Generates Trajectory τ │
└─────────▲────────┘           └───────────┬────────────┘
          │                                │
          │                                ▼
┌─────────┴────────┐           ┌────────────────────────┐
│  Self-Reflector  │◄──────────│   Critic / Evaluator   │
│ Verbal Feedback  │  Feedback │  Reward Metric R(τ)    │
│  & Invariant Fix │  (Fail)   └───────────┬────────────┘
└──────────────────┘                       │
                                           ▼ (Success: R=1.0)
                               ┌────────────────────────┐
                               │ Verified Final Output  │
                               └────────────────────────┘
```

### A. Triad Component Architecture (Actor - Critic - Reflector)
1. **Actor Model ($M_A$)**:
   - Menghasilkan trajectory tindakan, penalaran logis, atau kode program $\tau = (s_0, a_0, s_1, a_1, \dots, s_T)$ berdasarkan konteks masalah dan memori refleksi masa lalu.
2. **Evaluator / Critic ($M_C$)**:
   - Menilai kualitas trajectory $\tau$ menggunakan evaluasi deterministik (unit test execution, static AST linter, formal logic solver, atau semantic reward score $R(\tau) \in [0.0, 1.0]$).
3. **Self-Reflector ($M_R$)**:
   - Mengubah sinyal kesalahan numerik/eksekusi menjadi umpan balik verbal semantik (*verbal self-reflection*).
   - Menganalisis akar penyebab kegagalan (*root cause failure mode*), mengabstraksi invarian yang dilanggar, dan merumuskan rencana aksi korektif konkret untuk iterasi berikutnya.

### B. Episodic Semantic Memory & Trajectory Pruning
1. **Reflexion Memory Bank ($M_{bank}$)**:
   - Refleksi verbal disimpan dalam buffer memori jangka pendek per sesi. Sebelum mencoba kembali (*retry*), seluruh refleksi masa lalu diinjeksikan sebagai *in-context guidance* untuk memangkas cabang pencarian yang sudah terbukti gagal (*Semantic Negative Constraints*).
2. **Anti-Looping Invariant**:
   - Jika refleksi pada iterasi $k$ identik secara semantik dengan iterasi $k-1$ sementara skor reward tidak meningkat, hentikan eksplorasi lokal (*break local minima*) dan picu strategi *temperature perturbation* atau pivot hipotesis baru.

---

## 2. Tree-of-Thoughts (ToT) & Monte Carlo Tree Search (MCTS) Meta-Prompting

```
                             [ Root State s₀ ]
                               /      |      \
                              /       |       \
                       [ Thought A ] [Thought B] [ Thought C ]
                         (UCT=0.82)   (UCT=0.45)   (UCT=0.91) ★
                                                    /    \
                                                   /      \
                                            [ C1 ]         [ C2 ]  (Rollout & Backprop)
```

### A. Non-Linear Exploration vs Linear Chain-of-Thought
1. **Keterbatasan Linear Chain-of-Thought (CoT)**:
   - CoT tradisional bersifat *greedy unidirectional left-to-right generation*. Jika model mengambil premis yang keliru pada langkah awal, seluruh rantai pemikiran berikutnya terdegradasi (*cascading reasoning error*) tanpa kemampuan *lookahead* atau *backtracking*.
2. **Tree-of-Thoughts (ToT) State Formulation**:
   - Masalah dipecah menjadi *thought states* $s = [x, z_1, \dots, z_i]$, di mana $z_i$ adalah unit pemikiran diskrit (langkah pembuktian, kandidat diff fungsi, atau sub-solusi).
   - Model bertindak sebagai generator kandidat thought (*Action Generator*) sekaligus penilai heuristik nilai state (*State Value Evaluator* $V(s) \in [0.0, 1.0]$).

### B. Monte Carlo Tree Search (MCTS) Policy Engine
1. **Selection (Upper Confidence Bound for Trees - UCT/UCB1)**:
   $$\text{UCT}(s, a) = Q(s, a) + c_{\text{explore}} \cdot \sqrt{\frac{\ln N(s)}{1 + N(s, a)}}$$
   - Menyeimbangkan eksploitasi jalur pemikiran dengan estimasi reward tinggi $Q(s, a)$ dan eksplorasi cabang pemikiran yang belum sering dikunjungi $N(s, a)$.
2. **Expansion**:
   - Mengenerasi $K$ kandidat pemikiran (*branching factor*) dari state aktif.
3. **Simulation / Rollout**:
   - Melakukan evaluasi heuristik cepat (*fast shallow evaluation*) hingga state terminal atau depth limit tercapai.
4. **Backpropagation**:
   - Memperbarui statistik kunjungan $N(s)$ dan nilai kumulatif $V(s)$ dari daun (*leaf*) hingga ke akar (*root*). Jalur dengan nilai ekspektasi tertinggi dipilih sebagai trajectory optimal.

---

## 3. Epistemic Certainty Evaluation & Semantic Entropy Calibration

### A. Epistemic vs Aleatoric Uncertainty
1. **Aleatoric Uncertainty (Noise Data / Irreducible)**:
   - Ketidakpastian inheren pada data masukan atau ambiguitas bawaan dari instruksi pengguna. Diminimalkan melalui klarifikasi interaktif.
2. **Epistemic Uncertainty (Model Knowledge Deficit / Reducible)**:
   - Ketidakpastian akibat kurangnya fakta atau pengetahuan verifikasi internal model. Wajib dideteksi secara metakognitif untuk mencegah *confident hallucinations*.

### B. Semantic Entropy & Semantic Clustering Metric
1. **Sampling Multiple Reasoning Trajectories**:
   - Sampel $N$ jawaban independen dengan suhu stokastik $\tau > 0$: $\mathcal{Y} = \{y_1, y_2, \dots, y_N\}$.
2. **Semantic Equivalence Clustering ($C_1, C_2, \dots, C_K$)**:
   - Kelompokkan jawaban yang memiliki implikasi kebenaran yang setara secara semantik/logika (mengabaikan variasi gaya leksikal).
   - Probabilitas setiap cluster semantik:
     $$p(C_k) = \frac{|C_k|}{N}$$
3. **Semantic Entropy Formula**:
   $$H_{\text{semantic}} = -\sum_{k=1}^K p(C_k) \ln p(C_k)$$
4. **Epistemic Certainty Score ($E_c$)**:
   $$E_c = 1.0 - \frac{H_{\text{semantic}}}{\ln(\min(N, K_{\max}))}$$
   - Jika $E_c \ge \theta_{\text{gate}}$ (misal $\ge 0.85$): model memiliki keyakinan epistemik tinggi (*high certainty*), jawaban dapat diteruskan langsung.
   - Jika $E_c < \theta_{\text{gate}}$: model berada dalam zona halusinasi/keraguan tinggi; picu verifikasi eksternal, retrieval GraphRAG, atau fallback ke pengakuan ketidaktahuan (*calibrated uncertainty expression*).

---

## 4. Zero-Hallucination Guardrails & Recursive AST Self-Correction

### A. Axiom Grounding & Premise Containment Check
1. **Strict Context Containment Invariant**:
   - Setiap entitas, relasi, nilai numerik, atau klausa logika yang diklaim dalam output harus memiliki korespondensi langsung (*grounding lineage*) ke:
     a) Dokumen konteks masukan / knowledge graph nodes,
     b) Aksioma definisi formal yang terverifikasi,
     c) Output eksekusi alat / compiler feedback deterministik.
2. **Entity & Claim Extraction Verification**:
   - Filter setiap klaim faktual $c \in \text{Claims}(y)$. Jika $c \notin \text{Entailment}(\text{Axioms})$, tandai sebagai *Ungrounded / Hallucination Anomaly*.

### B. Recursive AST & Invariant Self-Correction Pipeline
1. **Linter & Syntax Pre-Flight**:
   - Parsing kode kandidat ke Abstract Syntax Tree (AST). Jika terjadi `SyntaxError`, kembalikan trace ke Actor tanpa eksekusi.
2. **Invariant Assertion Gating**:
   - Jalankan assertion suite pada fungsi target. Setiap kegagalan assertion langsung memicu loop Reflexion untuk memperbaiki fungsi bersama (*single root fix*) tanpa menambah dependensi baru.

---

## 5. Pure Python 3.12+ Executable Test Invariants (Zero-Dependency)

Berikut adalah implementasi deterministik metakognitif lengkap: **Reflexion Engine**, **Tree-of-Thoughts / MCTS Engine**, **Semantic Entropy Epistemic Evaluator**, dan **Zero-Hallucination Guardrail** yang dapat langsung dijalankan:

```python
"""
Neuron N040: Meta-Cognitive Self-Reflection & Recursive Self-Correction Suite
Pure Python 3.12+ Standard Library (Zero External Dependencies).
"""

import sys
import math
import random
from typing import Dict, List, Set, Tuple, Optional, Any, Callable

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# =====================================================================
# 1. Reflexion Loop & Verbal Memory Engine
# =====================================================================

class ReflexionMemoryBank:
    """Buffer memori episodik untuk menyimpan riwayat refleksi verbal."""
    def __init__(self, max_reflections: int = 5):
        self.max_reflections = max_reflections
        self.reflections: List[Dict[str, Any]] = []

    def record_reflection(self, iteration: int, failed_attempt: str, critique: str, corrective_action: str) -> None:
        entry = {
            "iteration": iteration,
            "failed_attempt": failed_attempt,
            "critique": critique,
            "corrective_action": corrective_action
        }
        self.reflections.append(entry)
        if len(self.reflections) > self.max_reflections:
            self.reflections.pop(0)

    def format_context_memory(self) -> str:
        if not self.reflections:
            return "No previous failure memory."
        lines = ["[Previous Failure Reflections & Corrective Invariants]:"]
        for r in self.reflections:
            lines.append(f"- Iter {r['iteration']} Critique: {r['critique']} -> Fix: {r['corrective_action']}")
        return "\n".join(lines)


class ReflexionEngine:
    """Siklus Actor-Critic-Reflector otonom untuk koreksi diri iteratif."""
    def __init__(self, memory_bank: ReflexionMemoryBank, max_iterations: int = 4):
        self.memory = memory_bank
        self.max_iterations = max_iterations

    def run_self_correction_loop(
        self,
        task_prompt: str,
        actor_fn: Callable[[str, str], str],
        critic_fn: Callable[[str], Tuple[bool, float, str]],
        reflector_fn: Callable[[str, str], Tuple[str, str]]
    ) -> Tuple[bool, str, int]:
        """
        Mengeksekusi loop refleksi verbal hingga reward = 1.0 atau max iterasi tercapai.
        Returns: (success_bool, final_output, total_iterations)
        """
        for iteration in range(1, self.max_iterations + 1):
            past_reflections = self.memory.format_context_memory()
            candidate_output = actor_fn(task_prompt, past_reflections)
            
            is_valid, reward, error_msg = critic_fn(candidate_output)
            if is_valid and math.isclose(reward, 1.0, abs_tol=1e-5):
                return True, candidate_output, iteration
            
            critique, corrective_action = reflector_fn(candidate_output, error_msg)
            self.memory.record_reflection(iteration, candidate_output, critique, corrective_action)
            
        return False, candidate_output, self.max_iterations


# =====================================================================
# 2. Tree-of-Thoughts (ToT) & MCTS Meta-Reasoning Engine
# =====================================================================

class MCTSThoughtNode:
    """Node state pohon pemikiran untuk eksplorasi non-linear."""
    def __init__(self, state_thought: str, parent: Optional['MCTSThoughtNode'] = None, depth: int = 0):
        self.state_thought = state_thought
        self.parent = parent
        self.children: List['MCTSThoughtNode'] = []
        self.visits: int = 0
        self.cumulative_value: float = 0.0
        self.depth = depth

    @property
    def value(self) -> float:
        return self.cumulative_value / self.visits if self.visits > 0 else 0.0

    def uct_score(self, total_parent_visits: int, exploration_weight: float = 1.414) -> float:
        if self.visits == 0:
            return float('inf')
        exploitation = self.value
        exploration = exploration_weight * math.sqrt(math.log(total_parent_visits) / self.visits)
        return exploitation + exploration

    def add_child(self, thought: str) -> 'MCTSThoughtNode':
        child = MCTSThoughtNode(thought, parent=self, depth=self.depth + 1)
        self.children.append(child)
        return child


class MCTSTreeOfThoughts:
    """Monte Carlo Tree Search untuk optimasi penelusuran ruang solusi pemikiran."""
    def __init__(
        self,
        thought_generator: Callable[[str, int], List[str]],
        state_evaluator: Callable[[str], float],
        exploration_c: float = 1.414,
        max_depth: int = 3
    ):
        self.thought_generator = thought_generator
        self.state_evaluator = state_evaluator
        self.c = exploration_c
        self.max_depth = max_depth

    def _rollout(self, state_thought: str, depth: int) -> float:
        curr = state_thought
        d = depth
        while d < self.max_depth:
            children = self.thought_generator(curr, 1)
            if not children or children[0].endswith("_leaf"):
                break
            curr = children[0]
            d += 1
        return self.state_evaluator(curr)

    def search(self, root_problem: str, num_simulations: int = 40, branching_factor: int = 3) -> List[str]:
        root = MCTSThoughtNode(state_thought=root_problem)

        for _ in range(num_simulations):
            # 1. Selection
            node = root
            while node.children:
                node = max(node.children, key=lambda c: c.uct_score(max(node.visits, 1), self.c))

            # 2. Expansion
            if node.visits > 0 or node == root:
                candidate_thoughts = self.thought_generator(node.state_thought, branching_factor)
                for th in candidate_thoughts:
                    node.add_child(th)
                if node.children:
                    node = node.children[0]

            # 3. Simulation (Rollout) & Value Evaluation
            simulated_value = self._rollout(node.state_thought, node.depth)

            # 4. Backpropagation
            curr: Optional[MCTSThoughtNode] = node
            while curr is not None:
                curr.visits += 1
                curr.cumulative_value += simulated_value
                curr = curr.parent

        # Ekstraksi lintasan pemikiran terbaik
        best_path: List[str] = []
        curr = root
        while curr.children:
            best_child = max(curr.children, key=lambda c: (c.value, c.visits))
            if best_child.state_thought.endswith("_leaf"):
                break
            best_path.append(best_child.state_thought)
            curr = best_child

        return best_path


# =====================================================================
# 3. Epistemic Certainty & Semantic Entropy Evaluator
# =====================================================================

class EpistemicCertaintyEvaluator:
    """Pengukur kepastian pengetahuan model berbasis Semantic Entropy."""
    
    @staticmethod
    def semantic_clustering(samples: List[str], equivalence_oracle: Callable[[str, str], bool]) -> List[List[str]]:
        """Mengelompokkan sampel penalaran ke dalam cluster semantik ekuivalen."""
        clusters: List[List[str]] = []
        for sample in samples:
            assigned = False
            for cluster in clusters:
                if equivalence_oracle(sample, cluster[0]):
                    cluster.append(sample)
                    assigned = True
                    break
            if not assigned:
                clusters.append([sample])
        return clusters

    @classmethod
    def calculate_epistemic_certainty(
        cls,
        samples: List[str],
        equivalence_oracle: Callable[[str, str], bool]
    ) -> Tuple[float, float, List[List[str]]]:
        """
        Menghitung Semantic Entropy & Epistemic Certainty Score.
        Returns: (epistemic_certainty [0..1], semantic_entropy, clusters)
        """
        if not samples:
            return 0.0, float('inf'), []
        
        n = len(samples)
        if n == 1:
            return 1.0, 0.0, [[samples[0]]]

        clusters = cls.semantic_clustering(samples, equivalence_oracle)
        
        entropy = 0.0
        for cluster in clusters:
            p_c = len(cluster) / n
            entropy -= p_c * math.log(p_c)

        max_possible_entropy = math.log(n)
        if math.isclose(max_possible_entropy, 0.0, abs_tol=1e-9):
            certainty = 1.0
        else:
            certainty = max(0.0, 1.0 - (entropy / max_possible_entropy))

        return certainty, entropy, clusters


# =====================================================================
# 4. Zero-Hallucination Guardrail & Grounding Validator
# =====================================================================

class ZeroHallucinationGuardrail:
    """Guardrail pemantau halusinasi berbasis grounding aksiomatik ketat."""
    def __init__(self, verified_axioms: Set[str]):
        self.axioms = {a.strip().lower() for a in verified_axioms}

    def verify_groundedness(self, claim_tokens: Set[str]) -> Tuple[bool, Set[str]]:
        """Memverifikasi bahwa seluruh entitas/klausa bersumber dari aksioma yang sah."""
        cleaned_tokens = {t.strip().lower() for t in claim_tokens}
        hallucinated_tokens = cleaned_tokens - self.axioms
        is_grounded = len(hallucinated_tokens) == 0
        return is_grounded, hallucinated_tokens

    def recursive_repair_claim(self, claim_tokens: Set[str], fallback_filler: str = "[UNVERIFIED]") -> Set[str]:
        """Secara rekursif menyaring klausa tak terverifikasi agar output 100% grounded."""
        is_grounded, hallucinated = self.verify_groundedness(claim_tokens)
        if is_grounded:
            return claim_tokens
        repaired = set()
        for token in claim_tokens:
            if token.strip().lower() in self.axioms:
                repaired.add(token)
            else:
                repaired.add(f"{token}:{fallback_filler}")
        return repaired


# =====================================================================
# 5. Invariant Test Execution Suite
# =====================================================================

def verify_neuron_n040_invariants():
    print("=== [Neuron N040: Meta-Cognitive Self-Reflection Invariants] ===")
    
    # -------------------------------------------------------------
    # Test 1: Reflexion Loop Convergence on Algorithmic Invariant
    # -------------------------------------------------------------
    print("[1/4] Testing Reflexion Loop & Verbal Reinforcement...")
    memory_bank = ReflexionMemoryBank(max_reflections=5)
    engine = ReflexionEngine(memory_bank=memory_bank, max_iterations=4)
    
    target_solution = "def binary_search(arr, target): left, right = 0, len(arr) - 1"
    
    def mock_actor(prompt: str, memory_ctx: str) -> str:
        if "mid calculation overflow" in memory_ctx and "boundary pointer" in memory_ctx:
            return "def binary_search(arr, target): left = 0; right = len(arr) - 1; mid = left + (right - left) // 2"
        elif "mid calculation overflow" in memory_ctx:
            return "def binary_search(arr, target): left = 0; right = len(arr); mid = left + (right - left) // 2"
        else:
            return "def binary_search(arr, target): left = 0; right = len(arr); mid = (left + right) // 2"

    def mock_critic(code: str) -> Tuple[bool, float, str]:
        if "right = len(arr) - 1" in code and "left + (right - left) // 2" in code:
            return True, 1.0, "All tests passed"
        elif "left + (right - left) // 2" not in code:
            return False, 0.5, "Integer overflow risk in mid calculation"
        else:
            return False, 0.8, "Index out of bounds risk with right pointer"

    def mock_reflector(code: str, error: str) -> Tuple[str, str]:
        if "overflow" in error:
            return "Used naive mid calculation", "Apply mid calculation overflow fix: left + (right - left) // 2"
        return "Right index is not len(arr) - 1", "Set boundary pointer right = len(arr) - 1"

    success, final_code, iters = engine.run_self_correction_loop(
        task_prompt="Implement safe binary search",
        actor_fn=mock_actor,
        critic_fn=mock_critic,
        reflector_fn=mock_reflector
    )
    assert success is True, "Reflexion loop must converge to valid solution!"
    assert iters == 3, f"Expected convergence in 3 iterations, got {iters}"
    assert "left + (right - left) // 2" in final_code
    print(f"  [✓] Reflexion Loop converged in {iters} iterations with verified code.")

    # -------------------------------------------------------------
    # Test 2: Tree-of-Thoughts / MCTS Non-Linear Path Finding
    # -------------------------------------------------------------
    print("[2/4] Testing Tree-of-Thoughts MCTS Path Search...")
    
    def mock_thought_generator(current_state: str, k: int) -> List[str]:
        if "Root" in current_state:
            return [f"Branch_{chr(65+i)}" for i in range(k)]
        elif "Branch_A" in current_state:
            return ["Branch_A_1", "Branch_A_2", "Branch_A_3"]
        elif "Branch_B" in current_state:
            return ["Branch_B_Optimal", "Branch_B_Suboptimal", "Branch_B_DeadEnd"]
        return [f"{current_state}_leaf"]

    def mock_evaluator(thought_state: str) -> float:
        if "Branch_B_Optimal" in thought_state:
            return 0.98
        elif "Branch_A" in thought_state:
            return 0.65
        elif "DeadEnd" in thought_state:
            return 0.05
        return 0.40

    mcts = MCTSTreeOfThoughts(mock_thought_generator, mock_evaluator, exploration_c=1.414)
    best_path = mcts.search(root_problem="Root_Problem", num_simulations=30, branching_factor=3)
    
    assert len(best_path) >= 2, f"MCTS should explore at least 2 steps deep, got {len(best_path)}"
    assert "Branch_B_Optimal" in best_path[-1] or "Branch_B" in best_path[0], f"MCTS should prioritize high-value branch, got {best_path}"
    print(f"  [✓] MCTS Search selected optimal trajectory: {' -> '.join(best_path)}")

    # -------------------------------------------------------------
    # Test 3: Epistemic Certainty & Semantic Entropy Quantification
    # -------------------------------------------------------------
    print("[3/4] Testing Semantic Entropy & Epistemic Certainty Calibration...")
    
    # Kasus A: Konsensus Tinggi (Semua sampel semantik setara -> Kepastian Epistemik = 1.0)
    high_consensus_samples = [
        "The time complexity is O(N log N) using quicksort.",
        "quicksort delivers O(n log n) running time.",
        "O(N log N) average runtime achieved with quicksort."
    ]
    def oracle_eq(s1: str, s2: str) -> bool:
        return ("o(n log n)" in s1.lower() and "o(n log n)" in s2.lower()) or \
               ("o(n^2)" in s1.lower() and "o(n^2)" in s2.lower())

    cert_high, ent_high, clusters_high = EpistemicCertaintyEvaluator.calculate_epistemic_certainty(
        high_consensus_samples, oracle_eq
    )
    assert math.isclose(cert_high, 1.0, abs_tol=1e-4), f"High consensus should yield certainty 1.0, got {cert_high}"
    assert math.isclose(ent_high, 0.0, abs_tol=1e-4), f"High consensus should yield entropy 0.0, got {ent_high}"
    assert len(clusters_high) == 1

    # Kasus B: Ketidakpastian Tinggi (Sampel terpecah -> Entropi tinggi, Kepastian rendah)
    divergent_samples = [
        "The time complexity is O(N log N) using quicksort.",
        "The algorithm takes O(N^2) worst case without random pivot.",
        "It runs in O(N log N) average complexity."
    ]
    cert_div, ent_div, clusters_div = EpistemicCertaintyEvaluator.calculate_epistemic_certainty(
        divergent_samples, oracle_eq
    )
    assert cert_div < cert_high, "Divergent samples must have lower epistemic certainty than unanimous ones"
    assert ent_div > 0.0, "Divergent samples must produce non-zero semantic entropy"
    assert len(clusters_div) == 2
    print(f"  [✓] Epistemic Certainty correctly calibrated: High={cert_high:.2f} vs Divergent={cert_div:.2f}")

    # -------------------------------------------------------------
    # Test 4: Zero-Hallucination Guardrail Axiom Verification
    # -------------------------------------------------------------
    print("[4/4] Testing Zero-Hallucination Grounding & Recursive Repair...")
    verified_knowledge = {"python", "fastapi", "postgresql", "pgvector", "redis", "asyncio"}
    guardrail = ZeroHallucinationGuardrail(verified_knowledge)

    # Valid grounded claim
    grounded_tokens = {"FastAPI", "PostgreSQL", "Asyncio"}
    is_valid, leaks = guardrail.verify_groundedness(grounded_tokens)
    assert is_valid is True, "Grounded tokens must pass guardrail verification"
    assert len(leaks) == 0

    # Hallucinated / Fabricated claim
    hallucinated_tokens = {"FastAPI", "PostgreSQL", "QuantumDB_v9", "HyperFlux_Engine"}
    is_valid_bad, leaks_bad = guardrail.verify_groundedness(hallucinated_tokens)
    assert is_valid_bad is False, "Fabricated entities must trigger hallucination alarm"
    assert "quantumdb_v9" in leaks_bad and "hyperflux_engine" in leaks_bad

    # Recursive Repair Action
    repaired_claim = guardrail.recursive_repair_claim(hallucinated_tokens, fallback_filler="[UNVERIFIED]")
    assert any("[UNVERIFIED]" in t for t in repaired_claim), "Repaired claim must sanitize unverified tokens"
    print("  [✓] Zero-Hallucination Guardrail successfully identified & sanitized fabricated entities.")

    print("\n[✓✓✓] ALL NEURON N040 META-COGNITIVE INVARIANTS PASSED PERFECTLY!")


if __name__ == "__main__":
    verify_neuron_n040_invariants()
```

---

## 🔒 Operational Invariants & Execution Checklist

1. **Meta-Cognitive Gate Before High-Stakes Action**:
   - Hitung kepastian epistemik $E_c$. Jika $E_c < 0.85$, dilarang mengeksekusi operasi destruktif atau mempublikasikan kode tanpa penelusuran fakta tambahan.
2. **Reflexion Over Blind Retries**:
   - Jangan pernah melakukan *retry* dengan prompt mentah yang sama tanpa refleksi verbal eksplisit atas error sebelumnya.
3. **MCTS for Complex Algorithmic Optimization**:
   - Gunakan eksplorasi percabangan pohon pemikiran (*ToT/MCTS*) untuk masalah dengan ruang pencarian diskrit (pembuktian invariant, SWE-bench bug localization, arsitektur sistem multi-komponen).
4. **Zero Tolerance for Hallucinated APIs/Entities**:
   - Selalu lakukan *grounding check* terhadap dependensi dan modul yang terinstal sebelum menuliskan kode impor.
