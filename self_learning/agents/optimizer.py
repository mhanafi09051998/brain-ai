"""Optimizer Agent: Menghasilkan kandidat solusi yang diperbaiki berdasarkan kritik dan memori heuristik."""

from typing import Any, Callable, Dict, List, Optional
from ..storage import KnowledgeStore
from .critic import CritiqueReport


class OptimizerAgent:
    """Agen pengoptimal yang merumuskan dan memilih kandidat perbaikan berikutnya."""

    def __init__(self, store: Optional[KnowledgeStore] = None):
        self.store = store or KnowledgeStore()

    def select_best_candidate(
        self,
        task_type: str,
        candidates: List[Dict[str, Any]],
        critique: Optional[CritiqueReport] = None,
    ) -> Dict[str, Any]:
        """Memilih kandidat terbaik berikutnya berdasarkan memori heuristik dan kritik sebelumnya."""
        heuristics = self.store.get_heuristics(task_type)
        anti_patterns = self.store.get_anti_patterns(task_type)

        # Berikan skor awal pada tiap kandidat berdasarkan kesesuaian dengan memori heuristik
        scored_candidates = []
        for cand in candidates:
            score = 0.0
            cand_name = cand.get("name", "").lower()

            # Bonus jika selaras dengan pola sukses yang tersimpan
            for h in heuristics:
                if any(word in h.pattern.lower() for word in cand_name.split()):
                    score += 2.0 * h.impact_score

            # Penalti jika mengandung anti-pola yang pernah gagal
            for ap in anti_patterns:
                if any(word in ap.pattern.lower() for word in cand_name.split()):
                    score -= 3.0

            scored_candidates.append((score, cand))

        # Urutkan dari skor tertinggi
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return scored_candidates[0][1] if scored_candidates else candidates[0]
