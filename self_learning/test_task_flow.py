"""Unit test untuk AgenticTaskFlow (6-Phase Closed-Loop Pipeline)."""

import tempfile
import unittest
from pathlib import Path

from self_learning.reflection import ReflexionMemoryStore
from self_learning.storage import KnowledgeStore
from self_learning.task_flow import AgenticTaskFlow, StepStatus, TaskPhase


class TestAgenticTaskFlow(unittest.TestCase):
    """Pengujian fungsionalitas pipeline AgenticTaskFlow."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        reflections_path = Path(self.temp_dir.name) / "reflections.json"
        knowledge_path = Path(self.temp_dir.name) / "knowledge.json"

        self.memory_store = ReflexionMemoryStore(storage_path=reflections_path)
        self.knowledge_store = KnowledgeStore(storage_path=knowledge_path)
        self.orchestrator = AgenticTaskFlow(
            memory_store=self.memory_store,
            knowledge_store=self.knowledge_store,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def _run(self, executor, verifier, max_attempts=3, task_name="task"):
        return self.orchestrator.run_pipeline(
            task_name=task_name,
            intended_goal="Menghasilkan nilai 42",
            acceptance_criteria=["value == 42"],
            grounded_files=["data.py"],
            plan_steps=["Langkah 1: Hitung 42"],
            executor_fn=executor,
            verifier_fn=verifier,
            max_attempts=max_attempts,
        )

    def test_pipeline_success_first_try(self):
        """Pipeline berhasil pada percobaan pertama."""
        def executor(ctx, feedback):
            return {"status": "ok", "value": 42}

        def verifier(output):
            return output.get("status") == "ok" and output.get("value") == 42

        context = self._run(executor, verifier, task_name="test_addition")

        self.assertTrue(context.is_success)
        self.assertEqual(len(context.reflections), 0)
        self.assertGreater(len(context.distilled_patterns), 0)

        # Cek tahapan alur
        phases = [step.phase for step in context.steps]
        self.assertIn(TaskPhase.INGESTION, phases)
        self.assertIn(TaskPhase.PLANNING, phases)
        self.assertIn(TaskPhase.EXECUTION, phases)
        self.assertIn(TaskPhase.VERIFICATION, phases)
        self.assertIn(TaskPhase.DISTILLATION, phases)
        self.assertNotIn(TaskPhase.REFLEXION, phases)

        # Setiap langkah verifikasi dicatat sekali dan diperbarui di tempat (bukan digandakan)
        verify_steps = [s for s in context.steps if s.phase == TaskPhase.VERIFICATION]
        self.assertEqual(len(verify_steps), 1)
        self.assertEqual(verify_steps[0].status, StepStatus.SUCCESS)
        self.assertTrue(all(s.status != StepStatus.RUNNING for s in context.steps))

        learned = self.knowledge_store.get_heuristics("test_addition")
        self.assertEqual(len(learned), 1)
        self.assertEqual(learned[0].entry_id, context.distilled_patterns[0])

    def test_pipeline_retry_with_reflection(self):
        """Pipeline gagal pada percobaan 1, refleksi aktif, dan berhasil pada percobaan 2."""
        counter = {"attempts": 0}
        feedback_seen = []

        def executor(ctx, feedback):
            counter["attempts"] += 1
            feedback_seen.append(feedback)
            if counter["attempts"] == 1:
                return {"val": 10}  # Salah
            return {"val": 42}      # Benar setelah refleksi

        def verifier(output):
            return output.get("val") == 42

        context = self._run(executor, verifier, task_name="test_self_heal")

        self.assertTrue(context.is_success)
        self.assertEqual(counter["attempts"], 2)
        self.assertEqual(len(context.reflections), 1)
        self.assertEqual(context.reflections[0].attempt_number, 1)
        # Percobaan pertama tanpa feedback; percobaan kedua menerima prompt refleksi
        self.assertIsNone(feedback_seen[0])
        self.assertIn("REFLEKSI DIRI", feedback_seen[1])
        # Refleksi ditandai resolved di memori episodik setelah sukses
        stored = self.memory_store.get_reflections_for_task("test_self_heal")
        self.assertEqual(len(stored), 1)
        self.assertTrue(stored[0].resolved)

    def test_pipeline_exception_uses_causal_diagnosis(self):
        """Exception dari eksekutor didiagnosis per tipe error (bukan pesan generik)."""
        def executor(ctx, feedback):
            if feedback is None:
                return {}["missing"]
            return 42

        context = self._run(executor, lambda out: out == 42)
        self.assertTrue(context.is_success)
        self.assertEqual(context.reflections[0].metadata["error_type"], "KeyError")
        self.assertIn("mapping", context.reflections[0].root_cause.lower())
        exec_steps = [s for s in context.steps if s.phase == TaskPhase.EXECUTION]
        self.assertEqual(exec_steps[0].status, StepStatus.FAILED)
        self.assertEqual(exec_steps[1].status, StepStatus.SUCCESS)

    def test_pipeline_exhausts_attempts_and_distills_anti_pattern(self):
        """Semua percobaan gagal: konteks gagal, refleksi tetap unresolved, anti-pola disimpan."""
        context = self._run(lambda ctx, fb: 0, lambda out: out == 42, max_attempts=2, task_name="hopeless")

        self.assertFalse(context.is_success)
        self.assertEqual(len(context.reflections), 2)
        self.assertEqual(len(self.memory_store.get_reflections_for_task("hopeless", unresolved_only=True)), 2)

        anti = self.knowledge_store.get_anti_patterns("hopeless")
        self.assertEqual(len(anti), 1)
        self.assertEqual(anti[0].metadata["attempts"], 2)
        self.assertEqual(self.knowledge_store.get_heuristics("hopeless"), [])
        self.assertEqual(context.distilled_patterns, [anti[0].entry_id])

    def test_pipeline_rejects_invalid_max_attempts(self):
        with self.assertRaises(ValueError):
            self._run(lambda ctx, fb: 42, lambda out: True, max_attempts=0)


if __name__ == "__main__":
    unittest.main()
