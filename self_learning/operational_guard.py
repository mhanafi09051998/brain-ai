"""
Guardrail Klasifikasi Risiko Aksi (Operational Guard).

Padanan programatis dari Protokol Operasional Agen §5 (Keamanan, Izin & Aksi Ireversibel)
di `operational_protocol.md`: setiap perintah shell/git/SQL dinilai ke salah satu dari
4 tingkat risiko, dan aksi OUTWARD/IRREVERSIBLE wajib mendapat persetujuan per-aksi
(sekali pakai) sebelum dieksekusi.
"""

from dataclasses import dataclass
from enum import Enum
import re
from typing import Iterable, List, Pattern, Sequence, Set, Tuple


class RiskLevel(str, Enum):
    """Tingkat risiko aksi, terurut dari paling ringan ke paling berat."""
    SAFE = "safe"                # baca/inspeksi; tidak mengubah apa pun
    REVERSIBLE = "reversible"    # tulis lokal yang dapat dibatalkan (edit, commit, install)
    OUTWARD = "outward"          # meninggalkan mesin: push, publish, request mutasi ke layanan lain
    IRREVERSIBLE = "irreversible"  # hapus/timpa/reset tanpa jalan kembali


_SEVERITY = {
    RiskLevel.SAFE: 0,
    RiskLevel.REVERSIBLE: 1,
    RiskLevel.OUTWARD: 2,
    RiskLevel.IRREVERSIBLE: 3,
}


class ConfirmationRequiredError(PermissionError):
    """Dilempar saat aksi OUTWARD/IRREVERSIBLE dieksekusi tanpa persetujuan per-aksi."""


@dataclass(frozen=True)
class ActionAssessment:
    """Hasil penilaian satu perintah."""
    command: str
    risk: RiskLevel
    reasons: Tuple[str, ...]

    @property
    def requires_confirmation(self) -> bool:
        return ActionGuard.requires_confirmation(self.risk)


def _compile(rules: Sequence[Tuple[str, str]]) -> List[Tuple[Pattern[str], str]]:
    return [(re.compile(pattern, re.IGNORECASE | re.DOTALL), reason) for pattern, reason in rules]


