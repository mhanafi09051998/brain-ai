"""Self-Learning Optimization Engine: Pengorkestrasi siklus tertutup observasi, kritik, penyulingan, dan optimasi."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .agents import (
    CriticAgent,
    CritiqueReport,
    DistillerAgent,
    ExecutionReport,
    ObserverAgent,
    OptimizerAgent,
)
from .agents.critic import TargetProfile
from .agents.observer import TestCase
from .storage import KnowledgeStore


@dataclass
class IterationLog:
    """Catatan riwayat satu siklus iterasi self-learning."""

    iteration: int
    candidate_name: str
    execution_report: ExecutionReport
    critique_report: CritiqueReport


@dataclass
class OptimizationResult:
    """Hasil akhir dari proses optimasi self-learning."""

    task_type: str
    is_converged: bool
    total_iterations: int
    best_candidate_name: str
    best_fitness_score: float
    best_execution_report: Optional[ExecutionReport]  # None jika tidak ada kandidat yang dievaluasi
    iteration_history: List[IterationLog] = field(default_factory=list)
    new_knowledge_count: int = 0


class SelfLearningEngine:
    """Mesin pengorkestrasi siklus optimasi self-learning."""

    def __init__(
        self,
        task_type: str,
        target_profile: Optional[TargetProfile] = None,
        store: Optional[KnowledgeStore] = None,
    ):
        self.task_type = task_type
        self.target = target_profile if target_profile is not None else TargetProfile()
        self.store = store if store is not None else KnowledgeStore()

        # Inisialisasi agen-agen spesialis
        self.observer = ObserverAgent()
        self.critic = CriticAgent(self.target)
        self.distiller = DistillerAgent(self.store)
        self.optimizer = OptimizerAgent(self.store)

    def run(
        self,
        candidate_pool: List[Dict[str, Any]],
        test_cases: List[TestCase],
        max_iterations: int = 5,
    ) -> OptimizationResult:
        """Menjalankan loop self-learning hingga konvergen atau mencapai batas maksimum iterasi."""
        if max_iterations < 1:
            raise ValueError("max_iterations harus >= 1.")
        for cand in candidate_pool:
            if not callable(cand.get("fn")):
                raise ValueError(f"Kandidat {cand.get('name', cand)!r} tidak memiliki 'fn' yang callable.")

        history: List[IterationLog] = []
        best_candidate: Optional[Dict[str, Any]] = None
        best_fitness: float = -1.0
        best_exec_report: Optional[ExecutionReport] = None
        total_new_knowledge = 0

        remaining_candidates = list(candidate_pool)
        last_critique: Optional[CritiqueReport] = None

        for iter_idx in range(1, max_iterations + 1):
            if not remaining_candidates:
                break

            # 1. Pilih kandidat berikutnya menggunakan OptimizerAgent dengan bantuan knowledge base
            selected_cand = self.optimizer.select_best_candidate(
                self.task_type, remaining_candidates, last_critique
            )
            remaining_candidates.remove(selected_cand)

            cand_name = selected_cand.get("name", f"Candidate_{iter_idx}")
            cand_fn = selected_cand["fn"]

            # 2. OBSERVE: Jalankan pengujian empiris dan kumpulkan metrik
            exec_report = self.observer.observe(cand_fn, test_cases)

            # 3. CRITIQUE: Nilai kesesuaian terhadap target
            critique = self.critic.evaluate(exec_report)
            last_critique = critique

            # 4. DISTILL: Ekstraksi temuan ke knowledge store
            new_entries = self.distiller.distill(
                task_type=self.task_type,
                iteration=iter_idx,
                execution_report=exec_report,
                critique_report=critique,
                candidate_meta={"strategy_name": cand_name},
            )
            total_new_knowledge += len(new_entries)

            # Catat riwayat
            history.append(
                IterationLog(
                    iteration=iter_idx,
                    candidate_name=cand_name,
                    execution_report=exec_report,
                    critique_report=critique,
                )
            )

            # Lacak kandidat terbaik
            if critique.fitness_score > best_fitness:
                best_fitness = critique.fitness_score
                best_candidate = selected_cand
                best_exec_report = exec_report

            # 5. Hentikan lebih awal jika sudah konvergen
            if critique.is_converged:
                break

        return OptimizationResult(
            task_type=self.task_type,
            is_converged=(last_critique.is_converged if last_critique else False),
            total_iterations=len(history),
            best_candidate_name=best_candidate.get("name", "None") if best_candidate else "None",
            best_fitness_score=best_fitness,
            best_execution_report=best_exec_report,
            iteration_history=history,
            new_knowledge_count=total_new_knowledge,
        )
