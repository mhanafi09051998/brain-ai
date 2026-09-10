"""Optimizer Agent: Menghasilkan kandidat solusi yang diperbaiki berdasarkan kritik dan memori heuristik."""

from typing import Any, Dict, List, Optional
from ..storage import KnowledgeEntry, KnowledgeStore
from .critic import CritiqueReport


class OptimizerAgent:
    """Agen pengoptimal yang merumuskan dan memilih kandidat perbaikan berikutnya."""

    # Bobot penilaian kandidat
    EXACT_HEURISTIC_BONUS = 5.0
    EXACT_ANTI_PATTERN_PENALTY = 5.0
    FUZZY_HEURISTIC_WEIGHT = 2.0
    FUZZY_ANTI_PATTERN_PENALTY = 3.0

    def __init__(self, store: Optional[KnowledgeStore] = None):
        self.store = store if store is not None else KnowledgeStore()

    @staticmethod
    def _entry_strategy(entry: KnowledgeEntry) -> str:
        return str(entry.metadata.get("strategy_name", "")).lower()

    def score_candidate(
        self,
        candidate: Dict[str, Any],
        heuristics: List[KnowledgeEntry],
        anti_patterns: List[KnowledgeEntry],
    ) -> float:
        """Menilai satu kandidat terhadap memori. Kecocokan nama strategi persis
        (dari metadata) diprioritaskan; kecocokan kata parsial menjadi sinyal sekunder."""
        cand_name = str(candidate.get("name", "")).lower()
        words = set(cand_name.split())
        score = 0.0

        for h in heuristics:
            if cand_name and self._entry_strategy(h) == cand_name:
                score += self.EXACT_HEURISTIC_BONUS * h.impact_score
            elif any(word in h.pattern.lower() for word in words):
                score += self.FUZZY_HEURISTIC_WEIGHT * h.impact_score

        for ap in anti_patterns:
            if cand_name and self._entry_strategy(ap) == cand_name:
                score -= self.EXACT_ANTI_PATTERN_PENALTY
            elif any(word in ap.pattern.lower() for word in words):
                score -= self.FUZZY_ANTI_PATTERN_PENALTY

        return score

    def select_best_candidate(
        self,
        task_type: str,
        candidates: List[Dict[str, Any]],
        critique: Optional[CritiqueReport] = None,
    ) -> Dict[str, Any]:
        """Memilih kandidat terbaik berikutnya berdasarkan memori heuristik dan kritik sebelumnya.
        Urutan asli dipertahankan untuk skor yang sama (sort stabil)."""
        if not candidates:
            raise ValueError("Daftar kandidat kosong; tidak ada strategi yang dapat dipilih.")

        heuristics = self.store.get_heuristics(task_type)
        anti_patterns = self.store.get_anti_patterns(task_type)

        scored = [
            (self.score_candidate(cand, heuristics, anti_patterns), idx, cand)
            for idx, cand in enumerate(candidates)
        ]
        scored.sort(key=lambda item: (-item[0], item[1]))
        return scored[0][2]
