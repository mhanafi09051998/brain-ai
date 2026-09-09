"""Unit test untuk menguji komponen dan alur kerja Mode Refleksi (Reflexion Engine)."""

import unittest
from pathlib import Path
from self_learning import (
    ReflectionAgent,
    ReflectionRecord,
    ReflectiveExecutor,
    ReflexionMemoryStore,
)


class TestModeRefleksi(unittest.TestCase):
    """Test suite pengujian Mode Refleksi."""

    def setUp(self):
        self.test_store_path = (
            Path(__file__).parent / "knowledge_base" / "test_reflections.json"
        )
        self.memory = ReflexionMemoryStore(self.test_store_path)
        self.memory.clear()

    def tearDown(self):
        self.memory.clear()

    def test_reflection_record_and_prompt_injection(self):
        """Memverifikasi struktur 4-kuadran dan output prompt in-context."""
        rec = ReflectionRecord(
            record_id="refl_test",
            task_name="array_parser",
            attempt_number=1,
            intended_goal="Parse JSON array tanpa crash",
            actual_outcome="IndexError: list index out of range",
            root_cause="Mengakses index ke-0 pada list kosong",
            corrective_heuristic="Periksa panjang list sebelum mengakses index",
            resolved=False,
        )
        prompt = rec.to_in_context_prompt()
        self.assertIn("=== REFLEKSI DIRI [PERINGATAN KEGAGALAN SEBELUMNYA]", prompt)
        self.assertIn("Target      : Parse JSON array", prompt)
        self.assertIn("Akar Masalah: Mengakses index ke-0", prompt)
        self.assertIn("Tindakan    : WAJIB TERAPKAN -> Periksa panjang", prompt)

    def test_memory_store_lifecycle(self):
        """Memverifikasi siklus simpan, filter unresolved, dan resolve memori."""
        rec1 = ReflectionRecord(
            record_id="r1",
            task_name="taks_A",
            attempt_number=1,
            intended_goal="Goal 1",
            actual_outcome="Error 1",
            root_cause="Cause 1",
            corrective_heuristic="Action 1",
            resolved=False,
        )
        rec2 = ReflectionRecord(
            record_id="r2",
            task_name="taks_A",
            attempt_number=2,
            intended_goal="Goal 1",
            actual_outcome="Error 2",
            root_cause="Cause 2",
            corrective_heuristic="Action 2",
            resolved=False,
        )
        self.memory.record(rec1)
        self.memory.record(rec2)

        records = self.memory.get_reflections_for_task("taks_A", unresolved_only=True)
        self.assertEqual(len(records), 2)

        # Tandai r1 selesai
        self.memory.resolve("r1")
        unresolved = self.memory.get_reflections_for_task("taks_A", unresolved_only=True)
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0].record_id, "r2")

    def test_reflection_agent_causal_diagnosis(self):
        """Memverifikasi agen mampu mendiagnosis akar masalah dari error runtime."""
        agent = ReflectionAgent(self.memory)

        # Kasus 1: ZeroDivisionError
        try:
            _ = 10 / 0
        except ZeroDivisionError as e:
            rec = agent.formulate_reflection("div_task", 1, "Bagi angka", e)
            self.assertIn("nol", rec.root_cause.lower())
            self.assertIn("penyebut", rec.corrective_heuristic.lower())

        # Kasus 2: KeyError
        try:
            d = {"user": "alice"}
            _ = d["email"]
        except KeyError as e:
            rec2 = agent.formulate_reflection("map_task", 1, "Ambil email", e)
            self.assertIn("email", rec2.actual_outcome)
            self.assertIn("mapping", rec2.root_cause.lower())
            self.assertIn(".get(", rec2.corrective_heuristic)

    def test_reflective_executor_self_healing(self):
        """Memverifikasi eksekutor mandiri: gagal di percobaan 1, refleksi, lalu sukses di percobaan 2."""
        def buggy_operation(attempt: int, reflections: list):
            # Pada percobaan 1: kode memiliki bug (IndexError)
            # Pada percobaan 2: kode membaca refleksi dan menerapkan guard
            data = []
            if reflections:
                # Membaca refleksi sebelumnya: menerapkan guard clause
                if not data:
                    return "fallback_default"
            # Tanpa refleksi: crash
            return data[0]

        executor = ReflectiveExecutor(
            task_name="safe_element_getter",
            intended_goal="Ambil elemen pertama dari koleksi dengan aman",
            memory_store=self.memory,
            max_attempts=3,
        )

        res = executor.execute(buggy_operation)
        self.assertTrue(res["success"])
        self.assertEqual(res["attempt"], 2)
        self.assertEqual(res["result"], "fallback_default")
        self.assertEqual(res["reflections_used"], 1)

        # Verifikasi bahwa refleksi di memori sekarang sudah berstatus resolved
        all_refs = self.memory.get_reflections_for_task("safe_element_getter")
        self.assertEqual(len(all_refs), 1)
        self.assertTrue(all_refs[0].resolved)


if __name__ == "__main__":
    unittest.main()
