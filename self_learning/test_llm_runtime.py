"""Unit test untuk semantic search KnowledgeStore dan LLM runtime nyata (mocked provider)."""

import tempfile
import unittest
from pathlib import Path

from self_learning import (
    GeminiProvider,
    KnowledgeEntry,
    KnowledgeStore,
    LLMError,
    LLMExecutor,
    LLMMessage,
    LLMResponse,
    OpenAIChatProvider,
    PromptOptimizer,
)
from self_learning.llm_runtime import _http_post_json, build_contextual_prompt


class _MockProvider:
    """Provider tiruan yang merekam pesan dan mengembalikan respons deterministik."""

    provider_name = "mock"

    def __init__(self, text="OK", fail_times=0, fail_message="mock down"):
        self.text = text
        self.fail_times = fail_times
        self.fail_message = fail_message
        self.calls = []

    def complete(self, messages):
        if self.fail_times > 0:
            self.fail_times -= 1
            raise LLMError(self.fail_message)
        self.calls.append([{"role": m.role, "content": m.content} for m in messages])
        return LLMResponse(text=self.text, provider="mock", model="mock-model", latency_ms=0.5)


class TestKnowledgeStoreSemanticSearch(unittest.TestCase):
    """Pengujian pencarian semantik TF-IDF tanpa dependensi eksternal."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = KnowledgeStore(Path(self.temp_dir.name) / "kb.json")
        self.store.add(KnowledgeEntry("e1", "algoritma", "heuristic",
            "Binary search lebih cepat dari linear search untuk array terurut",
            "Gunakan binary search ketika data terurut dan ukuran besar.", 1.0))
        self.store.add(KnowledgeEntry("e2", "web", "anti_pattern",
            "Hindari render blocking CSS di header HTML",
            "CSS blocking menunda first paint dan menurunkan skor Lighthouse.", -0.8))
        self.store.add(KnowledgeEntry("e3", "algoritma", "heuristic",
            "Validasi panjang array sebelum akses indeks",
            "Cegah IndexError dengan boundary check.", 0.9))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_semantic_search_ranks_relevant_entry_first(self):
        results = self.store.search_semantic("algoritma pencarian binary search array terurut")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0].entry_id, "e1")
        self.assertGreater(results[0][1], 0.0)

    def test_semantic_search_respects_limit_and_min_score(self):
        results = self.store.search_semantic("array index", limit=1)
        self.assertEqual(len(results), 1)
        # min_score sangat tinggi -> tidak ada hasil
        empty = self.store.search_semantic("array index", min_score=0.99)
        self.assertEqual(empty, [])

    def test_semantic_search_rejects_invalid_limit(self):
        with self.assertRaises(ValueError):
            self.store.search_semantic("apa saja", limit=0)

    def test_semantic_search_empty_query_or_empty_store(self):
        self.assertEqual(self.store.search_semantic(""), [])
        empty_store = KnowledgeStore(Path(self.temp_dir.name) / "empty.json")
        self.assertEqual(empty_store.search_semantic("binary search"), [])

    def test_semantic_search_ignores_stopwords(self):
        results = self.store.search_semantic("yang dan di ke dari untuk")
        self.assertEqual(results, [])


class TestPromptOptimizer(unittest.TestCase):
    """Pengujian tahap prompt optimization (pendekatan #2)."""

    def setUp(self):
        self.provider = _MockProvider(text="Search a sorted integer array for a target value using binary search.")
        self.optimizer = PromptOptimizer(self.provider)

    def test_optimize_sends_task_and_returns_english_prompt(self):
        response = self.optimizer.optimize(
            task_name="cari_array",
            intended_goal="Cari angka 42 di array terurut secepat mungkin",
            acceptance_criteria=["hasil benar", "latensi rendah"],
)
        self.assertIn("binary search", response.text.lower())
        user_content = self.provider.calls[0][1]["content"]
        self.assertIn("cari_array", user_content)
        self.assertIn("Cari angka 42", user_content)

    def test_optimize_includes_reflection_feedback_when_present(self):
        self.optimizer.optimize("t", "tujuan", ["kriteria"], reflection_feedback="percobaan #1 gagal")
        user_content = self.provider.calls[0][1]["content"]
        self.assertIn("percobaan #1 gagal", user_content)


class TestLLMExecutor(unittest.TestCase):
    """Pengujian integrasi LLM runtime: retrieve -> optimize -> call -> distill."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = KnowledgeStore(Path(self.temp_dir.name) / "kb.json")
        self.store.add(KnowledgeEntry("h1", "search", "heuristic",
            "Binary search O(log N) untuk array terurut",
            "Gunakan algoritma binary search ketika data sudah terurut.", 1.0))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_execute_success_with_semantic_retrieval_and_distillation(self):
        executor = LLMExecutor(_MockProvider(text="42 ditemukan"), knowledge_store=self.store)
        result = executor.execute(
            task_name="cari_nilai",
            intended_goal="Temukan nilai 42 di array menggunakan binary search",
            acceptance_criteria=["Output harus mengandung 42"],
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["retrieved_count"], 1)
        self.assertEqual(result["retrieved_entries"], ["h1"])
        distilled = [e for e in self.store._entries.values() if e.entry_id.startswith("llm-distill-cari_nilai")]
        self.assertEqual(len(distilled), 1)
        self.assertTrue(distilled[0].entry_id.startswith("llm-distill-cari_nilai"))

    def test_execute_without_optimizer_keeps_original_goal(self):
        executor = LLMExecutor(_MockProvider(text="done"), knowledge_store=self.store)
        result = executor.execute("t", "tujuan asli bahasa indonesia", ["kriteria"])
        self.assertTrue(result["success"])
        self.assertIsNone(result["optimized_goal"])

    def test_execute_with_prompt_optimizer_translates_goal(self):
        optimized_text = "Find value 42 in a sorted array using binary search."
        main_provider = _MockProvider(text="42 found")
        optimizer = PromptOptimizer(_MockProvider(text=optimized_text))
        executor = LLMExecutor(main_provider, knowledge_store=self.store, prompt_optimizer=optimizer)
        result = executor.execute(
            "cari_array",
            "Cari angka 42 di array terurut",
            ["hasil harus 42"],
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["optimized_goal"], optimized_text)
        # Prompt utama harus memakai goal hasil optimasi, bukan teks Indonesia
        main_user = main_provider.calls[0][1]["content"]
        self.assertIn(optimized_text, main_user)
        self.assertNotIn("Cari angka 42", main_user)

    def test_execute_retries_on_provider_failure(self):
        provider = _MockProvider(text="42", fail_times=1, fail_message="network blip")
        executor = LLMExecutor(provider, knowledge_store=self.store)
        result = executor.execute("t", "goal", ["kriteria"], max_attempts=2)
        self.assertTrue(result["success"])
        self.assertEqual(result["attempt"], 2)
        self.assertEqual(len(result["history"]), 1)
        self.assertIn("network blip", result["history"][0]["error"])

    def test_execute_exhausts_all_attempts(self):
        provider = _MockProvider(text="x", fail_times=99, fail_message="always down")
        executor = LLMExecutor(provider, knowledge_store=self.store)
        result = executor.execute("t", "goal", ["kriteria"], max_attempts=3)
        self.assertFalse(result["success"])
        self.assertEqual(result["attempts"], 3)

    def test_execute_rejects_invalid_response_via_callable_validator(self):
        provider = _MockProvider(text="jawaban tidak sesuai")
        executor = LLMExecutor(provider, knowledge_store=self.store)
        result = executor.execute("t", "goal", [lambda text: "42" in text], max_attempts=1)
        self.assertFalse(result["success"])
        self.assertIn("Validator", result["last_error"])


class TestPromptBuilder(unittest.TestCase):
    """Pengujian builder pesan kontekstual."""

    def test_build_contextual_prompt_includes_knowledge_and_criteria(self):
        entry = KnowledgeEntry("k1", "t", "anti_pattern", "Jangan lakukan X", "Alasan X buruk.", -0.8)
        messages = build_contextual_prompt("tugas", "tujuan", ["krit A"], [entry])
        self.assertEqual(messages[0].role, "system")
        user = messages[1].content
        self.assertIn("ANTI PATTERN", user)
        self.assertIn("Jangan lakukan X", user)
        self.assertIn("krit A", user)

    def test_build_contextual_prompt_without_knowledge(self):
        messages = build_contextual_prompt("t", "g", ["c"], [])
        self.assertEqual(len(messages), 2)
        self.assertNotIn("KNOWLEDGE BASE", messages[1].content)


if __name__ == "__main__":
    unittest.main()
