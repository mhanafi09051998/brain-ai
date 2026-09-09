"""Unit test lengkap untuk modul dan agen Self-Learning Framework."""

import unittest
from pathlib import Path
from self_learning import (
    CriticAgent,
    DistillerAgent,
    ExecutionReport,
    KnowledgeEntry,
    KnowledgeStore,
    ObserverAgent,
    OptimizerAgent,
    SelfLearningEngine,
    TargetProfile,
    TestCase,
)


class TestSelfLearningFramework(unittest.TestCase):
    """Pengujian terotomatisasi untuk komponen self-learning."""

    def setUp(self):
        self.test_store_path = Path(__file__).parent / "knowledge_base" / "test_store.json"
        self.store = KnowledgeStore(self.test_store_path)
        self.store.clear()

    def tearDown(self):
        self.store.clear()

    def test_knowledge_store_crud(self):
        """Memverifikasi operasi dasar KnowledgeStore."""
        entry = KnowledgeEntry(
            entry_id="test_01",
            task_type="unit_test",
            category="heuristic",
            pattern="Pola Validasi Input",
            explanation="Selalu lakukan pengecekan boundary.",
            impact_score=0.85,
        )
        self.store.add(entry)

        # Muat ulang dari disk
        reloaded_store = KnowledgeStore(self.test_store_path)
        items = reloaded_store.get_by_task("unit_test")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].pattern, "Pola Validasi Input")
        self.assertEqual(items[0].impact_score, 0.85)

    def test_observer_agent_success(self):
        """Memverifikasi ObserverAgent pada fungsi valid."""
        def square(x):
            return x * x

        test_cases = [
            TestCase("Case 2", 2, 4),
            TestCase("Case 3", 3, 9),
            TestCase("Case 0", 0, 0),
        ]
        observer = ObserverAgent(warmup_runs=0)
        report = observer.observe(square, test_cases)

        self.assertEqual(report.total_tests, 3)
        self.assertEqual(report.passed_tests, 3)
        self.assertEqual(report.failed_tests, 0)
        self.assertEqual(report.pass_rate, 1.0)
        self.assertGreater(report.total_execution_time_ms, 0.0)

    def test_observer_agent_with_failures(self):
        """Memverifikasi ObserverAgent menangkap exception dan assertion error."""
        def faulty(x):
            if x == 0:
                raise ZeroDivisionError("division by zero")
            return 10 // x

        test_cases = [
            TestCase("Normal", 2, 5),
            TestCase("Mismatch", 4, 99),  # 10 // 4 = 2 != 99
            TestCase("Exception", 0, 0),
        ]
        observer = ObserverAgent(warmup_runs=0)
        report = observer.observe(faulty, test_cases)

        self.assertEqual(report.passed_tests, 1)
        self.assertEqual(report.failed_tests, 2)
        self.assertAlmostEqual(report.pass_rate, 1 / 3, places=2)
        self.assertEqual(len(report.failure_details), 2)

    def test_critic_agent_scoring(self):
        """Memverifikasi CriticAgent menghasilkan skor dan status konvergensi."""
        target = TargetProfile(min_pass_rate=1.0, max_avg_latency_ms=1.0)
        critic = CriticAgent(target)

        # Kasus 1: Pass 100% dan cepat
        rep_success = ExecutionReport(
            total_tests=5,
            passed_tests=5,
            failed_tests=0,
            pass_rate=1.0,
            total_execution_time_ms=0.5,
            average_execution_time_ms=0.1,
        )
        critique = critic.evaluate(rep_success)
        self.assertTrue(critique.is_converged)
        self.assertEqual(critique.correctness_grade, "PASS")
        self.assertEqual(critique.fitness_score, 100.0)

        # Kasus 2: Pass 50%
        rep_partial = ExecutionReport(
            total_tests=4,
            passed_tests=2,
            failed_tests=2,
            pass_rate=0.5,
            total_execution_time_ms=2.0,
            average_execution_time_ms=0.5,
        )
        critique_partial = critic.evaluate(rep_partial)
        self.assertFalse(critique_partial.is_converged)
        self.assertEqual(critique_partial.correctness_grade, "PARTIAL")

    def test_end_to_end_engine_optimization(self):
        """Memverifikasi siklus lengkap SelfLearningEngine konvergen ke solusi optimal."""
        def slow_power(base, exp):
            # O(exp)
            res = 1
            for _ in range(exp):
                res *= base
            return res

        def fast_power(base, exp):
            # O(log exp)
            return pow(base, exp)

        test_cases = [
            TestCase("Pow 2^10", (2, 10), 1024),
            TestCase("Pow 3^5", (3, 5), 243),
            TestCase("Pow 5^0", (5, 0), 1),
        ]

        target = TargetProfile(min_pass_rate=1.0)
        engine = SelfLearningEngine(
            task_type="power_algo",
            target_profile=target,
            store=self.store,
        )

        candidates = [
            {"name": "Slow Iterative Power", "fn": slow_power},
            {"name": "Fast Binary Exponentiation", "fn": fast_power},
        ]

        res = engine.run(candidates, test_cases, max_iterations=2)
        self.assertTrue(res.is_converged)
        self.assertEqual(res.best_fitness_score, 100.0)
        self.assertGreaterEqual(res.new_knowledge_count, 1)


if __name__ == "__main__":
    unittest.main()
