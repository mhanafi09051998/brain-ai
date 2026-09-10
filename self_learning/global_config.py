"""
Modul Manajemen Konfigurasi Global & Jembatan Lintas Workspace (Cross-Workspace Engine).
Memungkinkan pembacaan, sinkronisasi, dan registrasi proyek lintas sesi dan folder kerja.
"""

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional


@dataclass
class ProjectEntry:
    """Representasi proyek terdaftar di dalam Global Memory Ledger."""
    name: str
    location: str
    status: str
    notes: str


class GlobalConfigManager:
    """Pengelola konfigurasi global dan ledger memori sentral di lingkungan pengguna."""

    DEFAULT_MEMORY_FILENAME = "memory.md"

    @classmethod
    def get_user_home(cls) -> Path:
        """Mengembalikan path home direktori pengguna."""
        return Path.home()

    @classmethod
    def get_gemini_config_dir(cls) -> Path:
        """Mengembalikan direktori konfigurasi global Antigravity / Gemini (~/.gemini/config)."""
        return cls.get_user_home() / ".gemini" / "config"

    @classmethod
    def get_global_memory_path(cls) -> Path:
        """
        Mencari path berkas memory.md global.
        Prioritas:
        1. ~/memory.md
        2. ~/.gemini/memory.md
        """
        home_mem = cls.get_user_home() / cls.DEFAULT_MEMORY_FILENAME
        if home_mem.exists():
            return home_mem

        gemini_mem = cls.get_user_home() / ".gemini" / cls.DEFAULT_MEMORY_FILENAME
        if gemini_mem.exists():
            return gemini_mem

        # Default fallback ke ~/memory.md
        return home_mem

    @classmethod
    def get_global_skills_dir(cls) -> Path:
        """Mengembalikan path direktori skill global (~/.gemini/config/skills)."""
        return cls.get_gemini_config_dir() / "skills"

    @classmethod
    def get_global_rules_dir(cls) -> Path:
        """Mengembalikan path direktori aturan global (~/.gemini/config/rules)."""
        return cls.get_gemini_config_dir() / "rules"

    @classmethod
    def is_global_configured(cls) -> bool:
        """Memeriksa apakah konfigurasi global Claudia Brain sudah terpasang di sistem."""
        rules_dir = cls.get_global_rules_dir()
        has_rules = (rules_dir / "AGENTS.md").exists() or (rules_dir / "GEMINI.md").exists()
        has_memory = cls.get_global_memory_path().exists()
        return has_rules or has_memory

    @classmethod
    def parse_registered_projects(cls, memory_path: Optional[Path] = None) -> List[ProjectEntry]:
        """Membedah daftar proyek dari tabel register di memory.md."""
        mem_file = memory_path or cls.get_global_memory_path()
        if not mem_file.exists():
            return []

        projects = []
        try:
            with open(mem_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            in_table = False
            for line in lines:
                stripped = line.strip()
                if "Register Proyek" in stripped or "Register Project" in stripped:
                    in_table = True
                    continue

                if in_table:
                    if stripped.startswith("|") and not "Nama Proyek" in stripped:
                        cols = [c.strip() for c in stripped.split("|")[1:-1]]
                        # Abaikan baris pemisah tabel seperti | :--- | :--- |
                        if all(set(c).issubset({'-', ':', ' '}) for c in cols):
                            continue
                        if len(cols) >= 4:
                            name = re.sub(r"\*\*|\*", "", cols[0]).strip()
                            loc = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", cols[1]).strip("`").strip()
                            status = cols[2].strip()
                            notes = cols[3].strip()
                            projects.append(ProjectEntry(name=name, location=loc, status=status, notes=notes))
                    elif in_table and stripped.startswith("---") and len(projects) > 0:
                        break
        except Exception:
            pass

        return projects

    @classmethod
    def register_or_update_project(
        cls,
        name: str,
        location: str,
        status: str,
        notes: str,
        memory_path: Optional[Path] = None
    ) -> bool:
        """
        Menambahkan atau memperbarui entri proyek di dalam Global Memory Ledger.
        """
        mem_file = memory_path or cls.get_global_memory_path()
        if not mem_file.exists():
            # Inisialisasi memory.md baru jika belum ada
            content = (
                "# Claudia Brain: Global Persistent Memory Ledger\n\n"
                "## 1. Register Proyek & Status Lintas Workspace\n\n"
                "| Nama Proyek | Lokasi Direktori | Status Teknis | Catatan Kunci / Arsitektur |\n"
                "| :--- | :--- | :--- | :--- |\n"
                f"| **{name}** | `{location}` | {status} | {notes} |\n\n"
                "---\n"
            )
            with open(mem_file, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        with open(mem_file, "r", encoding="utf-8") as f:
            content = f.read()

        row_str = f"| **{name}** | `{location}` | {status} | {notes} |"

        # Jika nama proyek sudah ada di tabel, perbarui barisnya
        pattern = re.compile(rf"\|\s*\*\*{re.escape(name)}\*\*\s*\|.*\|", re.IGNORECASE)
        if pattern.search(content):
            new_content = pattern.sub(row_str, content)
        else:
            # Sisipkan ke bawah baris header tabel
            table_header_pat = re.compile(r"(\|\s*:---.*\|\n)")
            if table_header_pat.search(content):
                new_content = table_header_pat.sub(rf"\1{row_str}\n", content)
            else:
                new_content = content + f"\n\n## Register Proyek\n| Nama Proyek | Lokasi Direktori | Status Teknis | Catatan Kunci / Arsitektur |\n| :--- | :--- | :--- | :--- |\n{row_str}\n"

        with open(mem_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True


class WorkspaceBridge:
    """Jembatan lintas workspace untuk mencari dan menautkan artefak antar folder."""

    @classmethod
    def resolve_workspace_path(cls, relative_or_absolute: str, base_dir: Optional[Path] = None) -> Path:
        """Menghitung path absolut dan memverifikasi keberadaannya di sistem."""
        path_obj = Path(relative_or_absolute)
        if path_obj.is_absolute():
            return path_obj

        anchor = base_dir or Path.cwd()
        return (anchor / path_obj).resolve()

    @classmethod
    def get_cross_workspace_context(cls, project_name: str) -> Optional[Dict[str, Any]]:
        """Mencari data konteks proyek lain dari Global Memory Ledger."""
        projects = GlobalConfigManager.parse_registered_projects()
        for p in projects:
            if project_name.lower() in p.name.lower():
                return {
                    "name": p.name,
                    "location": p.location,
                    "status": p.status,
                    "notes": p.notes,
                    "exists_on_disk": Path(p.location).exists() if os.path.isabs(p.location) else False
                }
        return None
