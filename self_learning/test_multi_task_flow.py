"""Pengujian Unit untuk Framework Multi-Task Flow.
Memverifikasi validitas alur kerja terspesialisasi dan router domain.
"""

import unittest
from pathlib import Path
import tempfile

from self_learning.multi_task_flow import (
    DomainRole,
    DomainStage,
    DynamicTaskFlow,
    FullStackTaskFlow,
    ResearchTaskFlow,
    SpatialXRTaskFlow,
    DocumentControllerTaskFlow,
    TaskFlowRouter,
    contains_keyword,
)
from self_learning.reflection import ReflexionMemoryStore
from self_learning.storage import KnowledgeStore
from self_learning.task_flow import TaskFlowContext, StepStatus


class TestMultiTaskFlow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)
        self.memory_store = ReflexionMemoryStore(base / "reflections.json")
        self.knowledge_store = KnowledgeStore(base / "knowledge.json")
        self.router = TaskFlowRouter(self.memory_store, self.knowledge_store)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_fullstack_stages(self):
        flow = self.router.get_flow(DomainRole.FULLSTACK)
        self.assertIsInstance(flow, FullStackTaskFlow)
        self.assertEqual(len(flow.stages), 5)
        stage_ids = [s.stage_id for s in flow.stages]
        self.assertIn("schema_grounding", stage_ids)
        self.assertIn("api_contract", stage_ids)
        self.assertIn("ui_state_binding", stage_ids)
        self.assertIn("automated_testing", stage_ids)
        self.assertIn("build_verification", stage_ids)

    def test_research_stages(self):
        flow = self.router.get_flow(DomainRole.RESEARCHER)
        self.assertIsInstance(flow, ResearchTaskFlow)
        self.assertEqual(len(flow.stages), 5)
        stage_ids = [s.stage_id for s in flow.stages]
        self.assertIn("inquiry_framing", stage_ids)
        self.assertIn("broad_discovery", stage_ids)
        self.assertIn("deep_grounding", stage_ids)
        self.assertIn("cross_triangulation", stage_ids)
        self.assertIn("synthesis_delivery", stage_ids)

    def test_spatial_xr_stages(self):
        flow = self.router.get_flow(DomainRole.SPATIAL_XR)
        self.assertIsInstance(flow, SpatialXRTaskFlow)
        self.assertEqual(len(flow.stages), 5)
        stage_ids = [s.stage_id for s in flow.stages]
        self.assertIn("spatial_budget", stage_ids)
        self.assertIn("scene_hierarchy", stage_ids)
        self.assertIn("xr_input_mapping", stage_ids)
        self.assertIn("spatial_ui_audio", stage_ids)
        self.assertIn("frametime_audit", stage_ids)

    def test_document_controller_stages(self):
        flow = self.router.get_flow(DomainRole.DOCUMENT_CONTROLLER)
        self.assertIsInstance(flow, DocumentControllerTaskFlow)
        self.assertEqual(len(flow.stages), 5)
        stage_ids = [s.stage_id for s in flow.stages]
        self.assertIn("codification", stage_ids)
        self.assertIn("mdr_registration", stage_ids)
        self.assertIn("review_authorization", stage_ids)
        self.assertIn("revision_audit", stage_ids)
        self.assertIn("controlled_distribution", stage_ids)

    def test_get_flow_and_get_stage_errors(self):
        self.assertIsInstance(self.router.get_flow("fullstack_engineer"), FullStackTaskFlow)
        with self.assertRaises(ValueError):
            self.router.get_flow("unknown_role")
        flow = self.router.get_flow(DomainRole.FULLSTACK)
        self.assertEqual(flow.get_stage("api_contract").name, "API Contract & Controller Logic")
        with self.assertRaises(ValueError):
            flow.get_stage("nope")

    def test_routing_by_description(self):
        # 1. XR query
        xr_flow = self.router.route_by_task_description("Buatkan adegan 3D interaktif WebXR dengan Three.js dan teleportasi Meta Quest")
        self.assertIsInstance(xr_flow, SpatialXRTaskFlow)

        # 2. Document Control query
        doc_flow = self.router.route_by_task_description("Kelola nomor revisi dan master document register ISO 9001")
        self.assertIsInstance(doc_flow, DocumentControllerTaskFlow)

        # 3. Research query
        research_flow = self.router.route_by_task_description("Lakukan riset mendalam dan analisis perbandingan arsitektur backend")
        self.assertIsInstance(research_flow, ResearchTaskFlow)

        # 4. Fullstack query (default)
        fullstack_flow = self.router.route_by_task_description("Buat REST API dan dashboard admin dengan Laravel dan React")
        self.assertIsInstance(fullstack_flow, FullStackTaskFlow)

    def test_keyword_matching_uses_word_boundaries(self):
        """Kata kunci dicocokkan sebagai token utuh agar tidak salah routing karena substring."""
        self.assertTrue(contains_keyword("Adegan 3D untuk Quest", ("3d",)))
        self.assertFalse(contains_keyword("Gunakan id3d sebagai kunci", ("3d",)))
        self.assertTrue(contains_keyword("Update entri MDR proyek", ("mdr",)))
        self.assertFalse(contains_keyword("Perbaiki admdr.py", ("mdr",)))
        self.assertTrue(contains_keyword("Integrasi three.js di halaman", ("three.js",)))
        # "admdr" tidak boleh mengarahkan ke Document Controller
        self.assertIsInstance(self.router.route_by_task_description("Refactor modul admdr untuk API"), FullStackTaskFlow)

    def test_stage_execution_success(self):
        flow = self.router.get_flow(DomainRole.FULLSTACK)
        ctx = TaskFlowContext(
            task_id="test-1",
            task_name="Test Fullstack",
            intended_goal="Build API"
        )

        stage = flow.stages[0]
        success = flow.execute_stage(
            context=ctx,
            stage=stage,
            action_fn=lambda c: {"schema": "ok"},
            verify_fn=lambda res: res.get("schema") == "ok"
        )

        self.assertTrue(success)
        self.assertEqual(len(ctx.steps), 1)
        self.assertEqual(ctx.steps[0].status, StepStatus.SUCCESS)
        self.assertTrue(ctx.steps[0].name.startswith("[FULLSTACK_ENGINEER]"))

    def test_stage_execution_failure(self):
        flow = self.router.get_flow(DomainRole.FULLSTACK)
        ctx = TaskFlowContext(
            task_id="test-2",
            task_name="Test Fullstack Fail",
            intended_goal="Build API"
        )

        stage = flow.stages[0]
        success = flow.execute_stage(
            context=ctx,
            stage=stage,
            action_fn=lambda c: {"schema": "corrupt"},
            verify_fn=lambda res: res.get("schema") == "ok"
        )

        self.assertFalse(success)
        self.assertEqual(len(ctx.steps), 1)
        self.assertEqual(ctx.steps[0].status, StepStatus.FAILED)

    def test_stage_execution_exception_is_captured(self):
        flow = self.router.get_flow(DomainRole.RESEARCHER)
        ctx = TaskFlowContext(task_id="test-3", task_name="Boom", intended_goal="x")

        def explode(c):
            raise RuntimeError("meledak")

        self.assertFalse(flow.execute_stage(ctx, flow.stages[0], explode))
        self.assertEqual(ctx.steps[0].status, StepStatus.FAILED)
        self.assertIn("meledak", ctx.steps[0].detail)

    def test_dynamic_task_flow_registration(self):
        # Mendaftarkan alur kerja baru (misal: Blockchain Smart Contract)
        blockchain_stages = [
            DomainStage("audit", "Formal Security Audit", "Verifikasi vulnerability reentrancy"),
            DomainStage("gas_opt", "Gas Optimization", "Pengecekan byte-code execution cost"),
        ]

        dynamic_flow = self.router.register_custom_flow(
            role_name="blockchain_engineer",
            stages=blockchain_stages,
            keywords=["solidity", "smart contract", "web3", "evm"]
        )

        self.assertIsInstance(dynamic_flow, DynamicTaskFlow)
        self.assertEqual(len(dynamic_flow.stages), 2)
        self.assertEqual(dynamic_flow.role_label, "blockchain_engineer")

        # Uji dynamic routing
        routed = self.router.route_by_task_description("Audit keamanan smart contract Solidity dan optimasi gas")
        self.assertEqual(routed.custom_role_name, "blockchain_engineer")
        self.assertEqual(len(routed.stages), 2)
        self.assertIs(self.router.get_flow("blockchain_engineer"), routed)

        # Label langkah memakai peran kustom, bukan FULLSTACK_ENGINEER
        ctx = TaskFlowContext(task_id="dyn", task_name="Audit", intended_goal="Aman")
        routed.execute_stage(ctx, routed.stages[0], lambda c: True)
        self.assertTrue(ctx.steps[0].name.startswith("[BLOCKCHAIN_ENGINEER]"))

    def test_dynamic_registration_is_idempotent(self):
        """Registrasi ulang peran yang sama memperbarui entri, tidak menumpuk duplikat."""
        stages = [DomainStage("s1", "Stage 1", "desc")]
        for _ in range(3):
            self.router.register_custom_flow("ml_engineer", stages, keywords=["training"])

        entries = self.knowledge_store.get_by_task("dynamic_task_flow")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].entry_id, "dynflow-ml_engineer")
        self.assertEqual(len(self.router.custom_routing_rules), 1)

        # Registrasi ulang dengan tahapan baru menggantikan flow lama
        self.router.register_custom_flow("ml_engineer", stages + [DomainStage("s2", "Stage 2", "d")], keywords=["training"])
        self.assertEqual(len(self.router.get_flow("ml_engineer").stages), 2)
        self.assertEqual(self.knowledge_store.get("dynflow-ml_engineer").metadata["stages"], ["s1", "s2"])

    def test_dynamic_task_flow_validation(self):
        with self.assertRaises(ValueError):
            DynamicTaskFlow("", [DomainStage("s", "S", "d")], self.memory_store, self.knowledge_store)
        with self.assertRaises(ValueError):
            DynamicTaskFlow("role", [], self.memory_store, self.knowledge_store)


if __name__ == "__main__":
    unittest.main()
