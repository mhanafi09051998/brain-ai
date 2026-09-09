"""Distiller Agent: Menyuling temuan empiris, kegagalan, dan heuristik keberhasilan ke dalam KnowledgeStore."""

import uuid
from typing import Any, Dict, List, Optional
from ..storage import KnowledgeEntry, KnowledgeStore
from .critic import CritiqueReport
from .observer import ExecutionReport


class DistillerAgent:
    """Agen penyuling memori yang mengekstrak prinsip berulang dari hasil evaluasi."""

    def __init__(self, store: Optional[KnowledgeStore] = None):
        self.store = store or KnowledgeStore()

    def distill(
        self,
        task_type: str,
        iteration: int,
        execution_report: ExecutionReport,
        critique_report: CritiqueReport,
        candidate_meta: Optional[Dict[str, Any]] = None,
    ) -> List[KnowledgeEntry]:
        """Mengekstraksi pengetahuan baru dan menyimpannya secara persisten."""
        meta = candidate_meta or {}
        new_entries: List[KnowledgeEntry] = []

        # 1. Penyulingan Anti-Pola jika terjadi kegagalan atau hambatan
        for fail in execution_report.failure_details:
            err_type = fail.get("error_type", "Unknown")
            pattern_key = f"anti_pattern_{task_type}_{err_type}_{iteration}"
            entry = KnowledgeEntry(
                entry_id=f"ap_{uuid.uuid4().hex[:8]}",
                task_type=task_type,
                category="anti_pattern",
                pattern=f"Kegagalan pengujian pada input: {fail.get('inputs')}",
                explanation=(
                    f"Pengujian '{fail.get('test_name')}' gagal menghasilkan output yang sesuai. "
                    f"Ekspektasi: {fail.get('expected')}, Aktual: {fail.get('actual')}. "
                    f"Tipe galat: {err_type}."
                ),
                impact_score=-0.8,
                metadata={"iteration": iteration, "test_name": fail.get("test_name")},
            )
            self.store.add(entry)
            new_entries.append(entry)

        # 2. Penyulingan Bottlenecks Latensi
        for bneck in critique_report.identified_bottlenecks:
            entry = KnowledgeEntry(
                entry_id=f"ap_{uuid.uuid4().hex[:8]}",
                task_type=task_type,
                category="anti_pattern",
                pattern=f"Bottleneck Kinerja: {bneck}",
                explanation=f"Algoritma pada iterasi {iteration} mengalami hambatan efisiensi yang melampaui batas toleransi.",
                impact_score=-0.5,
                metadata={"iteration": iteration},
            )
            self.store.add(entry)
            new_entries.append(entry)

        # 3. Penyulingan Heuristik Sukses
        if critique_report.is_converged or critique_report.fitness_score >= 80.0:
            strategy_name = meta.get("strategy_name", f"Strategy_Iter_{iteration}")
            entry = KnowledgeEntry(
                entry_id=f"h_{uuid.uuid4().hex[:8]}",
                task_type=task_type,
                category="heuristic",
                pattern=f"Strategi Optimal: {strategy_name}",
                explanation=(
                    f"Solusi mencapai skor kesesuaian {critique_report.fitness_score}/100 "
                    f"dengan pass rate {execution_report.pass_rate * 100:.1f}% dan rata-rata latensi "
                    f"{execution_report.average_execution_time_ms:.4f} ms."
                ),
                impact_score=0.9,
                metadata={"iteration": iteration, "fitness_score": critique_report.fitness_score},
            )
            self.store.add(entry)
            new_entries.append(entry)

        return new_entries
