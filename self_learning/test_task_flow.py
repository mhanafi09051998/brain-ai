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

    def test_pipeline_success_first_try(self):
        """Pipeline berhasil pada percobaan pertama."""
        def executor(ctx, feedback):
            return {"status": "ok", "value": 42}

        def verifier(output):
            return output.get("status") == "ok" and output.get("value") == 42

        context = self.orchestrator.run_pipeline(
            task_name="test_addition",
            intended_goal="Menghasilkan nilai 42",
            acceptance_criteria=["value == 42", "status == ok"],
            grounded_files=["data.py"],
            plan_steps=["Langkah 1: Hitung 42"],
            executor_fn=executor,
            verifier_fn=verifier,
        )

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

    def test_pipeline_retry_with_reflection(self):
        """Pipeline gagal pada percobaan 1, refleksi aktif, dan berhasil pada percobaan 2."""
        counter = {"attempts": 0}

        def executor(ctx, feedback):
            counter["attempts"] += 1
            if counter["attempts"] == 1:
                return {"val": 10}  # Salah
            return {"val": 42}      # Benar setelah refleksi

        def verifier(output):
            return output.get("val") == 42

        context = self.orchestrator.run_pipeline(
            task_name="test_self_heal",
            intended_goal="Menghasilkan nilai 42",
            acceptance_criteria=["val == 42"],
            grounded_files=["ref.py"],
            plan_steps=["Kalkulasi bertahap"],
            executor_fn=executor,
            verifier_fn=verifier,
        )

        self.assertTrue(context.is_success)
        self.assertEqual(counter["attempts"], 2)
        self.assertEqual(len(context.reflections), 1)
        self.assertEqual(context.reflections[0].attempt_number, 1)


if __name__ == "__main__":
    unittest.main()
