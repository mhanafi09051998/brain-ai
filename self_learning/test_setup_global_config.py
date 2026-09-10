"""Unit test untuk installer konfigurasi global (setup_global_config.py).
Seluruh operasi diarahkan ke home direktori sementara; home pengguna asli tidak disentuh."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import setup_global_config as installer


class TestSetupGlobalConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.home = Path(self.temp_dir.name) / "home"
        self.home.mkdir()
        self.repo_dir = Path(installer.__file__).resolve().parent

    def tearDown(self):
        self.temp_dir.cleanup()

    def _run(self, fn, *args, **kwargs):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = fn(*args, **kwargs)
        return result, buf.getvalue()

    def test_get_paths_uses_override_home(self):
        paths = installer.get_paths(self.home)
        self.assertEqual(paths["home"], self.home)
        self.assertEqual(paths["config_dir"], self.home / ".gemini" / "config")
        self.assertEqual(paths["memory_file"], self.home / "memory.md")
        self.assertEqual(paths["repo_dir"], self.repo_dir)
        self.assertTrue(paths["repo_skills"].is_dir())

    def test_dry_run_writes_nothing(self):
        _, out = self._run(installer.install_global, dry_run=True, home=self.home)
        self.assertIn("DRY RUN", out)
        self.assertIn("[REGISTRY]", out)
        self.assertIn("[CONFIG]", out)
        self.assertEqual(sorted(p.name for p in self.home.iterdir()), [])

    def test_install_is_idempotent_and_preserves_existing_config(self):
        paths = installer.get_paths(self.home)
        # Konfigurasi pengguna yang sudah ada sebelumnya harus dipertahankan
        paths["config_dir"].mkdir(parents=True)
        paths["config_json"].write_text(json.dumps({"theme": "dark", "plugins": {"other": {"enabled": True}}}), encoding="utf-8")
        paths["skills_json"].write_text(json.dumps({"entries": [{"path": "skills/custom-user-skill"}]}), encoding="utf-8")
        paths["memory_file"].write_text("# Ledger milik pengguna\n", encoding="utf-8")

        for _ in range(2):  # dua kali: hasil harus identik, tanpa duplikasi
            self._run(installer.install_global, home=self.home)

        repo_skills = sorted(d.name for d in paths["repo_skills"].iterdir() if d.is_dir())
        for name in ("AGENTS.md", "GEMINI.md"):
            self.assertEqual(
                (paths["rules_dir"] / name).read_text(encoding="utf-8"),
                (self.repo_dir / name).read_text(encoding="utf-8"),
            )
        installed = sorted(d.name for d in paths["skills_dir"].iterdir() if d.is_dir())
        self.assertEqual(installed, repo_skills)
        self.assertTrue((paths["skills_dir"] / "claudia-brain" / "SKILL.md").exists())

        registry = json.loads(paths["skills_json"].read_text(encoding="utf-8"))["entries"]
        registry_paths = [e["path"] for e in registry]
        self.assertEqual(len(registry_paths), len(set(registry_paths)))
        self.assertIn("skills/custom-user-skill", registry_paths)
        for name in repo_skills:
            self.assertIn(f"skills/{name}", registry_paths)

        config = json.loads(paths["config_json"].read_text(encoding="utf-8"))
        self.assertEqual(config["theme"], "dark")
        self.assertEqual(config["plugins"]["other"], {"enabled": True})
        self.assertEqual(config["plugins"]["claudia-brain"], {"enabled": True})

        # memory.md milik pengguna tidak boleh ditimpa
        self.assertEqual(paths["memory_file"].read_text(encoding="utf-8"), "# Ledger milik pengguna\n")

    def test_install_seeds_memory_when_absent(self):
        paths, _ = self._run(installer.install_global, home=self.home)
        self.assertTrue(paths["memory_file"].exists())
        self.assertEqual(
            paths["memory_file"].read_text(encoding="utf-8"),
            paths["repo_memory_md"].read_text(encoding="utf-8"),
        )

    def test_install_recovers_from_corrupt_json(self):
        paths = installer.get_paths(self.home)
        paths["config_dir"].mkdir(parents=True)
        paths["config_json"].write_text("{corrupt", encoding="utf-8")
        paths["skills_json"].write_text("[]", encoding="utf-8")  # bukan objek
        self._run(installer.install_global, home=self.home)
        config = json.loads(paths["config_json"].read_text(encoding="utf-8"))
        self.assertEqual(config["plugins"]["claudia-brain"], {"enabled": True})
        self.assertTrue(json.loads(paths["skills_json"].read_text(encoding="utf-8"))["entries"])

    def test_uninstall_removes_only_installer_artifacts(self):
        paths = installer.get_paths(self.home)
        paths["config_dir"].mkdir(parents=True)
        paths["skills_json"].write_text(json.dumps({"entries": [{"path": "skills/custom-user-skill"}]}), encoding="utf-8")
        paths["config_json"].write_text(json.dumps({"plugins": {"other": {"enabled": True}}}), encoding="utf-8")
        (paths["skills_dir"] / "custom-user-skill").mkdir(parents=True)

        self._run(installer.install_global, home=self.home)
        self._run(installer.uninstall_global, home=self.home)

        self.assertFalse((paths["rules_dir"] / "AGENTS.md").exists())
        self.assertFalse((paths["rules_dir"] / "GEMINI.md").exists())
        self.assertFalse((paths["skills_dir"] / "claudia-brain").exists())
        self.assertTrue((paths["skills_dir"] / "custom-user-skill").exists())
        registry = json.loads(paths["skills_json"].read_text(encoding="utf-8"))["entries"]
        self.assertEqual(registry, [{"path": "skills/custom-user-skill"}])
        config = json.loads(paths["config_json"].read_text(encoding="utf-8"))
        self.assertNotIn("claudia-brain", config["plugins"])
        self.assertIn("other", config["plugins"])
        self.assertTrue(paths["memory_file"].exists())  # ledger dipertahankan

    def test_status_and_cli_entrypoint(self):
        _, out_before = self._run(installer.main, ["--status", "--home", str(self.home)])
        self.assertIn("DISABLED", out_before)
        self.assertIn("MISSING", out_before)

        code, _ = self._run(installer.main, ["--home", str(self.home)])
        self.assertEqual(code, 0)

        _, out_after = self._run(installer.main, ["--status", "--home", str(self.home)])
        self.assertIn("ENABLED", out_after)
        self.assertIn("claudia-brain", out_after)

        code, _ = self._run(installer.main, ["--uninstall", "--home", str(self.home)])
        self.assertEqual(code, 0)
        _, out_final = self._run(installer.main, ["--status", "--home", str(self.home)])
        self.assertIn("DISABLED", out_final)

        with self.assertRaises(SystemExit):
            installer.main(["--status", "--uninstall"])  # opsi saling eksklusif


if __name__ == "__main__":
    unittest.main()
