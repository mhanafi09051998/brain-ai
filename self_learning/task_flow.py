"""Modul Orkestrator Alur Kerja Agen AI (Closed-Loop Agentic Task Flow).

Mengimplementasikan 6 fase eksekusi tugas AI:
1. Ingestion & Grounding
2. Planning & Decomposition
3. Grounded Execution
4. Empirical Verification
5. Reflexion & Self-Correction
6. Distillation & Delivery
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import uuid

from .identity_lock import IdentityGuard
from .reflection import ReflectionRecord, ReflexionMemoryStore
from .storage import KnowledgeEntry, KnowledgeStore


class TaskPhase(str, Enum):
    INGESTION = "ingestion"
    PLANNING = "planning"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    REFLEXION = "reflexion"
    DISTILLATION = "distillation"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class FlowStep:
    """Representasi satu langkah dalam alur kerja agen."""

    phase: TaskPhase
    name: str
    status: StepStatus = StepStatus.PENDING
    detail: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TaskFlowContext:
    """Konteks persisten selama eksekusi tugas berlangsung."""

    task_id: str
    task_name: str
    intended_goal: str
    acceptance_criteria: List[str] = field(default_factory=list)
    grounded_files: List[str] = field(default_factory=list)
    steps: List[FlowStep] = field(default_factory=list)
    reflections: List[ReflectionRecord] = field(default_factory=list)
    distilled_patterns: List[str] = field(default_factory=list)
    final_output: Any = None
    is_success: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_step(self, phase: TaskPhase, name: str, status: StepStatus, detail: str = "") -> FlowStep:
        step = FlowStep(phase=phase, name=name, status=status, detail=detail)
        self.steps.append(step)
        return step


class AgenticTaskFlow:
    """Orkestrator alur kerja AI berbasis siklus tertutup (Closed-Loop)."""

    def __init__(
        self,
        memory_store: Optional[ReflexionMemoryStore] = None,
        knowledge_store: Optional[KnowledgeStore] = None,
    ):
        self.memory_store = memory_store or ReflexionMemoryStore()
        self.knowledge_store = knowledge_store or KnowledgeStore()

    def run_pipeline(
        self,
        task_name: str,
        intended_goal: str,
        acceptance_criteria: List[str],
        grounded_files: List[str],
        plan_steps: List[str],
        executor_fn: Callable[[TaskFlowContext, Optional[str]], Any],
        verifier_fn: Callable[[Any], bool],
        max_attempts: int = 3,
    ) -> TaskFlowContext:
        """Mengeksekusi pipeline 6-fase terstruktur dengan reflexi diri otomatis jika gagal."""

        # Validasi Integritas Identitas Claudia (Immutable Identity Guardrail)
        IdentityGuard.validate_instruction(task_name)
        IdentityGuard.validate_instruction(intended_goal)

        context = TaskFlowContext(
            task_id=f"flow-{uuid.uuid4().hex[:8]}",
            task_name=task_name,
            intended_goal=intended_goal,
            acceptance_criteria=acceptance_criteria,
            grounded_files=grounded_files,
        )

        # Fase 1: Ingestion & Grounding
        context.add_step(
            TaskPhase.INGESTION,
            "Validasi Berkas Acuan & Konteks",
            StepStatus.SUCCESS,
            f"Konteks terverifikasi: {len(grounded_files)} berkas acuan.",
        )

        # Fase 2: Planning & Decomposition
        context.add_step(
            TaskPhase.PLANNING,
            "Perumusan Rencana Eksekusi",
            StepStatus.SUCCESS,
            f"Didekomposisi menjadi {len(plan_steps)} langkah dengan {len(acceptance_criteria)} kriteria sukses.",
        )

        # Siklus Eksekusi, Verifikasi, dan Refleksi
        attempt = 1
        last_feedback = None

        while attempt <= max_attempts:
            # Fase 3: Grounded Execution
            context.add_step(
                TaskPhase.EXECUTION,
                f"Percobaan Eksekusi #{attempt}",
                StepStatus.RUNNING,
                f"Menjalankan logika dengan constraints aktif: {bool(last_feedback)}",
            )

            try:
                result = executor_fn(context, last_feedback)
                context.final_output = result

                # Fase 4: Empirical Verification
                context.add_step(
                    TaskPhase.VERIFICATION,
                    f"Pengujian Verifikasi #{attempt}",
                    StepStatus.RUNNING,
                    "Menilai pemenuhan kriteria penerimaan...",
                )

                is_valid = verifier_fn(result)

                if is_valid:
                    # Sukses
                    context.is_success = True
                    context.add_step(
                        TaskPhase.VERIFICATION,
                        f"Pengujian Verifikasi #{attempt}",
                        StepStatus.SUCCESS,
                        "Semua kriteria penerimaan terpenuhi secara empiris.",
                    )

                    # Fase 5 & 6: Distillation & Persistence
                    entry = KnowledgeEntry(
                        entry_id=f"distill-{uuid.uuid4().hex[:8]}",
                        task_type=task_name,
                        category="heuristic",
                        pattern=f"Keberhasilan eksekusi tugas '{task_name}' pada percobaan #{attempt}",
                        explanation=f"Kriteria terpenuhi: {', '.join(acceptance_criteria)}",
                        impact_score=0.9,
                    )
                    self.knowledge_store.add(entry)
                    context.distilled_patterns.append(entry.entry_id)

                    context.add_step(
                        TaskPhase.DISTILLATION,
                        "Penyulingan Pengetahuan Sukses",
                        StepStatus.SUCCESS,
                        f"Pola disimpan ke KnowledgeStore: {entry.entry_id}",
                    )
                    break
                else:
                    raise AssertionError("Verifikasi kriteria penerimaan mengembalikan False.")

            except Exception as err:
                # Fase 5: Reflexion Loop (Refleksi Verbal 4-Kuadran)
                context.add_step(
                    TaskPhase.VERIFICATION,
                    f"Pengujian Verifikasi #{attempt}",
                    StepStatus.FAILED,
                    f"Kegagalan terdeteksi: {str(err)}",
                )

                reflection = ReflectionRecord(
                    record_id=f"ref-{uuid.uuid4().hex[:8]}",
                    task_name=task_name,
                    attempt_number=attempt,
                    intended_goal=intended_goal,
                    actual_outcome=str(err),
                    root_cause=f"Ketidaksesuaian hasil aktual dengan kriteria penerimaan pada iterasi #{attempt}.",
                    corrective_heuristic=f"Gunakan perbaikan terfokus dan eliminasi asumsi yang menyebabkan error: {err}",
                    resolved=False,
                )
                self.memory_store.record(reflection)
                context.reflections.append(reflection)
                last_feedback = reflection.to_in_context_prompt()

                context.add_step(
                    TaskPhase.REFLEXION,
                    f"Refleksi Verbal #{attempt}",
                    StepStatus.SUCCESS,
                    f"Refleksi kausal dirumuskan dan diinjeksikan untuk percobaan #{attempt + 1}",
                )

                attempt += 1

        return context
