"""Modul Implementasi Mode Refleksi (Verbal Self-Reflection / Reflexion Engine)."""

import json
import traceback
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ReflectionRecord:
    """Catatan refleksi terstruktur berbasis Rubrik 4-Kuadran."""

    record_id: str
    task_name: str
    attempt_number: int
    intended_goal: str
    actual_outcome: str
    root_cause: str
    corrective_heuristic: str
    resolved: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_in_context_prompt(self) -> str:
        """Menghasilkan teks injeksi konteks refleksi untuk percobaan berikutnya."""
        status = "[BERHASIL DIPERBAIKI]" if self.resolved else "[PERINGATAN KEGAGALAN SEBELUMNYA]"
        return (
            f"=== REFLEKSI DIRI {status} (Percobaan #{self.attempt_number}) ===\n"
            f"- Target      : {self.intended_goal}\n"
            f"- Hasil Aktual: {self.actual_outcome}\n"
            f"- Akar Masalah: {self.root_cause}\n"
            f"- Tindakan    : WAJIB TERAPKAN -> {self.corrective_heuristic}\n"
            f"================================================================"
        )


class ReflexionMemoryStore:
    """Penyimpanan memori episodik khusus untuk catatan refleksi diri."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            storage_path = (
                Path(__file__).parent / "knowledge_base" / "reflections.json"
            )
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._records: Dict[str, ReflectionRecord] = {}
        self.load()

    def record(self, reflection: ReflectionRecord) -> None:
        """Menyimpan catatan refleksi baru."""
        self._records[reflection.record_id] = reflection
        self.save()

    def get_reflections_for_task(
        self, task_name: str, unresolved_only: bool = False
    ) -> List[ReflectionRecord]:
        """Mengambil seluruh catatan refleksi untuk tugas tertentu."""
        records = [
            r for r in self._records.values() if r.task_name == task_name
        ]
        if unresolved_only:
            records = [r for r in records if not r.resolved]
        return sorted(records, key=lambda r: r.attempt_number)

    def resolve(self, record_id: str) -> None:
        """Menandai bahwa kegagalan telah berhasil diatasi."""
        if record_id in self._records:
            self._records[record_id].resolved = True
            self.save()

    def save(self) -> None:
        """Menyimpan catatan refleksi ke file JSON."""
        data = {rid: asdict(rec) for rid, rec in self._records.items()}
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self) -> None:
        """Memuat catatan refleksi dari file JSON jika ada."""
        if not self.storage_path.exists():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                for rid, item in raw_data.items():
                    self._records[rid] = ReflectionRecord(**item)
        except (json.JSONDecodeError, IOError):
            self._records = {}

    def clear(self) -> None:
        """Membersihkan memori refleksi."""
        self._records.clear()
        if self.storage_path.exists():
            self.storage_path.unlink()


class ReflectionAgent:
    """Agen yang bertugas menganalisis kegagalan dan merumuskan refleksi kausal terstruktur."""

    def __init__(self, memory_store: Optional[ReflexionMemoryStore] = None):
        self.memory = memory_store or ReflexionMemoryStore()

    def formulate_reflection(
        self,
        task_name: str,
        attempt_number: int,
        intended_goal: str,
        error: Exception,
        context_inputs: Any = None,
    ) -> ReflectionRecord:
        """Menganalisis kegagalan/exception dan merumuskan rubrik 4-kuadran secara otomatis."""
        err_type = type(error).__name__
        err_msg = str(error)

        actual_outcome = f"{err_type}: {err_msg} pada input {context_inputs}"

        # Diagnosis akar masalah berbasis pola exception umum
        if isinstance(error, IndexError):
            root_cause = "Mengakses indeks di luar rentang batas koleksi/array tanpa validasi panjang (boundary check)."
            corrective_heuristic = "Tambahkan guard clause `if not collection or index >= len(collection)` sebelum mengakses indeks."
        elif isinstance(error, KeyError):
            root_cause = f"Mengakses kunci dictionary '{err_msg}' yang tidak ada dalam mapping."
            corrective_heuristic = f"Gunakan method `.get('{err_msg}', default_value)` atau periksa `if '{err_msg}' in mapping`."
        elif isinstance(error, ZeroDivisionError):
            root_cause = "Melakukan pembagian dengan nilai nol pada operasi aritmatika."
            corrective_heuristic = "Pastikan penyebut tidak bernilai 0 sebelum operasi pembagian, atau tetapkan fallback penanganan khusus."
        elif isinstance(error, TypeError):
            root_cause = f"Ketidaksesuaian tipe data pada operasi: {err_msg}."
            corrective_heuristic = "Lakukan type casting eksplisit atau validasi tipe data menggunakan `isinstance()` sebelum operasi."
        elif isinstance(error, AssertionError):
            root_cause = f"Kondisi logika pengujian tidak terpenuhi: {err_msg}."
            corrective_heuristic = "Tinjau kembali formula komputasi dan bandingkan step-by-step dengan spesifikasi ekspektasi."
        else:
            root_cause = f"Galat runtime {err_type} terjadi pada eksekusi kode: {err_msg}."
            corrective_heuristic = "Isolasi blok rawan galat dengan penanganan kasus batas (edge-case sanitization)."

        record = ReflectionRecord(
            record_id=f"refl_{uuid.uuid4().hex[:8]}",
            task_name=task_name,
            attempt_number=attempt_number,
            intended_goal=intended_goal,
            actual_outcome=actual_outcome,
            root_cause=root_cause,
            corrective_heuristic=corrective_heuristic,
            resolved=False,
            metadata={
                "error_type": err_type,
                "traceback": traceback.format_exc(),
                "inputs": str(context_inputs),
            },
        )

        self.memory.record(record)
        return record


class ReflectiveExecutor:
    """Eksekutor tugas dengan siklus Mode Refleksi tertutup (Attempt -> Fail -> Reflect -> Correct -> Retry)."""

    def __init__(
        self,
        task_name: str,
        intended_goal: str,
        memory_store: Optional[ReflexionMemoryStore] = None,
        max_attempts: int = 3,
    ):
        self.task_name = task_name
        self.intended_goal = intended_goal
        self.memory = memory_store or ReflexionMemoryStore()
        self.agent = ReflectionAgent(self.memory)
        self.max_attempts = max_attempts

    def execute(
        self,
        action_fn: Callable[[int, List[ReflectionRecord]], Any],
        validator_fn: Optional[Callable[[Any], bool]] = None,
    ) -> Dict[str, Any]:
        """Mengeksekusi aksi berulang dengan injeksi refleksi jika terjadi kegagalan."""
        active_reflections: List[ReflectionRecord] = []
        last_error = None
        last_result = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                # Injeksi riwayat refleksi aktif ke dalam pemanggilan aksi
                result = action_fn(attempt, active_reflections)

                # Validasi output jika ada validator
                if validator_fn is not None and not validator_fn(result):
                    raise AssertionError(f"Validator menolak output: {result}")

                # Jika sukses, tandai seluruh refleksi sebelumnya sebagai resolved
                for refl in active_reflections:
                    self.memory.resolve(refl.record_id)

                return {
                    "success": True,
                    "attempt": attempt,
                    "result": result,
                    "reflections_used": len(active_reflections),
                    "resolved_records": [r.record_id for r in active_reflections],
                }

            except Exception as e:
                last_error = e
                # Formulasi refleksi diri terhadap kegagalan ini
                reflection = self.agent.formulate_reflection(
                    task_name=self.task_name,
                    attempt_number=attempt,
                    intended_goal=self.intended_goal,
                    error=e,
                )
                active_reflections.append(reflection)

        return {
            "success": False,
            "attempts": self.max_attempts,
            "last_error": str(last_error),
            "reflections_generated": [r.record_id for r in active_reflections],
        }
