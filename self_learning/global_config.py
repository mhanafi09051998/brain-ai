"""
Modul Manajemen Konfigurasi Global & Jembatan Lintas Workspace (Cross-Workspace Engine).
Memungkinkan pembacaan, sinkronisasi, dan registrasi proyek lintas sesi dan folder kerja.
"""

from dataclasses import dataclass
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


# Penanda heading bagian register proyek di memory.md (ID/EN)
REGISTER_HEADING_RE = re.compile(r"^#{1,6}\s.*\b(Register Proyek|Register Project)\b.*$", re.IGNORECASE | re.MULTILINE)
# Baris pemisah tabel markdown, misal: | :--- | :--- | :--- | :--- |
TABLE_SEPARATOR_RE = re.compile(r"^\|(?:\s*:?-{3,}:?\s*\|)+[ \t]*\r?\n", re.MULTILINE)
TABLE_HEADER = "| Nama Proyek | Lokasi Direktori | Status Teknis | Catatan Kunci / Arsitektur |"
TABLE_SEPARATOR = "| :--- | :--- | :--- | :--- |"


def _is_separator_row(cols: List[str]) -> bool:
    return all(set(c).issubset({"-", ":", " "}) for c in cols)


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
        """Membedah daftar proyek dari tabel register di memory.md.

        Hanya tabel di bawah heading "Register Proyek"/"Register Project" yang dibaca;
        pembacaan berhenti pada heading berikutnya atau pemisah `---`.
        """
        mem_file = memory_path or cls.get_global_memory_path()
        if not mem_file.exists():
            return []

        try:
            lines = mem_file.read_text(encoding="utf-8").splitlines()
        except OSError:
            return []

        projects: List[ProjectEntry] = []
        in_table = False
        for line in lines:
            stripped = line.strip()
            if not in_table:
                if REGISTER_HEADING_RE.match(stripped):
                    in_table = True
                continue

            if stripped.startswith("|"):
                cols = [c.strip() for c in stripped.split("|")[1:-1]]
                if _is_separator_row(cols) or "Nama Proyek" in stripped:
                    continue
                if len(cols) >= 4:
                    name = re.sub(r"\*\*|\*", "", cols[0]).strip()
                    loc = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", cols[1]).strip("`").strip()
                    projects.append(ProjectEntry(name=name, location=loc, status=cols[2], notes=cols[3]))
            elif stripped.startswith("#") or stripped.startswith("---"):
                # Akhir bagian register
                break

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
        Baris baru selalu disisipkan ke tabel di bawah heading "Register Proyek";
        jika bagian tersebut belum ada, bagian baru dibuat di akhir berkas.
        """
        if not name.strip():
            raise ValueError("Nama proyek tidak boleh kosong.")

        mem_file = memory_path or cls.get_global_memory_path()
        row_str = f"| **{name}** | `{location}` | {status} | {notes} |"

        if not mem_file.exists():
            content = (
                "# Claudia Brain: Global Persistent Memory Ledger\n\n"
                "## 1. Register Proyek & Status Lintas Workspace\n\n"
                f"{TABLE_HEADER}\n{TABLE_SEPARATOR}\n{row_str}\n\n---\n"
            )
            mem_file.parent.mkdir(parents=True, exist_ok=True)
            mem_file.write_text(content, encoding="utf-8")
            return True

        content = mem_file.read_text(encoding="utf-8")

        # 1. Proyek sudah terdaftar -> perbarui barisnya di tempat
        existing_row = re.compile(
            rf"^\|\s*\*\*{re.escape(name)}\*\*\s*\|[^\r\n]*$", re.IGNORECASE | re.MULTILINE
        )
        if existing_row.search(content):
            new_content = existing_row.sub(lambda _m: row_str, content, count=1)
        else:
            heading = REGISTER_HEADING_RE.search(content)
            separator = TABLE_SEPARATOR_RE.search(content, heading.end()) if heading else None
            if separator:
                # 2. Sisipkan tepat di bawah baris pemisah tabel register
                new_content = content[: separator.end()] + row_str + "\n" + content[separator.end():]
            else:
                # 3. Belum ada bagian register -> buat bagian baru
                new_content = (
                    content.rstrip("\r\n")
                    + f"\n\n## Register Proyek\n\n{TABLE_HEADER}\n{TABLE_SEPARATOR}\n{row_str}\n"
                )

        mem_file.write_text(new_content, encoding="utf-8")
        return True


class WorkspaceBridge:
    """Jembatan lintas workspace untuk mencari dan menautkan artefak antar folder."""

    @classmethod
    def resolve_workspace_path(cls, relative_or_absolute: str, base_dir: Optional[Path] = None) -> Path:
        """Menghitung path absolut dari path relatif terhadap `base_dir` (default: cwd)."""
        path_obj = Path(relative_or_absolute)
        if path_obj.is_absolute():
            return path_obj

        anchor = base_dir or Path.cwd()
        return (anchor / path_obj).resolve()

    @classmethod
    def get_cross_workspace_context(
        cls, project_name: str, memory_path: Optional[Path] = None
    ) -> Optional[Dict[str, Any]]:
        """Mencari data konteks proyek lain dari Global Memory Ledger (pencocokan nama parsial)."""
        needle = project_name.lower()
        for p in GlobalConfigManager.parse_registered_projects(memory_path):
            if needle in p.name.lower():
                return {
                    "name": p.name,
                    "location": p.location,
                    "status": p.status,
                    "notes": p.notes,
                    "exists_on_disk": Path(p.location).exists() if os.path.isabs(p.location) else False,
                }
        return None
