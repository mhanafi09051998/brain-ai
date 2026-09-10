"""Unit test untuk modul manajemen konfigurasi global dan jembatan lintas workspace."""

from pathlib import Path
import tempfile
import unittest
from self_learning.global_config import (
    GlobalConfigManager,
    ProjectEntry,
    WorkspaceBridge,
)


class TestGlobalConfig(unittest.TestCase):
    """Pengujian parsing, registrasi, dan resolusi path lintas workspace."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.mock_memory = self.temp_path / "memory.md"

        sample_content = (
            "# Global Persistent Memory\n\n"
            "## 1. Register Proyek & Status Lintas Workspace\n\n"
            "| Nama Proyek | Lokasi Direktori | Status Teknis | Catatan Kunci / Arsitektur |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **Project Alpha** | `C:/Workspace/Alpha` | Active | Alpha notes |\n"
            "| **Project Beta** | `C:/Workspace/Beta` | Staging | Beta notes |\n\n"
            "---\n"
        )
        self.mock_memory.write_text(sample_content, encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_registered_projects(self):
        """Memastikan parsing tabel proyek di memory.md menghasilkan objek ProjectEntry."""
        projects = GlobalConfigManager.parse_registered_projects(self.mock_memory)
        self.assertEqual(len(projects), 2)
        self.assertIsInstance(projects[0], ProjectEntry)
        self.assertEqual(projects[0].name, "Project Alpha")
        self.assertEqual(projects[0].location, "C:/Workspace/Alpha")
        self.assertEqual(projects[0].status, "Active")
        self.assertEqual(projects[1].name, "Project Beta")

    def test_parse_ignores_other_tables_and_missing_file(self):
        """Tabel lain (misal riwayat sesi) tidak ikut terbaca; berkas hilang -> daftar kosong."""
        content = (
            "# Memory\n\n"
            "## 4. Riwayat Sesi\n"
            "| Tanggal | Aktivitas | Status |\n| :--- | :--- | :--- |\n| 2026-01-01 | Sesuatu | Selesai |\n\n"
            "## 5. Register Proyek\n"
            "| Nama Proyek | Lokasi Direktori | Status Teknis | Catatan Kunci / Arsitektur |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **Gamma** | `C:/G` | Active | n |\n\n"
            "## 6. Lainnya\n"
            "| A | B | C | D |\n| :--- | :--- | :--- | :--- |\n| bukan | proyek | x | y |\n"
        )
        self.mock_memory.write_text(content, encoding="utf-8")
        projects = GlobalConfigManager.parse_registered_projects(self.mock_memory)
        self.assertEqual([p.name for p in projects], ["Gamma"])
        self.assertEqual(GlobalConfigManager.parse_registered_projects(self.temp_path / "nope.md"), [])

    def test_register_new_project(self):
        """Memastikan proyek baru dapat didaftarkan ke tabel memory.md."""
        success = GlobalConfigManager.register_or_update_project(
            name="Project Gamma",
            location="C:/Workspace/Gamma",
            status="Planning",
            notes="Gamma notes",
            memory_path=self.mock_memory
        )
        self.assertTrue(success)

        projects = GlobalConfigManager.parse_registered_projects(self.mock_memory)
        self.assertEqual(len(projects), 3)
        self.assertTrue(any(p.name == "Project Gamma" for p in projects))

    def test_update_existing_project(self):
        """Memastikan proyek yang sudah ada dapat diperbarui statusnya tanpa duplikasi baris."""
        success = GlobalConfigManager.register_or_update_project(
            name="Project Alpha",
            location="C:/Workspace/Alpha_V2",
            status="Production",
            notes="Updated notes",
            memory_path=self.mock_memory
        )
        self.assertTrue(success)

        projects = GlobalConfigManager.parse_registered_projects(self.mock_memory)
        self.assertEqual(len(projects), 2)  # Tidak boleh bertambah, hanya di-update
        alpha = next(p for p in projects if p.name == "Project Alpha")
        self.assertEqual(alpha.location, "C:/Workspace/Alpha_V2")
        self.assertEqual(alpha.status, "Production")

    def test_register_inserts_into_register_table_not_first_table(self):
        """Baris baru wajib masuk ke tabel Register Proyek meskipun ada tabel lain sebelumnya."""
        content = (
            "# Memory\n\n"
            "## 4. Riwayat Sesi\n"
            "| Tanggal | Aktivitas | Status |\n| :--- | :--- | :--- |\n| 2026-01-01 | Sesuatu | Selesai |\n\n"
            "## 5. Register Proyek\n"
            "| Nama Proyek | Lokasi Direktori | Status Teknis | Catatan Kunci / Arsitektur |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **Gamma** | `C:/G` | Active | n |\n"
        )
        self.mock_memory.write_text(content, encoding="utf-8")
        GlobalConfigManager.register_or_update_project("Delta", "C:/D", "New", "d", memory_path=self.mock_memory)

        text = self.mock_memory.read_text(encoding="utf-8")
        session_section = text.split("## 5. Register Proyek")[0]
        self.assertNotIn("Delta", session_section)
        self.assertEqual([p.name for p in GlobalConfigManager.parse_registered_projects(self.mock_memory)], ["Delta", "Gamma"])

    def test_register_creates_section_when_absent_and_file_when_missing(self):
        """Tanpa bagian register -> bagian baru dibuat; tanpa berkas -> ledger baru dibuat."""
        self.mock_memory.write_text("# Memory\n\nCatatan bebas.\n", encoding="utf-8")
        GlobalConfigManager.register_or_update_project("Solo", "C:/S", "Active", "n", memory_path=self.mock_memory)
        self.assertEqual([p.name for p in GlobalConfigManager.parse_registered_projects(self.mock_memory)], ["Solo"])
        self.assertIn("Catatan bebas.", self.mock_memory.read_text(encoding="utf-8"))

        fresh = self.temp_path / "nested" / "memory.md"
        GlobalConfigManager.register_or_update_project("Fresh", "C:/F", "Active", "n", memory_path=fresh)
        self.assertEqual([p.name for p in GlobalConfigManager.parse_registered_projects(fresh)], ["Fresh"])

        with self.assertRaises(ValueError):
            GlobalConfigManager.register_or_update_project("  ", "C:/X", "s", "n", memory_path=fresh)

    def test_workspace_bridge_resolve_path(self):
        """Memastikan resolusi path absolut dan relatif bekerja konsisten."""
        # Path absolut
        abs_path = Path("C:/Tools/app.py")
        resolved = WorkspaceBridge.resolve_workspace_path("C:/Tools/app.py")
        self.assertEqual(resolved, abs_path)

        # Path relatif
        base = self.temp_path
        resolved_rel = WorkspaceBridge.resolve_workspace_path("sub/file.txt", base_dir=base)
        self.assertEqual(resolved_rel, (base / "sub" / "file.txt").resolve())

    def test_workspace_bridge_cross_context(self):
        """Pencarian konteks proyek lain dari ledger (pencocokan nama parsial) beserta cek keberadaan di disk."""
        existing_dir = self.temp_path / "AlphaDir"
        existing_dir.mkdir()
        GlobalConfigManager.register_or_update_project(
            "Project Alpha", str(existing_dir), "Active", "n", memory_path=self.mock_memory
        )
        ctx = WorkspaceBridge.get_cross_workspace_context("alpha", memory_path=self.mock_memory)
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["name"], "Project Alpha")
        self.assertTrue(ctx["exists_on_disk"])

        beta = WorkspaceBridge.get_cross_workspace_context("beta", memory_path=self.mock_memory)
        self.assertFalse(beta["exists_on_disk"])
        self.assertIsNone(WorkspaceBridge.get_cross_workspace_context("omega", memory_path=self.mock_memory))


if __name__ == "__main__":
    unittest.main()
