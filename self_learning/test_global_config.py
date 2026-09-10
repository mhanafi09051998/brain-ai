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
        self.assertEqual(projects[0].name, "Project Alpha")
        self.assertEqual(projects[0].location, "C:/Workspace/Alpha")
        self.assertEqual(projects[0].status, "Active")
        self.assertEqual(projects[1].name, "Project Beta")

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


if __name__ == "__main__":
    unittest.main()
