#!/usr/bin/env python3
"""
Skrip Otomasi Instalasi Konfigurasi Global Claudia Brain (Cross-Workspace Installer).
Memasang aturan global, skills, dan ledger memori ke direktori pengguna (~/.gemini/config/)
sehingga Claudia Brain aktif secara otomatis di seluruh sesi dan folder kerja manapun.

Perintah:
  python setup_global_config.py            # pasang (idempoten, aman dijalankan ulang)
  python setup_global_config.py --dry-run  # simulasi tanpa menulis berkas
  python setup_global_config.py --status   # cek status instalasi
  python setup_global_config.py --uninstall # lepas rules/skills/registry (memory.md dipertahankan)
"""

import argparse
import json
from pathlib import Path
import shutil
import sys
from typing import Any, Dict, Optional

# Konfigurasi encoding stdout untuk kompatibilitas Windows CP1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PLUGIN_NAME = "claudia-brain"
RULE_FILES = ("AGENTS.md", "GEMINI.md")


def get_paths(home: Optional[Path] = None, repo_dir: Optional[Path] = None) -> Dict[str, Path]:
    """Memetakan seluruh path sumber (repo) dan tujuan (home pengguna).
    `home`/`repo_dir` dapat dioverride untuk pengujian terisolasi."""
    home = Path(home) if home is not None else Path.home()
    repo_dir = Path(repo_dir) if repo_dir is not None else Path(__file__).resolve().parent
    config_dir = home / ".gemini" / "config"

    return {
        "home": home,
        "config_dir": config_dir,
        "rules_dir": config_dir / "rules",
        "skills_dir": config_dir / "skills",
        "memory_file": home / "memory.md",
        "skills_json": config_dir / "skills.json",
        "config_json": config_dir / "config.json",
        "repo_dir": repo_dir,
        "repo_skills": repo_dir / ".agents" / "skills",
        "repo_agents_md": repo_dir / "AGENTS.md",
        "repo_gemini_md": repo_dir / "GEMINI.md",
        "repo_memory_md": repo_dir / "memory.md",
    }


