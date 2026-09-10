"""Observer Agent: Bertugas mengamati eksekusi, mengukur metrik empiris, dan menangkap kegagalan."""

import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class TestCase:
    """Spesifikasi kasus uji empiris.

    `inputs` bertipe tuple diperlakukan sebagai daftar argumen posisional
    (`fn(*inputs)`); tipe lain diteruskan sebagai satu argumen (`fn(inputs)`).
    """

    name: str
    inputs: Any
    expected_output: Any
    comparator: Optional[Callable[[Any, Any], bool]] = None


@dataclass
class ExecutionReport:
    """Laporan hasil observasi eksekusi kandidat fungsi."""

    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float  # 0.0 s/d 1.0
    total_execution_time_ms: float
    average_execution_time_ms: float
    failure_details: List[Dict[str, Any]] = field(default_factory=list)
    raw_outputs: List[Any] = field(default_factory=list)


def invoke_candidate(candidate_fn: Callable, inputs: Any) -> Any:
    """Memanggil fungsi kandidat dengan konvensi argumen TestCase (tuple = *args)."""
    if isinstance(inputs, tuple):
        return candidate_fn(*inputs)
    return candidate_fn(inputs)


class ObserverAgent:
    """Agen pengamat yang menguji fungsi kandidat secara empiris dan mencatat telemetri."""

    def __init__(self, warmup_runs: int = 1):
        self.warmup_runs = warmup_runs

    def observe(self, candidate_fn: Callable, test_cases: List[TestCase]) -> ExecutionReport:
        """Menjalankan fungsi kandidat terhadap seluruh test case dan mencatat metrik empiris."""
        total = len(test_cases)
        passed = 0
        failures = []
        raw_outputs = []
        execution_times: List[float] = []

        # Warmup (cache/JIT/import lazy) agar pengukuran latensi pertama tidak bias
        if test_cases:
            for _ in range(self.warmup_runs):
                try:
                    invoke_candidate(candidate_fn, test_cases[0].inputs)
                except Exception:
                    pass

        for tc in test_cases:
            t_start = time.perf_counter()
            try:
                actual = invoke_candidate(candidate_fn, tc.inputs)

                t_end = time.perf_counter()
                elapsed_ms = (t_end - t_start) * 1000.0
                execution_times.append(elapsed_ms)
                raw_outputs.append(actual)

                # Evaluasi komparator
                if tc.comparator is not None:
                    is_match = tc.comparator(actual, tc.expected_output)
                else:
                    is_match = (actual == tc.expected_output)

                if is_match:
                    passed += 1
                else:
                    failures.append({
                        "test_name": tc.name,
                        "inputs": tc.inputs,
                        "expected": tc.expected_output,
                        "actual": actual,
                        "error_type": "AssertionMismatch",
                        "latency_ms": elapsed_ms,
                    })
            except Exception as e:
                t_end = time.perf_counter()
                elapsed_ms = (t_end - t_start) * 1000.0
                execution_times.append(elapsed_ms)
                failures.append({
                    "test_name": tc.name,
                    "inputs": tc.inputs,
                    "expected": tc.expected_output,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc(),
                    "latency_ms": elapsed_ms,
                })

        total_time = sum(execution_times)
        avg_time = (total_time / total) if total > 0 else 0.0
        pass_rate = (passed / total) if total > 0 else 0.0

        return ExecutionReport(
            total_tests=total,
            passed_tests=passed,
            failed_tests=total - passed,
            pass_rate=pass_rate,
            total_execution_time_ms=total_time,
            average_execution_time_ms=avg_time,
            failure_details=failures,
            raw_outputs=raw_outputs,
        )
