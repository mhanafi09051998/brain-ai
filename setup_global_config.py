#!/usr/bin/env python3
"""
Skrip Otomasi Instalasi Konfigurasi Global Claudia Brain (Cross-Workspace Installer).
Memasang aturan global, skills, dan ledger memori ke direktori pengguna (~/.gemini/config/)
sehingga Claudia Brain aktif secara otomatis di seluruh sesi dan folder kerja manapun.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import sys

# Konfigurasi encoding stdout untuk kompatibilitas Windows CP1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def get_paths():
    home = Path.home()
    gemini_dir = home / ".gemini"
    config_dir = gemini_dir / "config"
    rules_dir = config_dir / "rules"
    skills_dir = config_dir / "skills"
    memory_file = home / "memory.md"
    skills_json = config_dir / "skills.json"
    config_json = config_dir / "config.json"

    repo_dir = Path(__file__).resolve().parent
    repo_skills = repo_dir / ".agents" / "skills"
    repo_agents_md = repo_dir / "AGENTS.md"
    repo_gemini_md = repo_dir / "GEMINI.md"
    repo_memory_md = repo_dir / "memory.md"

    return {
        "home": home,
        "config_dir": config_dir,
        "rules_dir": rules_dir,
        "skills_dir": skills_dir,
        "memory_file": memory_file,
        "skills_json": skills_json,
        "config_json": config_json,
        "repo_dir": repo_dir,
        "repo_skills": repo_skills,
        "repo_agents_md": repo_agents_md,
        "repo_gemini_md": repo_gemini_md,
        "repo_memory_md": repo_memory_md
    }


def check_status(paths):
    print("=" * 60)
    print("[STATUS] KONFIGURASI GLOBAL CLAUDIA BRAIN")
    print("=" * 60)
    print(f"User Home       : {paths['home']}")
    print(f"Config Dir      : {paths['config_dir']} [{'EXISTS' if paths['config_dir'].exists() else 'MISSING'}]")
    print(f"Rules Dir       : {paths['rules_dir']} [{'EXISTS' if paths['rules_dir'].exists() else 'MISSING'}]")
    print(f"Global Memory   : {paths['memory_file']} [{'EXISTS' if paths['memory_file'].exists() else 'MISSING'}]")
    print(f"Skills Dir      : {paths['skills_dir']} [{'EXISTS' if paths['skills_dir'].exists() else 'MISSING'}]")

    if paths["skills_dir"].exists():
        installed_skills = [d.name for d in paths["skills_dir"].iterdir() if d.is_dir()]
        print(f"Installed Skills: {', '.join(installed_skills) if installed_skills else 'None'}")
    else:
        print("Installed Skills: None")

    print("=" * 60)


def install_global(dry_run=False):
    paths = get_paths()

    print("=" * 60)
    print("[INSTALL] MEMULAI INSTALASI KONFIGURASI GLOBAL CLAUDIA BRAIN")
    print(f"Mode: {'DRY RUN (Simulasi)' if dry_run else 'LIVE EXECUTION'}")
    print("=" * 60)

    # 1. Buat direktori rules & copy file aturan
    if not dry_run:
        paths["rules_dir"].mkdir(parents=True, exist_ok=True)

    for md_file, target_name in [(paths["repo_agents_md"], "AGENTS.md"), (paths["repo_gemini_md"], "GEMINI.md")]:
        if md_file.exists():
            target_path = paths["rules_dir"] / target_name
            print(f"  [RULES] Salin {md_file.name} -> {target_path}")
            if not dry_run:
                shutil.copyfile(md_file, target_path)

    # 2. Pasang Skills ke ~/.gemini/config/skills/
    if paths["repo_skills"].exists():
        if not dry_run:
            paths["skills_dir"].mkdir(parents=True, exist_ok=True)

        for skill_dir in paths["repo_skills"].iterdir():
            if skill_dir.is_dir():
                target_skill = paths["skills_dir"] / skill_dir.name
                print(f"  [SKILL] Pasang skill '{skill_dir.name}' -> {target_skill}")
                if not dry_run:
                    if target_skill.exists():
                        shutil.rmtree(target_skill)
                    shutil.copytree(skill_dir, target_skill)

    # 3. Daftarkan skills ke skills.json
    if not dry_run:
        skills_entries = []
        if paths["skills_json"].exists():
            try:
                with open(paths["skills_json"], "r", encoding="utf-8") as f:
                    data = json.load(f)
                    skills_entries = data.get("entries", [])
            except Exception:
                skills_entries = []

        existing_paths = {e.get("path") for e in skills_entries}
        if paths["repo_skills"].exists():
            for s in paths["repo_skills"].iterdir():
                if s.is_dir():
                    entry_rel = f"skills/{s.name}"
                    if entry_rel not in existing_paths:
                        skills_entries.append({"path": entry_rel})
                        existing_paths.add(entry_rel)

        paths["skills_json"].parent.mkdir(parents=True, exist_ok=True)
        with open(paths["skills_json"], "w", encoding="utf-8") as f:
            json.dump({"entries": skills_entries}, f, indent=2)
        print(f"  [REGISTRY] Diperbarui {paths['skills_json']} ({len(skills_entries)} skills aktif)")

    # 4. Inisialisasi memory.md global jika belum ada
    if not paths["memory_file"].exists():
        print(f"  [MEMORY] Inisialisasi Global Persistent Memory Ledger -> {paths['memory_file']}")
        if not dry_run and paths["repo_memory_md"].exists():
            shutil.copyfile(paths["repo_memory_md"], paths["memory_file"])
    else:
        print(f"  [MEMORY] Global Memory Ledger sudah ada di {paths['memory_file']} (Dipertahankan)")

    # 5. Aktifkan claudia-brain di config.json
    if not dry_run:
        config_data = {}
        if paths["config_json"].exists():
            try:
                with open(paths["config_json"], "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                config_data = {}

        plugins = config_data.setdefault("plugins", {})
        plugins["claudia-brain"] = {"enabled": True}

        with open(paths["config_json"], "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        print(f"  [CONFIG] Plugin 'claudia-brain' diaktifkan di {paths['config_json']}")

    print("=" * 60)
    print("[SUCCESS] INSTALASI GLOBAL SELESAI DENGAN SUKSES!")
    print("Claudia Brain kini aktif secara otomatis di seluruh sesi dan folder kerja.")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Installer Konfigurasi Global Claudia Brain (Cross-Workspace Engine)")
    parser.add_argument("--status", action="store_true", help="Cek status konfigurasi global saat ini")
    parser.add_argument("--dry-run", action="store_true", help="Simulasikan langkah instalasi tanpa menulis file")
    args = parser.parse_args()

    paths = get_paths()
    if args.status:
        check_status(paths)
    else:
        install_global(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
