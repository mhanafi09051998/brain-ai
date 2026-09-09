"""Framework Multi-Task Flow untuk AI Agent Claudia.

Menyediakan orkestrasi alur kerja terspesialisasi per disiplin keahlian (Domain-Specific Task Flows):
1. FullStackTaskFlow: Schema -> Backend/API -> Frontend/UI -> Integration Test -> Production Build
2. ResearchTaskFlow: Scope Definition -> Broad Discovery -> Deep Ingestion -> Triangulation -> Grounded Findings
3. SpatialXRTaskFlow: Coordinate Budget -> Scene Graph -> 6DoF Mapping -> Frame-Rate Audit -> XR Handshake
4. DocumentControllerTaskFlow: Ingestion -> MDR Indexing -> RACI Review -> Revision Audit -> Controlled Release
5. TaskFlowRouter: Router otomatis penentu alur kerja berdasarkan jenis tugas/skill.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import uuid

from .reflection import ReflectionRecord, ReflexionMemoryStore
from .storage import KnowledgeEntry, KnowledgeStore
from .task_flow import FlowStep, StepStatus, TaskFlowContext, TaskPhase


class DomainRole(str, Enum):
    """Domain peran dan spesialisasi keahlian."""
    FULLSTACK = "fullstack_engineer"
    RESEARCHER = "codebase_researcher"
    SPATIAL_XR = "spatial_xr_developer"
    DOCUMENT_CONTROLLER = "document_controller"
    OPTIMIZER = "performance_optimizer"


@dataclass
class DomainStage:
    """Tahapan spesifik dalam domain task flow."""
    stage_id: str
    name: str
    description: str
    required_artifacts: List[str] = field(default_factory=list)
    verification_check: str = ""


class BaseSpecializedTaskFlow(ABC):
    """Kelas dasar abstrak untuk alur kerja terspesialisasi."""

    def __init__(
        self,
        domain_role: DomainRole,
        memory_store: Optional[ReflexionMemoryStore] = None,
        knowledge_store: Optional[KnowledgeStore] = None,
    ):
        self.domain_role = domain_role
        self.memory_store = memory_store or ReflexionMemoryStore()
        self.knowledge_store = knowledge_store or KnowledgeStore()
        self.stages: List[DomainStage] = self._define_stages()

    @abstractmethod
    def _define_stages(self) -> List[DomainStage]:
        """Mendefinisikan tahapan-tahapan khusus domain."""
        pass

    def execute_stage(
        self,
        context: TaskFlowContext,
        stage: DomainStage,
        action_fn: Callable[[TaskFlowContext], Any],
        verify_fn: Optional[Callable[[Any], bool]] = None,
    ) -> bool:
        """Mengeksekusi satu tahapan domain secara tertutup."""
        step = context.add_step(
            phase=TaskPhase.EXECUTION,
            name=f"[{self.domain_role.value.upper()}] {stage.name}",
            status=StepStatus.RUNNING,
            detail=stage.description
        )

        try:
            result = action_fn(context)
            if verify_fn:
                is_valid = verify_fn(result)
                if not is_valid:
                    step.status = StepStatus.FAILED
                    step.detail = f"Verifikasi gagal pada tahapan: {stage.name}"
                    return False

            step.status = StepStatus.SUCCESS
            step.detail = f"Tahapan '{stage.name}' selesai dan terverifikasi."
            return True
        except Exception as e:
            step.status = StepStatus.FAILED
            step.detail = f"Kesalahan saat mengeksekusi tahapan: {str(e)}"
            return False


class FullStackTaskFlow(BaseSpecializedTaskFlow):
    """Alur kerja khusus Full-Stack Engineer.
    
    Fokus: Kontrak API, skema DB, rendering state, pengujian terotomasi, zero lint error.
    """

    def __init__(self, memory_store=None, knowledge_store=None):
        super().__init__(DomainRole.FULLSTACK, memory_store, knowledge_store)

    def _define_stages(self) -> List[DomainStage]:
        return [
            DomainStage(
                stage_id="schema_grounding",
                name="Schema & Model Grounding",
                description="Validasi relasi entitas basis data, migrasi, dan type definition.",
                required_artifacts=["database_schema", "entity_models"],
                verification_check="Database migration / schema check lolos."
            ),
            DomainStage(
                stage_id="api_contract",
                name="API Contract & Controller Logic",
                description="Perancangan endpoint REST/tRPC/GraphQL dan validasi request/response.",
                required_artifacts=["controller", "route_definition", "validation_schema"],
                verification_check="HTTP status code & JSON structure lolos."
            ),
            DomainStage(
                stage_id="ui_state_binding",
                name="Frontend UI & State Binding",
                description="Implementasi komponen UI responsif, penanganan loading/error state.",
                required_artifacts=["ui_components", "state_management"],
                verification_check="Zero DOM error & UI renders as specified."
            ),
            DomainStage(
                stage_id="automated_testing",
                name="Automated Test Verification",
                description="Eksekusi unit test, feature test, dan regression guard di terminal.",
                required_artifacts=["test_suites"],
                verification_check="100% test suites passing (0 fail, 0 regression)."
            ),
            DomainStage(
                stage_id="build_verification",
                name="Production Build & Asset Optimization",
                description="Verifikasi kompilasi bundel produksi (Vite/Webpack/Next.js/Artisan).",
                required_artifacts=["build_dist"],
                verification_check="Build exit code 0 tanpa chunk warning kritis."
            )
        ]


class ResearchTaskFlow(BaseSpecializedTaskFlow):
    """Alur kerja khusus Codebase & Technical Researcher.
    
    Fokus: Scope pembatasan, penemuan repo/berkas, triangulasi sumber, fakta bebas halusinasi.
    """

    def __init__(self, memory_store=None, knowledge_store=None):
        super().__init__(DomainRole.RESEARCHER, memory_store, knowledge_store)

    def _define_stages(self) -> List[DomainStage]:
        return [
            DomainStage(
                stage_id="inquiry_framing",
                name="Inquiry Scope & Framing",
                description="Mendefinisikan batasan investigasi, hipotesis awal, dan kriteria bukti.",
                required_artifacts=["inquiry_brief"],
                verification_check="Parameter pertanyaan jelas dan terukur."
            ),
            DomainStage(
                stage_id="broad_discovery",
                name="Broad Discovery & File Scanning",
                description="Pemindaian luas direktori, dependensi, manifest, dan struktur relasi modul.",
                required_artifacts=["discovery_manifest"],
                verification_check="Seluruh file relevan terpetakan tanpa missing references."
            ),
            DomainStage(
                stage_id="deep_grounding",
                name="Deep Textual & Logic Grounding",
                description="Pembacaan mendalam baris kode aktual, signature fungsi, dan implementasi riil.",
                required_artifacts=["code_snippets", "logic_diagrams"],
                verification_check="Seluruh klaim merujuk langsung ke file:/// dan baris nyata di disk."
            ),
            DomainStage(
                stage_id="cross_triangulation",
                name="Cross-Reference & Triangulation",
                description="Memvalidasi konsistensi antara dokumentasi, kode aktual, dan pengujian empiris.",
                required_artifacts=["gap_analysis"],
                verification_check="Nol kontradiksi antara dokumen acuan dan perilaku nyata kode."
            ),
            DomainStage(
                stage_id="synthesis_delivery",
                name="Fact Extraction & Concise Delivery",
                description="Penyusunan laporan temuan berdensitas tinggi, tabel perbandingan, dan rekomendasi.",
                required_artifacts=["research_report"],
                verification_check="Rasio sinyal-ke-kebisingan maksimal, bebas asumsi/halusinasi."
            )
        ]


class SpatialXRTaskFlow(BaseSpecializedTaskFlow):
    """Alur kerja khusus Spatial Computing & WebXR (AR/VR) Engineer.
    
    Fokus: Budget koordinat, scene-graph hierarchy, input 6DoF/haptics, frame-rate 90 FPS.
    """

    def __init__(self, memory_store=None, knowledge_store=None):
        super().__init__(DomainRole.SPATIAL_XR, memory_store, knowledge_store)

    def _define_stages(self) -> List[DomainStage]:
        return [
            DomainStage(
                stage_id="spatial_budget",
                name="Spatial Budget & Coordinate Setup",
                description="Penetapan skala metrik dunia nyata (1 unit = 1 meter), origin kamera, dan pencahayaan.",
                required_artifacts=["camera_rig", "lighting_setup"],
                verification_check="Eye-level standing height (1.6m) dan batas frustum terkonfigurasi."
            ),
            DomainStage(
                stage_id="scene_hierarchy",
                name="Scene Graph & Environment Hierarchy",
                description="Penyusunan geometri, material shader, lantai teleportasi, dan latar atmosfer.",
                required_artifacts=["environment_mesh", "teleport_floor"],
                verification_check="Batasan poligon di bawah budget mobile XR (Quest target)."
            ),
            DomainStage(
                stage_id="xr_input_mapping",
                name="6DoF Controller & Interaction Mapping",
                description="Integrasi laser pointer, reticle, haptic actuators, dan locomotion teleportasi.",
                required_artifacts=["controller_manager", "raycaster_pipeline"],
                verification_check="Handshake controller 0 dan 1 merespons trigger/grip event."
            ),
            DomainStage(
                stage_id="spatial_ui_audio",
                name="Spatial UI & Procedural Audio",
                description="Floating 3D canvas console interaktif dan audio spasial Web Audio API.",
                required_artifacts=["spatial_panel", "audio_synthesizer"],
                verification_check="UV raycast detection tepat sasaran dan audio latency < 10ms."
            ),
            DomainStage(
                stage_id="frametime_audit",
                name="Frame-Rate Audit & Device Handshake",
                description="Pengujian performa stabil pada target 90 FPS untuk mencegah motion sickness.",
                required_artifacts=["performance_profile"],
                verification_check="Draw calls teroptimasi dan WebXR sessionstart/sessionend stabil."
            )
        ]


class DocumentControllerTaskFlow(BaseSpecializedTaskFlow):
    """Alur kerja khusus Document Controller (ISO 9001:2015 Klausul 7.5).
    
    Fokus: Kodifikasi unik, master register (MDR), kontrol revisi, audit trail, otorisasi.
    """

    def __init__(self, memory_store=None, knowledge_store=None):
        super().__init__(DomainRole.DOCUMENT_CONTROLLER, memory_store, knowledge_store)

    def _define_stages(self) -> List[DomainStage]:
        return [
            DomainStage(
                stage_id="codification",
                name="Identification & Codification",
                description="Pemberian nomor registrasi dokumen unik, penamaan direktori eksplisit (Klausul 7.5.2).",
                required_artifacts=["document_number", "directory_path"],
                verification_check="Nomor dokumen dan nama direktori unik serta bebas ambiguitas."
            ),
            DomainStage(
                stage_id="mdr_registration",
                name="Master Document Register (MDR) Indexing",
                description="Pencatatan metadata (Judul, Disiplin, Pemilik Dokumen, Klasifikasi) ke master register.",
                required_artifacts=["mdr_entry"],
                verification_check="Metadata tercatat lengkap dalam tabel register persisten."
            ),
            DomainStage(
                stage_id="review_authorization",
                name="Review & Authorization Check (RACI)",
                description="Verifikasi pemenuhan review teknis, kepatuhan format, dan otorisasi persetujuan.",
                required_artifacts=["approval_log"],
                verification_check="Status persetujuan jelas (Draft, Under Review, Approved)."
            ),
            DomainStage(
                stage_id="revision_audit",
                name="Revision Control & Change Log Audit",
                description="Pengelolaan nomor revisi (Rev 0, Rev A), ringkasan riwayat perubahan komprehensif.",
                required_artifacts=["revision_history"],
                verification_check="Riwayat revisi terdokumentasi dan versi kadaluarsa diarsipkan/ditandai."
            ),
            DomainStage(
                stage_id="controlled_distribution",
                name="Controlled Distribution & Cross-Reference Sync",
                description="Penyelarasan referensi silang ke seluruh dokumen induk (README.md, memory.md).",
                required_artifacts=["distribution_log"],
                verification_check="Seluruh tautan berkas lokal (file:///) valid dan dapat diakses."
            )
        ]


class DynamicTaskFlow(BaseSpecializedTaskFlow):
    """Alur kerja yang disintesis secara dinamis untuk domain baru."""

    def __init__(
        self,
        custom_role_name: str,
        custom_stages: List[DomainStage],
        memory_store: Optional[ReflexionMemoryStore] = None,
        knowledge_store: Optional[KnowledgeStore] = None,
    ):
        self.custom_role_name = custom_role_name
        self._custom_stages = custom_stages
        # Inisialisasi tanpa enum kaku
        super().__init__(DomainRole.FULLSTACK, memory_store, knowledge_store)
        self.stages = custom_stages

    def _define_stages(self) -> List[DomainStage]:
        return getattr(self, "_custom_stages", [])


class TaskFlowRouter:
    """Router cerdas untuk memilih, menginisialisasi, dan mensintesis Task Flow yang tepat."""

    def __init__(
        self,
        memory_store: Optional[ReflexionMemoryStore] = None,
        knowledge_store: Optional[KnowledgeStore] = None
    ):
        self.memory_store = memory_store or ReflexionMemoryStore()
        self.knowledge_store = knowledge_store or KnowledgeStore()

        self.flows: Dict[str, BaseSpecializedTaskFlow] = {
            DomainRole.FULLSTACK.value: FullStackTaskFlow(self.memory_store, self.knowledge_store),
            DomainRole.RESEARCHER.value: ResearchTaskFlow(self.memory_store, self.knowledge_store),
            DomainRole.SPATIAL_XR.value: SpatialXRTaskFlow(self.memory_store, self.knowledge_store),
            DomainRole.DOCUMENT_CONTROLLER.value: DocumentControllerTaskFlow(self.memory_store, self.knowledge_store),
        }
        self.custom_routing_rules: List[Dict[str, Any]] = []

    def get_flow(self, role: DomainRole | str) -> BaseSpecializedTaskFlow:
        """Mengambil instance flow berdasarkan peran domain."""
        key = role.value if isinstance(role, DomainRole) else str(role)
        if key not in self.flows:
            raise ValueError(f"Domain role '{key}' tidak terdaftar dalam Multi-Task Flow Router.")
        return self.flows[key]

    def register_custom_flow(
        self,
        role_name: str,
        stages: List[DomainStage],
        keywords: Optional[List[str]] = None
    ) -> DynamicTaskFlow:
        """Mendaftarkan alur kerja baru secara dinamis saat ada keahlian/domain baru."""
        flow = DynamicTaskFlow(
            custom_role_name=role_name,
            custom_stages=stages,
            memory_store=self.memory_store,
            knowledge_store=self.knowledge_store
        )
        self.flows[role_name] = flow

        if keywords:
            self.custom_routing_rules.append({
                "role_name": role_name,
                "keywords": [k.lower() for k in keywords]
            })

        # Persistensikan pengetahuan alur baru ke knowledge store
        self.knowledge_store.add(KnowledgeEntry(
            entry_id=f"dynflow-{uuid.uuid4().hex[:8]}",
            task_type="dynamic_task_flow",
            category="heuristic",
            pattern=f"Pipeline {role_name} ({len(stages)} stages)",
            explanation=f"Alur kerja dinamis terspesialisasi untuk domain {role_name}.",
            impact_score=1.0,
            metadata={"keywords": keywords or [], "stages": [s.stage_id for s in stages]}
        ))

        return flow

    def route_by_task_description(self, description: str) -> BaseSpecializedTaskFlow:
        """Menganalisis deskripsi tugas dan memilih flow yang paling tepat secara otomatis."""
        text = description.lower()

        # 1. Cek aturan kustom dinamis terlebih dahulu
        for rule in self.custom_routing_rules:
            if any(k in text for k in rule["keywords"]):
                return self.flows[rule["role_name"]]

        # 2. XR / 3D Keywords
        if any(k in text for k in ["ar/vr", "webxr", "three.js", "threejs", "a-frame", "spatial", "quest", "3d", "teleport"]):
            return self.flows[DomainRole.SPATIAL_XR.value]

        # 3. Document Control Keywords
        if any(k in text for k in ["document control", "iso 9001", "mdr", "transmittal", "revisi", "klausul 7.5", "pengendali dokumen"]):
            return self.flows[DomainRole.DOCUMENT_CONTROLLER.value]

        # 4. Research Keywords
        if any(k in text for k in ["riset", "analisis", "research", "bedah kode", "investigasi", "bandingkan", "survey"]):
            return self.flows[DomainRole.RESEARCHER.value]

        # 5. Default to FullStack
        return self.flows[DomainRole.FULLSTACK.value]

