"""Critic Agent: Menganalisis laporan eksekusi, menghitung skor kesesuaian empiris, dan merumuskan kritik."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .observer import ExecutionReport


@dataclass
class TargetProfile:
    """Profil target yang diharapkan oleh sistem."""

    min_pass_rate: float = 1.0
    max_avg_latency_ms: Optional[float] = None
    strict_correctness: bool = True


@dataclass
class CritiqueReport:
    """Laporan kritik dan analisis performa."""

    is_converged: bool
    fitness_score: float  # 0.0 s/d 100.0
    correctness_grade: str  # 'PASS', 'PARTIAL', 'FAIL'
    latency_evaluation: str
    actionable_feedback: List[str] = field(default_factory=list)
    identified_bottlenecks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CriticAgent:
    """Agen pengkritik yang mengevaluasi apakah solusi telah memenuhi standar dan mendiagnosis kelemahan."""

    def __init__(self, target_profile: Optional[TargetProfile] = None):
        self.target = target_profile or TargetProfile()

    def evaluate(self, report: ExecutionReport) -> CritiqueReport:
        """Mengevaluasi laporan eksekusi dan menghasilkan kritik terstruktur."""
        actionable_feedback: List[str] = []
        bottlenecks: List[str] = []

        # 1. Evaluasi Kebenaran (Correctness)
        if report.pass_rate >= 1.0:
            correctness_grade = "PASS"
        elif report.pass_rate >= 0.5:
            correctness_grade = "PARTIAL"
        else:
            correctness_grade = "FAIL"

        if report.failed_tests > 0:
            actionable_feedback.append(
                f"Terdapat {report.failed_tests} dari {report.total_tests} kasus uji yang gagal "
                f"(Pass rate: {report.pass_rate * 100:.1f}%)."
            )
            # Analisis jenis kesalahan
            error_types = set()
            for fail in report.failure_details:
                err = fail.get("error_type", "Unknown")
                error_types.add(err)
                if "inputs" in fail and (fail["inputs"] == [] or fail["inputs"] == "" or fail["inputs"] == 0):
                    bottlenecks.append("Gagal menangani edge case (input kosong/nol).")

            for et in error_types:
                actionable_feedback.append(f"Terjadi error bertipe '{et}' pada kasus uji.")

        # 2. Evaluasi Latensi / Performa
        latency_eval = "Acceptable"
        latency_factor = 1.0
        if self.target.max_avg_latency_ms is not None:
            if report.average_execution_time_ms > self.target.max_avg_latency_ms:
                ratio = report.average_execution_time_ms / self.target.max_avg_latency_ms
                latency_eval = f"Exceeds Target by {ratio:.2f}x"
                bottlenecks.append(f"Latensi rata-rata ({report.average_execution_time_ms:.4f} ms) melampaui batas target ({self.target.max_avg_latency_ms:.4f} ms).")
                actionable_feedback.append(
                    f"Optimalkan kompleksitas algoritma: waktu saat ini melampaui target sebesar {ratio:.2f}x."
                )
                latency_factor = max(0.0, 1.0 - (ratio - 1.0) * 0.5)
            else:
                latency_eval = f"Within Target ({report.average_execution_time_ms:.4f} ms <= {self.target.max_avg_latency_ms:.4f} ms)"

        # 3. Hitung Fitness Score (0 - 100)
        # 70% Bobot Kebenaran, 30% Bobot Efisiensi Latensi
        correctness_score = report.pass_rate * 70.0
        performance_score = latency_factor * 30.0
        fitness_score = max(0.0, min(100.0, correctness_score + performance_score))

        # 4. Tentukan Konvergensi
        is_converged = (report.pass_rate >= self.target.min_pass_rate)
        if self.target.max_avg_latency_ms is not None:
            is_converged = is_converged and (report.average_execution_time_ms <= self.target.max_avg_latency_ms)

        if is_converged:
            actionable_feedback.append("Seluruh kriteria target empiris telah terpenuhi. Solusi optimal.")

        return CritiqueReport(
            is_converged=is_converged,
            fitness_score=round(fitness_score, 2),
            correctness_grade=correctness_grade,
            latency_evaluation=latency_eval,
            actionable_feedback=actionable_feedback,
            identified_bottlenecks=bottlenecks,
        )
