# Persistent Project Memory & Context

Dokumen ini adalah memori dinamis jangka panjang proyek. Dokumen ini diperbarui secara berkelanjutan agar asisten tidak kehilangan konteks antar sesi percakapan.

---

## 1. Profil & Identitas Asisten
- **Nama**: Claudia
- **Karakter & Gaya Komunikasi**: Mengacu ke [`soul.md`](soul.md):
  - Singkat, padat, lugas, tanpa basa-basi pengantar/penutup klise.
  - Berbasis empiris dan kode nyata yang dapat diverifikasi.
  - Klarifikasi jika instruksi ambigu, nol halusinasi, dan anti-over-engineering (KISS & YAGNI).

---

## 2. Status Proyek & Konteks Workspace
- **Workspace Root**: `C:\Users\Win10\Music\train`
- **Subjek**: Pusat Arsitektur & Sistem Kecerdasan Claudia (Context7 Deep Mode Core). Seluruh proyek aplikasi eksternal telah dibersihkan agar workspace fokus murni pada mesin penalaran, task flow otonom, dan memori jangka panjang.
- **Komponen Utama**:
  1. `self_learning/`: Framework Multi-Agent optimasi mandiri, Reflexion Engine 4-kuadran, Closed-Loop Task Flow 6-fase, Multi-Task Flow terdistribusi, dan KnowledgeStore berbasis JSON.
  2. `.agents/skills/document-controller/`: Custom skill Document Controller berbasis ISO 9001:2015 Klausul 7.5.
  3. Dokumen Aturan & Identitas: [`GEMINI.md`](GEMINI.md), [`AGENTS.md`](AGENTS.md), [`identity.md`](identity.md), [`soul.md`](soul.md), [`README.md`](README.md), [`memory.md`](memory.md).
  4. Protokol Sistem: [`self_learning/protocol.md`](self_learning/protocol.md), [`self_learning/reflection_protocol.md`](self_learning/reflection_protocol.md), [`self_learning/agentic_task_flow.md`](self_learning/agentic_task_flow.md), [`self_learning/multi_task_flow.md`](self_learning/multi_task_flow.md).
  5. Pengujian Integritas: 19 unit tests otomatis terverifikasi lulus sempurna (`test_*.py`).

---

## 3. Catatan Keputusan Teknis & Preferensi
- Selalu gunakan type hints dan doctests pada kode Python baru.
- Mode Self-Learning aktif: setiap pengujian dan optimasi dievaluasi empiris menggunakan siklus tertutup (Observe -> Critique -> Distill -> Optimize) dan disaring ke `KnowledgeStore`.
- Mode Refleksi aktif: saat menghadapi kegagalan/error, wajib melakukan retrospeksi 4-kuadran (Target, Aktual, Akar Masalah, Tindakan Korektif) dan menyuntikkannya sebagai constraint sebelum mencoba kembali via `self_learning/reflection.py`.
- Arsitektur full-stack Node.js/TypeScript menggunakan paradigma hybrid SSR/RSC + Client Components, validasi runtime Zod, dan Prisma ORM.
- Penjelasan dan komunikasi menggunakan Bahasa Indonesia yang ringkas, teknis, dan presisi.
- Mekanisme persistensi konteks: Menggunakan kombinasi Workspace Rules (`GEMINI.md` / `AGENTS.md`) yang otomatis di-inject pada setiap sesi baru, ditambah sinkronisasi rutin ke file `memory.md`.
- Closed-Loop Agentic Task Flow aktif: Setiap penanganan tugas wajib melalui 6 fase (Ingestion, Planning, Execution, Verification, Reflexion, Distillation) sesuai `self_learning/agentic_task_flow.md` dan `self_learning/task_flow.py`.

---

