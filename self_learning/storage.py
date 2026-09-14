"""Modul Storage untuk persistensi pengetahuan Self-Learning."""

import math
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Stopword ringkas (ID + EN) agar kata fungsional tidak mendominasi skor kemiripan.
_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "of", "on", "or", "that", "the", "to", "was", "were", "will",
    "with", "yang", "dan", "di", "ke", "dari", "untuk", "pada", "adalah",
    "dengan", "atau", "jika", "saat", "agar", "bisa", "akan", "tidak",
})


def _tokenize(text: str) -> List[str]:
    """Tokenisasi sederhana: huruf kecil, ambil alfanumerik, buang stopword."""
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


def atomic_write_json(path: Path, data: Any) -> None:
    """Menulis JSON secara atomik: tulis ke berkas sementara di direktori yang sama,
    lalu `os.replace` agar berkas tujuan tidak pernah korup jika proses terhenti."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def load_json_dict(path: Path) -> Dict[str, Any]:
    """Memuat objek JSON dari disk. Berkas yang tidak ada, rusak, atau bukan objek
    diperlakukan sebagai store kosong."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


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

    def count(self) -> int:
        """Jumlah entri yang tersimpan. (Sengaja bukan `__len__`: store kosong harus tetap
        truthy agar idiom `store or KnowledgeStore()` tidak mengganti store yang diberikan.)"""
        return len(self._entries)

    def add(self, entry: KnowledgeEntry) -> None:
        """Menambahkan (atau menimpa berdasarkan entry_id) entri pengetahuan dan menyimpan ke disk."""
        self._entries[entry.entry_id] = entry
        self.save()

    def get(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Mengambil satu entri berdasarkan ID, atau None jika tidak ada."""
        return self._entries.get(entry_id)

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
        """Menyimpan seluruh memori ke file JSON secara atomik."""
        data = {eid: asdict(entry) for eid, entry in self._entries.items()}
        atomic_write_json(self.storage_path, data)

    def load(self) -> None:
        """Memuat memori dari file JSON jika ada. Entri yang skemanya tidak cocok dilewati,
        bukan menggugurkan seluruh store."""
        self._entries = {}
        for eid, item in load_json_dict(self.storage_path).items():
            try:
                self._entries[eid] = KnowledgeEntry(**item)
            except TypeError:
                continue

    def clear(self) -> None:
        """Membersihkan seluruh memori (digunakan untuk reset atau testing)."""
        self._entries.clear()
        if self.storage_path.exists():
            self.storage_path.unlink()

    def search_semantic(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.0,
    ) -> List[tuple]:
        """Pencarian semantik berbasis TF-IDF + cosine similarity (stdlib murni).

        Mengembalikan daftar `(KnowledgeEntry, score)` diurutkan dari skor tertinggi.
        Skor berada pada rentang 0.0 s/d 1.0. Entry yang tidak memiliki token
        relevan tidak dikembalikan.
        """
        if limit < 1:
            raise ValueError("limit harus >= 1.")
        query_tokens = _tokenize(query)
        if not query_tokens or not self._entries:
            return []

        # Korpus dokumen = pattern + explanation + task_type per entry.
        docs: Dict[str, List[str]] = {}
        for eid, entry in self._entries.items():
            docs[eid] = _tokenize(
                f"{entry.pattern} {entry.explanation} {entry.task_type}"
            )

        # DF (document frequency) untuk smoothing IDF.
        df: Dict[str, int] = {}
        for tokens in docs.values():
            for term in set(tokens):
                df[term] = df.get(term, 0) + 1

        n_docs = len(docs)

        def _tfidf(tokens: List[str]) -> Dict[str, float]:
            tf: Dict[str, float] = {}
            for term in tokens:
                tf[term] = tf.get(term, 0.0) + 1.0
            total = len(tokens) if tokens else 1.0
            vec: Dict[str, float] = {}
            for term, count in tf.items():
                idf = math.log((n_docs + 1.0) / (df.get(term, 0) + 1.0)) + 1.0
                vec[term] = (count / total) * idf
            return vec

        query_vec = _tfidf(query_tokens)
        scored: List[tuple] = []
        for eid, entry in self._entries.items():
            doc_vec = _tfidf(docs[eid])
            dot = sum(query_vec.get(t, 0.0) * doc_vec.get(t, 0.0) for t in query_vec)
            q_norm = math.sqrt(sum(v * v for v in query_vec.values()))
            d_norm = math.sqrt(sum(v * v for v in doc_vec.values()))
            score = (dot / (q_norm * d_norm)) if (q_norm > 0.0 and d_norm > 0.0) else 0.0
            if score > min_score:
                scored.append((entry, round(score, 6)))

        scored.sort(key=lambda pair: (-pair[1], pair[0].entry_id))
        return scored[:limit]
