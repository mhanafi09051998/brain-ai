"""Pengujian Unit untuk Framework Multi-Task Flow.
Memverifikasi validitas alur kerja terspesialisasi dan router domain.
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from self_learning.multi_task_flow import (
    DomainRole,
    DomainStage,
    FullStackTaskFlow,
    ResearchTaskFlow,
    SpatialXRTaskFlow,
    DocumentControllerTaskFlow,
    TaskFlowRouter,
)
from self_learning.task_flow import TaskFlowContext, StepStatus


class TestMultiTaskFlow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.router = TaskFlowRouter()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

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

        self.assertEqual(len(dynamic_flow.stages), 2)

        # Uji dynamic routing
        routed = self.router.route_by_task_description("Audit keamanan smart contract Solidity dan optimasi gas")
        self.assertEqual(routed.custom_role_name, "blockchain_engineer")
        self.assertEqual(len(routed.stages), 2)


if __name__ == "__main__":
    unittest.main()
