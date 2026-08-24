# Neuron N020: Autonomous Cross-Session Memory & Resilient Checkpoint Continuity

## 📌 Tujuan Arsitektur
Memastikan **Claudia** memiliki memori kontinu lintas sesi kerja, tahan terhadap pemutusan koneksi (*session disconnect*), limit token/kuota model (*rate limits / quota exhausted*), serta mampu melanjutkan pekerjaan yang belum selesai di IDE atau agen mana pun (OpenCode, Gemini CLI, Antigravity, VS Code, Cursor, Windsurf, Neovim) tanpa kehilangan konteks.

---

## 💾 Mekanisme Penyimpanan State Permanen (Snapshot Ledger)
Setiap sesi kerja aktif wajib merekam progres ke berkas sinkronisasi persisten:
- **`memory.md`**: Peta indeks memori global aktif dan task list terkini.
- **`memory/session_checkpoint.json`**: State mesin terstruktur (JSON) yang berisi:
  1. `sessionId`: UUID percakapan aktif.
  2. `timestamp`: Waktu snapshot ISO-8601.
  3. `lastGoal`: Tujuan atau task utama yang sedang dikerjakan.
  4. `completedSteps`: Daftar sub-task yang telah selesai dan terverifikasi.
  5. `pendingSteps`: Daftar langkah yang masih tertunda atau terpotong.
  6. `modifiedFiles`: Daftar berkas yang sedang diubah beserta status verifikasinya.
  7. `activeContextRules`: Aturan arsitektur khusus yang sedang diterapkan.

---

## 🔄 Protokol Resume Lintas IDE & Model

Ketika Claudia dipanggil di sesi baru atau IDE baru (misal via OpenCode / Antigravity):

### 1. Inisialisasi Otomatis (Cold Start Traversal)
- Langkah 1: Baca `memory/session_checkpoint.json` dan `memory.md`.
- Langkah 2: Evaluasi `pendingSteps` dan `modifiedFiles`.
- Langkah 3: Jalankan self-verification (`git status`, `npm test` atau unit test terkait) untuk memeriksa apakah state codebase konsisten.

### 2. Protokol Penanganan Saat Kena Limit / Terpotong
Jika terjadi kendala koneksi atau kuota terlampaui:
1. Rekam jejak langkah terakhir ke `memory/session_checkpoint.json`.
2. Berikan instruksi langsung untuk menyambung sesi:
   ```bash
   # Melanjutkan sesi di CLI atau agen manapun:
   "Lanjutkan pekerjaan dari memory/session_checkpoint.json"
   ```
3. Agent penerus langsung membaca checkpoint tersebut dan mengeksekusi step berikutnya tanpa perlu mengulang penjelasan dari awal.

---

## 🔒 Kebijakan Integritas & Anti-Data Loss
1. **Zero State Desynchronization**: Tidak ada task yang ditinggalkan tanpa catatan status di `memory/session_checkpoint.json`.
2. **YAGNI & Minimality**: Hanya rekam hal penting (tujuan, file aktif, pending task, test status); jangan dump log riwayat mentah yang membengkakkan konteks.
3. **Auto-Sync GitHub**: Setelah memperbarui memori sesi, jalankan `python scripts/auto_sync_github.py` untuk mengamankan checkpoint ke remote repository.
