"""Simulasi Benchmark Mandiri untuk Framework Optimasi Self-Learning.

Kasus Uji: Optimasi Algoritma Pencarian Elemen pada Array Terurut Besar (100.000 elemen).
Menunjukkan bagaimana agen mendeteksi bottleneck latensi, kegagalan edge-case, menyuling
pengetahuan ke KnowledgeStore, dan mencapai konvergensi solusi optimal.
"""

from typing import List, Optional
from self_learning import (
    KnowledgeStore,
    SelfLearningEngine,
    TargetProfile,
    TestCase,
)


# ==================== IMPLEMENTASI KANDIDAT STRATEGI ====================

def naive_linear_search(arr: List[int], target: int) -> Optional[int]:
    """Strategi 1: Linear Search O(N) - Benar namun sangat lambat pada dataset besar."""
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return None


def buggy_binary_search(arr: List[int], target: int) -> Optional[int]:
    """Strategi 2: Binary Search cacat - Cepat tapi salah pada edge-case (tidak menangani array kosong)."""
    if not arr:
        # Sengaja cacat: melempar error saat array kosong alih-alih mengembalikan None
        raise ValueError("Array tidak boleh kosong!")

    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return None


def optimized_binary_search(arr: List[int], target: int) -> Optional[int]:
    """Strategi 3: Binary Search O(log N) - Benar, tangguh terhadap edge case, dan sangat cepat."""
    if not arr:
        return None

    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return None


# ==================== EKSEKUSI BENCHMARK ====================

def run_benchmark():
    print("=" * 70)
    print("DEMO FRAMEWORK AGENT UNTUK OPTIMASI SELF-LEARNING")
    print("=" * 70)

    # Siapkan dataset uji realistis
    large_sorted_arr = list(range(0, 200_000, 2))  # [0, 2, 4, ..., 199998] (100.000 elemen)

    test_cases = [
        TestCase(
            name="Cari Elemen di Awal",
            inputs=(large_sorted_arr, 0),
            expected_output=0,
        ),
        TestCase(
            name="Cari Elemen di Tengah",
            inputs=(large_sorted_arr, 100_000),
            expected_output=50_000,
        ),
        TestCase(
            name="Cari Elemen di Akhir",
            inputs=(large_sorted_arr, 199_998),
            expected_output=99_999,
        ),
        TestCase(
            name="Cari Elemen Ganjil (Tidak Ada)",
            inputs=(large_sorted_arr, 55_555),
            expected_output=None,
        ),
        TestCase(
            name="Edge Case: Array Kosong",
            inputs=([], 42),
            expected_output=None,
        ),
    ]

    # Tetapkan target empiris: Wajib pass 100% dan latensi rata-rata <= 0.1 ms
    target_profile = TargetProfile(
        min_pass_rate=1.0,
        max_avg_latency_ms=0.1,  # 100 mikrodetik
    )

    store = KnowledgeStore()
    store.clear()  # Mulai dengan memori bersih untuk demonstrasi

    engine = SelfLearningEngine(
        task_type="array_search_optimization",
        target_profile=target_profile,
        store=store,
    )

    candidate_pool = [
        {"name": "Naive Linear Search O(N)", "fn": naive_linear_search},
        {"name": "Buggy Binary Search", "fn": buggy_binary_search},
        {"name": "Optimized Binary Search O(log N)", "fn": optimized_binary_search},
    ]

    print(f"\n[1] Memulai Siklus Self-Learning dengan {len(candidate_pool)} kandidat strategi...")
    result = engine.run(candidate_pool=candidate_pool, test_cases=test_cases, max_iterations=5)

    print("\n" + "-" * 70)
    print("HASIL SIKLUS SELF-LEARNING:")
    print(f"Status Konvergensi : {'KONVERGEN (Target Tercapai)' if result.is_converged else 'BELUM KONVERGEN'}")
    print(f"Total Iterasi      : {result.total_iterations}")
    print(f"Kandidat Terbaik   : {result.best_candidate_name}")
    print(f"Fitness Score      : {result.best_fitness_score}/100.0")
    print(f"Pengetahuan Baru   : {result.new_knowledge_count} entri disuling ke KnowledgeStore")
    print("-" * 70)

    print("\nLOG RIWAYAT EVALUASI PER ITERASI:")
    for item in result.iteration_history:
        print(f"\n* Iterasi {item.iteration}: [{item.candidate_name}]")
        print(f"  - Pass Rate      : {item.execution_report.pass_rate * 100:.1f}% ({item.execution_report.passed_tests}/{item.execution_report.total_tests} tes)")
        print(f"  - Waktu Rata-rata: {item.execution_report.average_execution_time_ms:.5f} ms")
        print(f"  - Status Latensi : {item.critique_report.latency_evaluation}")
        print(f"  - Umpan Balik    : {item.critique_report.actionable_feedback[0] if item.critique_report.actionable_feedback else 'None'}")

    print("\n" + "=" * 70)
    print("PENGETAHUAN YANG BERHASIL DISULING KE KNOWLEDGE STORE:")
    print("=" * 70)
    for entry in store.get_by_task("array_search_optimization"):
        symbol = "[HEURISTIK]" if entry.category == "heuristic" else "[ANTI-POLA]"
        print(f"{symbol:13} {entry.pattern}")
        print(f"  Detail     : {entry.explanation}")
        print(f"  Impact     : {entry.impact_score}")
        print()


if __name__ == "__main__":
    run_benchmark()