class ActionGuard:
    """Menilai tingkat risiko perintah berdasarkan pola. Perintah majemuk (`&&`, `;`, `|`)
    dinilai pada tingkat tertinggi dari semua bagiannya."""

    IRREVERSIBLE_RULES = _compile([
        (r"\brm\s+-[a-z]*[rf][a-z]*\b", "hapus berkas rekursif/paksa (rm -r/-f)"),
        (r"\bRemove-Item\b[^|;&]*-Recurse", "hapus direktori rekursif (Remove-Item -Recurse)"),
        (r"\bgit\s+push\b[^|;&]*(?:--force\b|--force-with-lease\b|\s-f\b|\s\+\w)", "force push menimpa riwayat remote"),
        (r"\bgit\s+reset\s+--hard\b", "git reset --hard membuang perubahan"),
        (r"\bgit\s+checkout\s+--\s", "git checkout -- membuang perubahan working tree"),
        (r"\bgit\s+restore\b(?![^|;&]*--staged)", "git restore membuang perubahan working tree"),
        (r"\bgit\s+clean\s+-[a-z]*f", "git clean -f menghapus berkas untracked"),
        (r"\bgit\s+branch\s+-D\b", "hapus cabang paksa"),
        (r"\bgit\s+stash\s+(drop|clear)\b", "hapus stash"),
        (r"\bDROP\s+(TABLE|DATABASE|SCHEMA|INDEX|VIEW)\b", "DROP objek basis data"),
        (r"\bTRUNCATE\s+(TABLE\s+)?\w", "TRUNCATE tabel"),
        (r"\bDELETE\s+FROM\b(?![^;]*\bWHERE\b)", "DELETE tanpa klausa WHERE"),
        (r"\bUPDATE\s+\w+\s+SET\b(?![^;]*\bWHERE\b)", "UPDATE tanpa klausa WHERE"),
        (r"\b(mkfs(\.\w+)?|shred|wipefs)\b|\bdd\s+if=", "operasi tingkat disk destruktif"),
        (r"\bformat\s+[a-z]:", "format drive"),
        (r"\bdocker\s+(system\s+prune|volume\s+(rm|prune)|rm\s+-f|rmi\s+-f)\b", "hapus resource docker paksa"),
        (r"\bpm2\s+(delete|kill|flush)\b", "hapus proses/log pm2"),
        (r"\bkubectl\s+delete\b|\bterraform\s+destroy\b", "hapus resource infrastruktur"),
        (r"\b(aws|gcloud|az)\b[^|;&]*\b(delete|rm|remove|destroy)\b", "hapus resource cloud"),
    ])

    OUTWARD_RULES = _compile([
        (r"\bgit\s+push\b", "push ke remote"),
        (r"\bgh\s+(pr\s+(create|merge|close)|release\s+(create|delete)|repo\s+(create|delete)|issue\s+(create|close))\b", "mutasi GitHub via gh"),
        (r"\b(npm|pnpm|yarn)\s+publish\b|\btwine\s+upload\b|\bcargo\s+publish\b|\bgem\s+push\b", "publikasi paket ke registry"),
        (r"\bcurl\b[^|;&]*(\s-X\s*(POST|PUT|PATCH|DELETE)\b|\s(-d|--data(-\w+)?|-F|--form|-T|--upload-file)\b)", "HTTP request mutasi ke layanan eksternal"),
        (r"\bInvoke-(RestMethod|WebRequest)\b[^|;&]*-Method\s+(Post|Put|Patch|Delete)\b", "HTTP request mutasi ke layanan eksternal"),
        (r"\bwget\b[^|;&]*--post-(data|file)\b", "HTTP POST ke layanan eksternal"),
        (r"\bssh\b[^|;&]*\b(rm|reboot|shutdown|systemctl\s+(stop|restart|disable|mask)|pm2\s+(restart|stop|delete)|kill(all)?)\b", "mutasi server remote via ssh"),
        (r"\b(scp|rsync)\b[^|;&]*\s\S+@\S+:", "salin berkas ke host remote"),
        (r"\b(aws|gcloud|az|kubectl|terraform|helm)\s+(apply|deploy|create|run|upgrade|install)\b", "deploy/mutasi infrastruktur"),
        (r"\bdocker\s+push\b", "push image ke registry"),
        (r"\b(sendmail|mail|mutt)\b\s", "kirim email"),
    ])

    REVERSIBLE_RULES = _compile([
        (r"\bgit\s+(commit|add|stash(\s+push|\s+pop)?|checkout\s+-b|switch|merge|rebase|cherry-pick|tag|mv|rm)\b", "mutasi repo lokal (dapat dibatalkan)"),
        (r"\b(mv|cp|mkdir|touch|ln|tee|Move-Item|Copy-Item|New-Item|Set-Content|Add-Content|Out-File|Rename-Item)\b", "tulis/pindah berkas lokal"),
        (r"(?<![<>])>{1,2}\s*(?!/dev/null|\$null)\S", "redirect output ke berkas"),
        (r"\b(pip|pip3|npm|pnpm|yarn|cargo|apt|apt-get|brew|choco|winget)\s+(install|uninstall|remove|add|i|purge)\b", "ubah paket terpasang"),
        (r"\bsed\s+-i\b", "edit berkas in-place"),
        (r"\b(chmod|chown|icacls)\b", "ubah permission berkas"),
        (r"\b(systemctl|pm2)\s+(start|restart|stop|enable|reload|save)\b", "ubah status proses lokal"),
        (r"\bdocker\s+(run|start|stop|restart|build|compose\s+(up|down))\b", "ubah status container lokal"),
        (r"\b(export|set|setx)\s+\w+=", "ubah variabel lingkungan"),
    ])

    @classmethod
    def requires_confirmation(cls, risk: RiskLevel) -> bool:
        """OUTWARD dan IRREVERSIBLE wajib konfirmasi per-aksi (OP-5.1)."""
        return _SEVERITY[risk] >= _SEVERITY[RiskLevel.OUTWARD]

    @classmethod
    def assess(cls, command: str) -> ActionAssessment:
        """Menilai satu perintah. Bagian majemuk dinilai bersama; tingkat tertinggi menang."""
        text = command.strip()
        if not text:
            return ActionAssessment(command, RiskLevel.SAFE, ())

        matched: List[Tuple[RiskLevel, str]] = []
        for level, rules in (
            (RiskLevel.IRREVERSIBLE, cls.IRREVERSIBLE_RULES),
            (RiskLevel.OUTWARD, cls.OUTWARD_RULES),
            (RiskLevel.REVERSIBLE, cls.REVERSIBLE_RULES),
        ):
            for pattern, reason in rules:
                if pattern.search(text):
                    matched.append((level, reason))

        if not matched:
            return ActionAssessment(command, RiskLevel.SAFE, ())

        top = max(matched, key=lambda item: _SEVERITY[item[0]])[0]
        reasons = tuple(dict.fromkeys(reason for level, reason in matched if level == top))
        return ActionAssessment(command, top, reasons)

    @classmethod
    def assess_many(cls, commands: Iterable[str]) -> List[ActionAssessment]:
        return [cls.assess(c) for c in commands]

    @classmethod
    def enforce(cls, command: str, approvals: "ApprovalRegistry | None" = None) -> ActionAssessment:
        """Menilai perintah dan melempar `ConfirmationRequiredError` jika perintah membutuhkan
        konfirmasi tetapi belum disetujui di `approvals`. Persetujuan yang dipakai dikonsumsi."""
        assessment = cls.assess(command)
        if not assessment.requires_confirmation:
            return assessment
        if approvals is not None and approvals.consume(command):
            return assessment
        raise ConfirmationRequiredError(
            f"Aksi {assessment.risk.value.upper()} membutuhkan konfirmasi pengguna per-aksi "
            f"({'; '.join(assessment.reasons)}): {command.strip()}"
        )


class ApprovalRegistry:
    """Persetujuan per-aksi sekali pakai (OP-5.1). Persetujuan hanya berlaku untuk perintah
    yang persis sama (setelah normalisasi spasi) dan hangus setelah dipakai satu kali —
    "ya, push" untuk satu commit tidak berlaku untuk commit berikutnya."""

    def __init__(self) -> None:
        self._approved: Set[str] = set()

    @staticmethod
    def normalize(command: str) -> str:
        return " ".join(command.split())

    def grant(self, command: str) -> None:
        self._approved.add(self.normalize(command))

    def is_approved(self, command: str) -> bool:
        return self.normalize(command) in self._approved

    def consume(self, command: str) -> bool:
        """Mengembalikan True dan mencabut persetujuan jika perintah disetujui; False jika tidak."""
        key = self.normalize(command)
        if key in self._approved:
            self._approved.remove(key)
            return True
        return False

    def revoke_all(self) -> None:
        self._approved.clear()