def _read_json(path: Path) -> Dict[str, Any]:
    """Membaca objek JSON; berkas yang tidak ada/rusak dianggap kosong."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def _repo_skill_dirs(paths: Dict[str, Path]):
    if not paths["repo_skills"].exists():
        return []
    return sorted(d for d in paths["repo_skills"].iterdir() if d.is_dir())


def check_status(paths: Dict[str, Path]) -> None:
    def flag(p: Path) -> str:
        return "EXISTS" if p.exists() else "MISSING"

    print("=" * 60)
    print("[STATUS] KONFIGURASI GLOBAL CLAUDIA BRAIN")
    print("=" * 60)
    print(f"User Home       : {paths['home']}")
    print(f"Config Dir      : {paths['config_dir']} [{flag(paths['config_dir'])}]")
    print(f"Rules Dir       : {paths['rules_dir']} [{flag(paths['rules_dir'])}]")
    for name in RULE_FILES:
        print(f"  - {name:<12}: [{flag(paths['rules_dir'] / name)}]")
    print(f"Global Memory   : {paths['memory_file']} [{flag(paths['memory_file'])}]")
    print(f"Skills Dir      : {paths['skills_dir']} [{flag(paths['skills_dir'])}]")

    if paths["skills_dir"].exists():
        installed_skills = sorted(d.name for d in paths["skills_dir"].iterdir() if d.is_dir())
        print(f"Installed Skills: {', '.join(installed_skills) if installed_skills else 'None'}")
    else:
        print("Installed Skills: None")

    plugins = _read_json(paths["config_json"]).get("plugins", {})
    enabled = bool(plugins.get(PLUGIN_NAME, {}).get("enabled")) if isinstance(plugins, dict) else False
    print(f"Plugin '{PLUGIN_NAME}': {'ENABLED' if enabled else 'DISABLED'}")
    print("=" * 60)


def install_global(dry_run: bool = False, home: Optional[Path] = None, repo_dir: Optional[Path] = None) -> Dict[str, Path]:
    paths = get_paths(home, repo_dir)

    print("=" * 60)
    print("[INSTALL] MEMULAI INSTALASI KONFIGURASI GLOBAL CLAUDIA BRAIN")
    print(f"Mode: {'DRY RUN (Simulasi)' if dry_run else 'LIVE EXECUTION'}")
    print("=" * 60)

    # 1. Buat direktori rules & copy file aturan
    for md_file in (paths["repo_agents_md"], paths["repo_gemini_md"]):
        if md_file.exists():
            target_path = paths["rules_dir"] / md_file.name
            print(f"  [RULES] Salin {md_file.name} -> {target_path}")
            if not dry_run:
                paths["rules_dir"].mkdir(parents=True, exist_ok=True)
                shutil.copyfile(md_file, target_path)
        else:
            print(f"  [RULES] Lewati {md_file.name} (tidak ditemukan di repo)")

    # 2. Pasang Skills ke ~/.gemini/config/skills/
    skill_dirs = _repo_skill_dirs(paths)
    for skill_dir in skill_dirs:
        target_skill = paths["skills_dir"] / skill_dir.name
        print(f"  [SKILL] Pasang skill '{skill_dir.name}' -> {target_skill}")
        if not dry_run:
            paths["skills_dir"].mkdir(parents=True, exist_ok=True)
            if target_skill.exists():
                shutil.rmtree(target_skill)
            shutil.copytree(skill_dir, target_skill)

    # 3. Daftarkan skills ke skills.json (tanpa duplikasi, entri lain dipertahankan)
    skills_entries = list(_read_json(paths["skills_json"]).get("entries", []))
    existing_paths = {e.get("path") for e in skills_entries if isinstance(e, dict)}
    for s in skill_dirs:
        entry_rel = f"skills/{s.name}"
        if entry_rel not in existing_paths:
            skills_entries.append({"path": entry_rel})
            existing_paths.add(entry_rel)
    print(f"  [REGISTRY] Perbarui {paths['skills_json']} ({len(skills_entries)} skills aktif)")
    if not dry_run:
        _write_json(paths["skills_json"], {"entries": skills_entries})

    # 4. Inisialisasi memory.md global jika belum ada (yang sudah ada tidak pernah ditimpa)
    if not paths["memory_file"].exists():
        print(f"  [MEMORY] Inisialisasi Global Persistent Memory Ledger -> {paths['memory_file']}")
        if not dry_run and paths["repo_memory_md"].exists():
            shutil.copyfile(paths["repo_memory_md"], paths["memory_file"])
    else:
        print(f"  [MEMORY] Global Memory Ledger sudah ada di {paths['memory_file']} (Dipertahankan)")

    # 5. Aktifkan claudia-brain di config.json
    print(f"  [CONFIG] Aktifkan plugin '{PLUGIN_NAME}' di {paths['config_json']}")
    if not dry_run:
        config_data = _read_json(paths["config_json"])
        plugins = config_data.setdefault("plugins", {})
        if not isinstance(plugins, dict):
            plugins = config_data["plugins"] = {}
        plugins[PLUGIN_NAME] = {"enabled": True}
        _write_json(paths["config_json"], config_data)

    print("=" * 60)
    if dry_run:
        print("[DRY RUN] Simulasi selesai. Tidak ada berkas yang ditulis.")
    else:
        print("[SUCCESS] INSTALASI GLOBAL SELESAI DENGAN SUKSES!")
        print("Claudia Brain kini aktif secara otomatis di seluruh sesi dan folder kerja.")
    print("=" * 60)
    return paths


def uninstall_global(home: Optional[Path] = None, repo_dir: Optional[Path] = None) -> Dict[str, Path]:
    """Melepas rules, skills, entri registry, dan flag plugin yang dipasang installer ini.
    `~/memory.md` sengaja dipertahankan karena berisi ledger memori pengguna."""
    paths = get_paths(home, repo_dir)

    print("=" * 60)
    print("[UNINSTALL] MELEPAS KONFIGURASI GLOBAL CLAUDIA BRAIN")
    print("=" * 60)

    for name in RULE_FILES:
        target = paths["rules_dir"] / name
        if target.exists():
            target.unlink()
            print(f"  [RULES] Hapus {target}")

    skill_names = {d.name for d in _repo_skill_dirs(paths)}
    for name in sorted(skill_names):
        target = paths["skills_dir"] / name
        if target.exists():
            shutil.rmtree(target)
            print(f"  [SKILL] Hapus {target}")

    if paths["skills_json"].exists():
        entries = _read_json(paths["skills_json"]).get("entries", [])
        kept = [e for e in entries if not (isinstance(e, dict) and e.get("path", "").removeprefix("skills/") in skill_names)]
        _write_json(paths["skills_json"], {"entries": kept})
        print(f"  [REGISTRY] Perbarui {paths['skills_json']} ({len(kept)} skills tersisa)")

    if paths["config_json"].exists():
        config_data = _read_json(paths["config_json"])
        plugins = config_data.get("plugins")
        if isinstance(plugins, dict) and PLUGIN_NAME in plugins:
            del plugins[PLUGIN_NAME]
            _write_json(paths["config_json"], config_data)
            print(f"  [CONFIG] Nonaktifkan plugin '{PLUGIN_NAME}' di {paths['config_json']}")

    print(f"  [MEMORY] {paths['memory_file']} dipertahankan (hapus manual jika tidak diperlukan)")
    print("=" * 60)
    print("[DONE] Uninstall selesai.")
    print("=" * 60)
    return paths


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description="Installer Konfigurasi Global Claudia Brain (Cross-Workspace Engine)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--status", action="store_true", help="Cek status konfigurasi global saat ini")
    group.add_argument("--dry-run", action="store_true", help="Simulasikan langkah instalasi tanpa menulis file")
    group.add_argument("--uninstall", action="store_true", help="Lepas rules/skills/registry (memory.md dipertahankan)")
    parser.add_argument("--home", type=Path, default=None, help="Override direktori home pengguna (untuk pengujian)")
    args = parser.parse_args(argv)

    if args.status:
        check_status(get_paths(args.home))
    elif args.uninstall:
        uninstall_global(home=args.home)
    else:
        install_global(dry_run=args.dry_run, home=args.home)
    return 0


if __name__ == "__main__":
    sys.exit(main())
