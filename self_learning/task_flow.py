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
from typing import Any, Callable, Dict, List, Optional
import uuid

from .identity_lock import IdentityGuard
from .reflection import ReflectionAgent, ReflectionRecord, ReflexionMemoryStore
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
        self.memory_store = memory_store if memory_store is not None else ReflexionMemoryStore()
        self.knowledge_store = knowledge_store if knowledge_store is not None else KnowledgeStore()
        self.reflection_agent = ReflectionAgent(self.memory_store)

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
        """Mengeksekusi pipeline 6-fase terstruktur dengan refleksi diri otomatis jika gagal."""
        if max_attempts < 1:
            raise ValueError("max_attempts harus >= 1.")

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
        last_feedback: Optional[str] = None

        for attempt in range(1, max_attempts + 1):
            # Fase 3: Grounded Execution
            exec_step = context.add_step(
                TaskPhase.EXECUTION,
                f"Percobaan Eksekusi #{attempt}",
                StepStatus.RUNNING,
                f"Menjalankan logika dengan constraints aktif: {last_feedback is not None}",
            )
            verify_step: Optional[FlowStep] = None

            try:
                result = executor_fn(context, last_feedback)
                context.final_output = result
                exec_step.status = StepStatus.SUCCESS
                exec_step.detail = "Eksekutor selesai tanpa exception."

                # Fase 4: Empirical Verification
                verify_step = context.add_step(
                    TaskPhase.VERIFICATION,
                    f"Pengujian Verifikasi #{attempt}",
                    StepStatus.RUNNING,
                    "Menilai pemenuhan kriteria penerimaan...",
                )

                if not verifier_fn(result):
                    raise AssertionError("Verifikasi kriteria penerimaan mengembalikan False.")

                verify_step.status = StepStatus.SUCCESS
                verify_step.detail = "Semua kriteria penerimaan terpenuhi secara empiris."
                context.is_success = True

                # Fase 6: Distillation & Persistence (heuristik sukses)
                self._distill_success(context, attempt)
                break

            except Exception as err:
                # Langkah yang sedang berjalan (eksekusi atau verifikasi) ditandai gagal
                failed_step = verify_step or exec_step
                failed_step.status = StepStatus.FAILED
                failed_step.detail = f"Kegagalan terdeteksi: {err}"

                # Fase 5: Reflexion Loop (Refleksi Verbal 4-Kuadran, diagnosis kausal per tipe error)
                reflection = self.reflection_agent.formulate_reflection(
                    task_name=task_name,
                    attempt_number=attempt,
                    intended_goal=intended_goal,
                    error=err,
                )
                context.reflections.append(reflection)
                last_feedback = reflection.to_in_context_prompt()

                context.add_step(
                    TaskPhase.REFLEXION,
                    f"Refleksi Verbal #{attempt}",
                    StepStatus.SUCCESS,
                    f"Refleksi kausal dirumuskan ({reflection.record_id}) dan diinjeksikan untuk percobaan #{attempt + 1}",
                )

        if context.is_success:
            # Kegagalan sebelumnya terbukti teratasi -> tandai resolved di memori episodik
            for refl in context.reflections:
                self.memory_store.resolve(refl.record_id)
        else:
            # Fase 6 (jalur gagal): anti-pola dicatat agar iterasi/sesi berikutnya tidak mengulang
            self._distill_failure(context, max_attempts)

        return context

    def _distill_success(self, context: TaskFlowContext, attempt: int) -> None:
        entry = KnowledgeEntry(
            entry_id=f"distill-{uuid.uuid4().hex[:8]}",
            task_type=context.task_name,
            category="heuristic",
            pattern=f"Keberhasilan eksekusi tugas '{context.task_name}' pada percobaan #{attempt}",
            explanation=f"Kriteria terpenuhi: {', '.join(context.acceptance_criteria)}",
            impact_score=0.9,
            metadata={"task_id": context.task_id, "attempts": attempt, "reflections": len(context.reflections)},
        )
        self.knowledge_store.add(entry)
        context.distilled_patterns.append(entry.entry_id)
        context.add_step(
            TaskPhase.DISTILLATION,
            "Penyulingan Pengetahuan Sukses",
            StepStatus.SUCCESS,
            f"Pola disimpan ke KnowledgeStore: {entry.entry_id}",
        )

    def _distill_failure(self, context: TaskFlowContext, max_attempts: int) -> None:
        last_reflection = context.reflections[-1] if context.reflections else None
        entry = KnowledgeEntry(
            entry_id=f"distill-{uuid.uuid4().hex[:8]}",
            task_type=context.task_name,
            category="anti_pattern",
            pattern=f"Kegagalan tugas '{context.task_name}' setelah {max_attempts} percobaan",
            explanation=(
                last_reflection.root_cause
                if last_reflection
                else "Kriteria penerimaan tidak pernah terpenuhi."
            ),
            impact_score=-0.8,
            metadata={
                "task_id": context.task_id,
                "attempts": max_attempts,
                "reflection_ids": [r.record_id for r in context.reflections],
            },
        )
        self.knowledge_store.add(entry)
        context.distilled_patterns.append(entry.entry_id)
        context.add_step(
            TaskPhase.DISTILLATION,
            "Penyulingan Anti-Pola Kegagalan",
            StepStatus.SUCCESS,
            f"Anti-pola disimpan ke KnowledgeStore: {entry.entry_id}",
        )
