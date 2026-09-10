"""Unit test lengkap untuk modul dan agen Self-Learning Framework."""

import json
import tempfile
import unittest
from pathlib import Path
from self_learning import (
    CriticAgent,
    CritiqueReport,
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
    """Pengujian terotomatisasi untuk komponen self-learning (store terisolasi di direktori sementara)."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_store_path = Path(self.temp_dir.name) / "test_store.json"
        self.store = KnowledgeStore(self.test_store_path)

    def tearDown(self):
        self.temp_dir.cleanup()

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
        self.assertEqual(self.store.count(), 1)
        self.assertIs(self.store.get("test_01"), entry)
        self.assertIsNone(self.store.get("missing"))

        # Muat ulang dari disk
        reloaded_store = KnowledgeStore(self.test_store_path)
        items = reloaded_store.get_by_task("unit_test")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].pattern, "Pola Validasi Input")
        self.assertEqual(items[0].impact_score, 0.85)

    def test_knowledge_store_tolerates_corrupt_file_and_unknown_fields(self):
        """Berkas rusak -> store kosong; entri dengan field asing dilewati tanpa menggugurkan store."""
        self.test_store_path.write_text("{not json", encoding="utf-8")
        self.assertEqual(KnowledgeStore(self.test_store_path).count(), 0)

        valid = {
            "entry_id": "ok", "task_type": "t", "category": "heuristic",
            "pattern": "p", "explanation": "e", "impact_score": 0.5,
        }
        invalid = dict(valid, entry_id="bad", unknown_field="x")
        self.test_store_path.write_text(json.dumps({"ok": valid, "bad": invalid}), encoding="utf-8")
        store = KnowledgeStore(self.test_store_path)
        self.assertEqual(store.count(), 1)
        self.assertIsNotNone(store.get("ok"))

    def test_knowledge_store_save_is_atomic(self):
        """Tidak ada berkas sementara yang tertinggal setelah penyimpanan."""
        self.store.add(KnowledgeEntry("a", "t", "heuristic", "p", "e", 0.1))
        leftovers = [p for p in self.test_store_path.parent.iterdir() if p.suffix == ".tmp"]
        self.assertEqual(leftovers, [])
        self.assertTrue(self.test_store_path.exists())

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

    def test_observer_warmup_unpacks_tuple_arguments(self):
        """Warmup wajib memakai konvensi argumen yang sama dengan loop utama (tuple = *args)."""
        calls = []

        def add(a, b):
            calls.append((a, b))
            return a + b

        observer = ObserverAgent(warmup_runs=2)
        report = observer.observe(add, [TestCase("1+2", (1, 2), 3)])

        self.assertEqual(report.pass_rate, 1.0)
        # 2 warmup + 1 pengukuran, semuanya dipanggil dengan dua argumen terpisah
        self.assertEqual(calls, [(1, 2), (1, 2), (1, 2)])

    def test_observer_empty_test_cases(self):
        """Tanpa kasus uji: tidak ada pembagian dengan nol."""
        report = ObserverAgent().observe(lambda x: x, [])
        self.assertEqual(report.total_tests, 0)
        self.assertEqual(report.pass_rate, 0.0)
        self.assertEqual(report.average_execution_time_ms, 0.0)

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

    def test_critic_detects_edge_case_in_tuple_inputs(self):
        """Input multi-argumen ([], 42) tetap terdeteksi sebagai edge case (koleksi kosong)."""
        report = ExecutionReport(
            total_tests=2, passed_tests=1, failed_tests=1, pass_rate=0.5,
            total_execution_time_ms=1.0, average_execution_time_ms=0.5,
            failure_details=[{"test_name": "Empty", "inputs": ([], 42), "error_type": "ValueError"}],
        )
        critique = CriticAgent().evaluate(report)
        self.assertTrue(any("edge case" in b for b in critique.identified_bottlenecks))
        # Bottleneck edge case dilaporkan sekali meskipun beberapa kasus gagal
        report.failure_details.append({"test_name": "Zero", "inputs": 0, "error_type": "ValueError"})
        critique2 = CriticAgent().evaluate(report)
        self.assertEqual(sum("edge case" in b for b in critique2.identified_bottlenecks), 1)

    def test_distiller_never_learns_partially_failing_strategy_as_heuristic(self):
        """Strategi cepat tapi gagal sebagian tes tidak boleh disuling sebagai 'Strategi Optimal'."""
        distiller = DistillerAgent(self.store)
        partial_report = ExecutionReport(
            total_tests=5, passed_tests=4, failed_tests=1, pass_rate=0.8,
            total_execution_time_ms=0.05, average_execution_time_ms=0.01,
            failure_details=[{"test_name": "Empty", "inputs": ([], 1), "expected": None, "error_type": "ValueError"}],
        )
        partial_critique = CritiqueReport(
            is_converged=False, fitness_score=86.0, correctness_grade="PARTIAL", latency_evaluation="ok",
        )
        entries = distiller.distill("t", 1, partial_report, partial_critique, {"strategy_name": "Buggy"})
        self.assertEqual([e.category for e in entries], ["anti_pattern"])
        self.assertEqual(entries[0].metadata["strategy_name"], "Buggy")
        self.assertEqual(self.store.get_heuristics("t"), [])

        full_report = ExecutionReport(
            total_tests=5, passed_tests=5, failed_tests=0, pass_rate=1.0,
            total_execution_time_ms=0.05, average_execution_time_ms=0.01,
        )
        full_critique = CritiqueReport(
            is_converged=True, fitness_score=100.0, correctness_grade="PASS", latency_evaluation="ok",
        )
        entries = distiller.distill("t", 2, full_report, full_critique, {"strategy_name": "Good"})
        self.assertEqual([e.category for e in entries], ["heuristic"])
        self.assertEqual(entries[0].impact_score, 1.0)

    def test_optimizer_prefers_memory_and_penalizes_known_failures(self):
        """Kandidat dengan nama strategi yang tercatat gagal diberi penalti; yang sukses dibonus."""
        self.store.add(KnowledgeEntry("h1", "t", "heuristic", "Strategi Optimal: Fast", "e", 1.0,
                                      metadata={"strategy_name": "Fast"}))
        self.store.add(KnowledgeEntry("a1", "t", "anti_pattern", "Kegagalan pengujian pada input: ([], 1)", "e", -0.8,
                                      metadata={"strategy_name": "Buggy"}))
        optimizer = OptimizerAgent(self.store)
        candidates = [
            {"name": "Buggy", "fn": lambda: None},
            {"name": "Unknown", "fn": lambda: None},
            {"name": "Fast", "fn": lambda: None},
        ]
        self.assertEqual(optimizer.select_best_candidate("t", candidates)["name"], "Fast")
        # Tanpa memori: urutan asli dipertahankan (sort stabil)
        self.assertEqual(optimizer.select_best_candidate("other", candidates)["name"], "Buggy")
        with self.assertRaises(ValueError):
            optimizer.select_best_candidate("t", [])

    def test_engine_rejects_invalid_inputs(self):
        engine = SelfLearningEngine("t", store=self.store)
        with self.assertRaises(ValueError):
            engine.run([{"name": "no-fn"}], [TestCase("x", 1, 1)])
        with self.assertRaises(ValueError):
            engine.run([{"name": "ok", "fn": lambda x: x}], [TestCase("x", 1, 1)], max_iterations=0)

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
        self.assertIsNotNone(res.best_execution_report)

    def test_engine_with_empty_candidate_pool(self):
        res = SelfLearningEngine("t", store=self.store).run([], [TestCase("x", 1, 1)])
        self.assertFalse(res.is_converged)
        self.assertEqual(res.total_iterations, 0)
        self.assertEqual(res.best_candidate_name, "None")
        self.assertIsNone(res.best_execution_report)


if __name__ == "__main__":
    unittest.main()
