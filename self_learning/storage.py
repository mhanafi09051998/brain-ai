"""Modul Storage untuk persistensi pengetahuan Self-Learning."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class KnowledgeEntry:
    """Representasi satu butir pengetahuan yang dipelajari."""

    entry_id: str
    task_type: str
    category: str  # 'heuristic' atau 'anti_pattern'
    pattern: str
    explanation: str
    impact_score: float  # -1.0 (sangat buruk) s/d +1.0 (sangat baik)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeStore:
    """Penyimpanan memori persisten berbasis JSON untuk siklus self-learning."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            storage_path = Path(__file__).parent / "knowledge_base" / "learned_patterns.json"
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: Dict[str, KnowledgeEntry] = {}
        self.load()

    def add(self, entry: KnowledgeEntry) -> None:
        """Menambahkan entri pengetahuan baru dan menyimpan ke disk."""
        self._entries[entry.entry_id] = entry
        self.save()

    def get_by_task(self, task_type: str) -> List[KnowledgeEntry]:
        """Mengambil seluruh pengetahuan terkait tipe tugas tertentu."""
        return [e for e in self._entries.values() if e.task_type == task_type]

    def get_heuristics(self, task_type: str) -> List[KnowledgeEntry]:
        """Mengambil heuristik sukses yang terbukti positif."""
        return [
            e
            for e in self.get_by_task(task_type)
            if e.category == "heuristic" and e.impact_score > 0
        ]

    def get_anti_patterns(self, task_type: str) -> List[KnowledgeEntry]:
        """Mengambil anti-pola yang harus dihindari."""
        return [
            e
            for e in self.get_by_task(task_type)
            if e.category == "anti_pattern"
        ]

    def save(self) -> None:
        """Menyimpan seluruh memori ke file JSON."""
        data = {eid: asdict(entry) for eid, entry in self._entries.items()}
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self) -> None:
        """Memuat memori yang tersimpan dari file JSON jika ada."""
        if not self.storage_path.exists():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                for eid, item in raw_data.items():
                    self._entries[eid] = KnowledgeEntry(**item)
        except (json.JSONDecodeError, IOError):
            self._entries = {}

    def clear(self) -> None:
        """Membersihkan seluruh memori (digunakan untuk reset atau testing)."""
        self._entries.clear()
        if self.storage_path.exists():
            self.storage_path.unlink()