## 4. Riwayat Sesi & Log Perkembangan
| Tanggal / Sesi | Aktivitas & Perubahan Penting | Status |
| :--- | :--- | :--- |
| Sesi Sebelumnya | Pembuatan modul pembelajaran 01-07, kode contoh implementasi, verifikasi 110 doctests, inisialisasi `identity.md` & `soul.md`. | Selesai |
| 2026-09-09 (Awal) | Pembentukan mekanisme retensi konteks lintas sesi (`GEMINI.md`, `AGENTS.md`, `memory.md`). | Selesai & Aktif |
| 2026-09-09 | Clone dan bedah arsitektur repositori Full-Stack modern (`shadcn-ui/taxonomy` di `fullstack_nextjs_taxonomy`). | Selesai |
| 2026-09-09 | Penyusunan modul dokumentasi lengkap 01 s.d. 07 di `hasil_pembelajaran_fullstack/`. | Selesai |
| 2026-09-09 | Pembuatan implementasi UI YouTube identik di `youtube_clone/index.html`. | Selesai |
| 2026-09-09 | Implementasi Protokol Mode Self-Learning & Framework Agent Optimasi Mandiri (`self_learning/`), terverifikasi 5 unit tests & benchmark. | Selesai |
| 2026-09-09 | Implementasi Mode Refleksi (Verbal Self-Reflection / Reflexion Engine di `self_learning/reflection.py`), terverifikasi 4 unit tests (total 9 tests passing). | Selesai |
| 2026-09-09 | Pembuatan klon UI Google Drive Desktop identik (`google_drive_clone/index.html` & `README.md`). | Selesai |
| 2026-09-09 | Formalisasi dan implementasi Closed-Loop Agentic Task Flow 6-Fase (`self_learning/task_flow.py`, `agentic_task_flow.md`, `GEMINI.md`), terverifikasi 11 unit tests passing. | Selesai & Aktif |
| 2026-09-09 | Pembuatan proyek Full-Stack Biografi dengan Laravel 12 (`biografi_fullstack/`), SQLite, Blade, Tailwind CSS, RESTful API, dan pengujian unit (8 tests passing). | Selesai & Terverifikasi |
| 2026-09-09 | Riset repositori Document Controller, pembuatan skill `document-controller` (ISO 9001 & Laravel EDMS di `.gemini/config/skills` & `.agents/skills`), serta manajemen & restrukturisasi master `README.md` workspace `train`. | Selesai & Aktif |
| 2026-09-09 | Standarisasi penamaan direktori `hasil_pembelajaran` menjadi `hasil_pembelajaran_algoritma_python` sesuai prinsip Document Controller (ISO 9001 Klausul 7.5), inisialisasi package Python, pembaruan tautan/impor, dan verifikasi 110 doctests lulus. | Selesai & Terverifikasi |
| 2026-09-09 | Instalasi menyeluruh Claudia Brain ke Konfigurasi Global Antigravity (`~/.gemini/config/` dan `~`): plugin `claudia-brain`, skill `claudia-brain`, aturan global (`AGENTS.md` & `GEMINI.md`), aktivasi di `config.json`, `plugins.json`, dan `skills.json`. | Selesai & Aktif Global |
| 2026-09-09 | Pembangunan arsitektur WebXR interaktif di `C:\Users\Win10\Music\arvr` (Three.js r174, WebXR Device API, 6DoF VR Controllers, Spatial Teleportation, 3D Floating Spatial UI Canvas, Web Audio API Synthesizer, Vite build terverifikasi 0 error). | Selesai & Terverifikasi |
| 2026-09-09 | Perancangan & implementasi Framework Multi-Task Flow (`self_learning/multi_task_flow.py`, `multi_task_flow.md`): membagi pipeline kerja spesifik per domain (Full-Stack, Researcher, Spatial XR, Document Controller), mendukung Dynamic Task Flow Synthesis saat ada domain/skill baru, terverifikasi 19 unit tests lulus, dan sinkronisasi ke global skill `claudia-brain`. | Selesai & Terverifikasi |
| 2026-09-09 | Kodifikasi & aktivasi resmi **Context7 Deep Mode** secara global (`~/.gemini/config/rules/`, `~/.gemini/config/plugins/`, `C:\Users\Win10\AGENTS.md`, `GEMINI.md`, `soul.md`): mengunci 3 Invarian Mutlak (Kebenaran Faktual, Tangga Minimalis/Minimal Diffs, Eksekusi Kepadatan Tinggi) dan 3 Protokol Intelijen Otomatis (Auto-Plan, Auto-Boost, Auto-Learn). | Selesai & Aktif Global |
| 2026-09-09 | Pembersihan total seluruh proyek eksternal di direktori `train` (`biografi_fullstack`, `fullstack_nextjs_taxonomy`, `google_drive_clone`, `hasil_pembelajaran_*`, `the_algorithms_python`, `youtube_clone`). Workspace dikonversi murni menjadi **Claudia Intelligence Hub** (`self_learning/`, `.agents/skills/document-controller/`, aturan, identitas, memori terverifikasi 19 unit tests lulus). | Selesai & Bersih |







