# Cross-Session Cross-Workspace Memory

[ad-hoc note]

Pengguna ingin memori Codex aktif lintas sesi dan lintas workspace. Aturan utama:

1. **Sumber kebenaran memori**: `~/memory.md` (di Windows: `C:\Users\<user>\memory.md`). Berkas ini diinisialisasi otomatis oleh `setup_global_config.py` bila belum ada.
2. **Aturan perilaku global**: `~/.codex/AGENTS.md` (di Windows: `C:\Users\<user>\.codex\AGENTS.md`). Berkas ini dipasang otomatis oleh installer repo.
3. Pada sesi baru di folder apa pun, baca `~/memory.md` bila tugas menyentuh proyek yang terdaftar di sana.
4. Setelah tugas teknis penting selesai, tambahkan ringkasan keputusan/status ke `~/memory.md` (baris baru, tanpa menimpa isi lama).
5. Installer repo `brain-ai` (`python setup_global_config.py`) memasang keduanya secara otomatis, idempoten, dan tidak pernah menimpa `memory.md` yang sudah ada.
6. Jangan pernah mengekspos API key/token di output.
