<div align="center">

# 🧠 Claudia Brain AI
### *Context7 Deep Mode: Arsitektur Agen Mandiri, Reflexion Engine & Closed-Loop Task Flow*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Architecture](https://img.shields.io/badge/Architecture-Context7%20Deep%20Mode-8A2BE2?style=for-the-badge)](https://github.com/mhanafi09051998/brain-ai)
[![Test Suite](https://img.shields.io/badge/Tests-27%2F27%20Passing%20(100%25)-success?style=for-the-badge&logo=pytest&logoColor=white)](https://github.com/mhanafi09051998/brain-ai)
[![ISO Standard](https://img.shields.io/badge/Standard-ISO%209001%3A2015%20Clause%207.5-orange?style=for-the-badge)](https://github.com/mhanafi09051998/brain-ai)
[![Zero Leak](https://img.shields.io/badge/Security-Zero%20Credential%20Leakage-green?style=for-the-badge&logo=securityscorecard&logoColor=white)](https://github.com/mhanafi09051998/brain-ai)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

<p align="center">
  <b>Sistem Kecerdasan AI Tingkat Produksi</b> yang mengintegrasikan penalaran otonom, refleksi diri 4-kuadran, pembelajaran mandiri siklus tertutup (OODA), dan memori persisten lintas sesi serta lintas direktori kerja.
</p>

---

[📖 Filosofi Inti](#-1-filosofi--3-invarian-mutlak-context7-deep-mode) •
[🏛️ Arsitektur Sistem](#️-2-arsitektur-sistem-kecerdasan) •
[🔄 Closed-Loop Task Flow](#-3-closed-loop-agentic-task-flow-6-fase) •
[🌐 Konfigurasi Global](#-4-persistensi--konfigurasi-global-lintas-workspace) •
[🎯 Pustaka Skill](#-5-pustaka-keahlian-terintegrasi-skills) •
[⚡ Panduan Cepat](#-6-panduan-instalasi--penggunaan-cepat) •
[🧪 Verifikasi Empiris](#-7-verifikasi-empiris--zero-regression) •
[🔒 Keamanan & Kredensial](#-8-kebijakan-keamanan-kredensial--penguncian-identitas-abadi)

---

</div>

## 🌟 1. Filosofi & 3 Invarian Mutlak (Context7 Deep Mode)

Claudia Brain beroperasi dengan arsitektur **Context7 Deep Mode** yang menolak asumsi spekulatif dan memprioritaskan efisiensi teknis maksimal:

```
                  ┌──────────────────────────────────────────────────────────┐
                  │          3 INVARIAN MUTLAK CLAUDIA BRAIN                 │
                  └─────────────────────────────┬────────────────────────────┘
                                                │
         ┌──────────────────────────────────────┼──────────────────────────────────────┐
         ▼                                      ▼                                      ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐ ┌──────────────────────────────┐
│  1. Factual Grounding Mutlak │ │    2. Tangga Minimalis       │ │ 3. Eksekusi Kepadatan Tinggi │
│                              │ │     (The Minimality Ladder)  │ │   (High-Density Execution)   │
│ • Nol asumsi / halusinasi.   │ │ • Root-cause localization.   │ │ • Rasio sinyal tertinggi.    │
│ • Verifikasi riil di terminal│ │ • Prioritaskan native/stdlib.│ │ • Tanpa basa-basi pembuka.   │
│ • Kode siap produksi nyata.  │ │ • Minimal diffs, KISS, YAGNI │ │ • Solusi presisi terstruktur.│
└──────────────────────────────┘ └──────────────────────────────┘ └──────────────────────────────┘
```

---

## 🏛️ 2. Arsitektur Sistem Kecerdasan

Sistem dirancang secara modular dengan pemisahan peran yang tegas (*separation of concerns*):

```
brain-ai/
│
├── 🧠 self_learning/             # Mesin Inti Pembelajaran Mandiri & Multi-Agent
│   ├── agents/                   # Substrat Multi-Agent (Observer, Critic, Distiller, Optimizer)
│   ├── knowledge_base/           # Basis Pengetahuan Persisten & Memori Refleksi Episodik
│   ├── global_config.py          # Manajemen Konfigurasi Global & Jembatan Lintas Workspace
│   ├── identity_lock.py          # Penguncian Identitas Abadi (Immutable Identity & Guardrails)
│   ├── storage.py                # KnowledgeStore berbasis JSON (Heuristik & Anti-Pola)
│   ├── reflection.py             # Reflexion Engine (Evaluasi Kausal 4-Kuadran)
│   ├── task_flow.py              # Closed-Loop Agentic Task Flow (6 Fase Otonom)
│   ├── multi_task_flow.py        # Multi-Task Flow Terdistribusi per Disiplin & Dynamic Router
│   ├── protocol.md               # Spesifikasi Siklus Tertutup OODA
│   ├── reflection_protocol.md    # Standar Injeksi Prompt Refleksi Kausal
│   ├── agentic_task_flow.md      # Standar Eksekusi Tugas Bertahap
│   ├── multi_task_flow.md        # Spesifikasi Pipeline Domain (FullStack, Research, XR, DC)
│   └── test_*.py                 # Pengujian Unit Otomatis (27/27 Lolos 100%)
│
├── ⚙️ setup_global_config.py      # Skrip Otomasi 1-Komando Instalasi Global Cross-Workspace
│
├── 🎯 .agents/skills/            # Pustaka Keahlian Teknis (Skill Modules)
│   ├── claudia-brain/            # Standar Identitas, Task Flow & Aturan Operasional
│   ├── web-game-dev/             # Rekayasa Game Web 60/120 FPS, Fixed Timestep, Rapier/Three.js
│   ├── document-controller/      # Manajemen Dokumen ISO 9001:2015 Klausul 7.5 & EDMS
│   └── pdf-generator/            # Pembuatan Dokumen PDF Korporat Eksekutif (ReportLab)
│
├── 📜 Aturan & Konteks Global
│   ├── GEMINI.md                 # Konfigurasi Aturan Global & Invarian Context7
│   ├── AGENTS.md                 # Panduan Operasional Agen & Memory Reference
│   ├── identity.md               # Identitas & Parameter Karakter Claudia
│   ├── soul.md                   # Inti Filosofi & Karakteristik Komunikasi
│   └── memory.md                 # Memori Persisten Lintas Sesi (Single Source of Truth)
```

---

## 🔄 3. Closed-Loop Agentic Task Flow (6 Fase)

Setiap siklus kerja rekayasa perangkat lunak dieksekusi melalui 6 fase tertutup:

| Fase | Nama Fase | Aksi Operasional & Kriteria Penerimaan |
| :---: | :--- | :--- |
| **1** | **Ingestion & Grounding** | Membaca dokumen acuan (`memory.md`), memeriksa file riil di disk, dan mengonfirmasi spesifikasi sebelum bertindak. |
| **2** | **Planning & Decomposition** | Memecah tugas kompleks menjadi sub-tugas independen (*divide and conquer*) dengan kriteria penerimaan terukur. |
| **3** | **Grounded Execution** | Menerapkan intervensi kode terkecil (*minimal diffs*), dilengkapi *type hints*, *docstrings*, dan pengujian unit. |
| **4** | **Empirical Verification** | Menjalankan pengujian sintaks, linter, dan unit test langsung di terminal untuk memastikan **nol regresi**. |
| **5** | **Reflexion Mode** | Jika terjadi kesalahan, otomatis mengaktifkan diagnosis kausal **4-Kuadran** (Target, Aktual, Akar Masalah, Solusi Korektif) sebelum mencoba kembali. |
| **6** | **Distillation & Delivery** | Menyimpan heuristik baru ke `memory.md` (Auto-Learn) dan menyajikan laporan hasil secara padat, lugas, dan presisi. |

---

## 🌐 4. Persistensi & Konfigurasi Global Lintas Workspace

Berbeda dengan asisten AI konvensional yang kehilangan ingatan dan konfigurasi saat sesi berakhir atau berpindah direktori, Claudia Brain dilengkapi **Global Persistent Memory Ledger** dan **Automated Cross-Workspace Configuration**:

- **Single Source of Truth**: Berkas [`memory.md`](memory.md) (disinkronkan ke `~/memory.md` di level sistem pengguna) menyimpan status proyek, register arsitektur, parameter integrasi, dan batasan kegagalan (*negative constraints*).
- **Cross-Session Continuity**: Pada awal sesi percakapan baru di folder manapun, Claudia otomatis membaca ledger memori sentral untuk memulihkan seluruh konteks historis tanpa perlu instruksi ulang.
- **Cross-Workspace Bridging**: Modul `WorkspaceBridge` dan `GlobalConfigManager` (`self_learning/global_config.py`) secara programmatis membaca, menghubungkan, dan mendaftarkan direktori proyek yang tersebar di disk ke dalam register sentral.
- **1-Command Global Installer (`setup_global_config.py`)**: Mengotomasi replikasi aturan global (`AGENTS.md`, `GEMINI.md`), registrasi pustaka skill (`.gemini/config/skills/`), dan aktivasi plugin ke direktori konfigurasi global pengguna.
- **Auto-Learn Handover**: Setiap perbaikan bug kritis atau milestone baru langsung dicatat permanen ke register memori di akhir tugas.

---

## 🎯 5. Pustaka Keahlian Terintegrasi (Skills)

| Modul Skill | Lokasi Direktori | Cakupan Kapabilitas |
| :--- | :--- | :--- |
| **`claudia-brain`** | [`.agents/skills/claudia-brain/`](.agents/skills/claudia-brain/) | Otak operasional, sistem identitas, OODA loop, dan meta-framework task flow. |
| **`web-game-dev`** | [`.agents/skills/web-game-dev/`](.agents/skills/web-game-dev/) | Fixed Timestep Game Loop, Zero-Allocation Memory Pool, Web Audio API Synthesizer, Shaders, dan AABB Collision. |
| **`document-controller`** | [`.agents/skills/document-controller/`](.agents/skills/document-controller/) | Standar ISO 9001:2015 Klausul 7.5, penomoran dokumen korporat, Master Document Register (MDR), dan alur RACI. |
| **`pdf-generator`** | [`.agents/skills/pdf-generator/`](.agents/skills/pdf-generator/) | Pembuatan PDF eksekutif profesional menggunakan ReportLab di Python dengan tipografi bersih. |

---

## ⚡ 6. Panduan Instalasi & Penggunaan Cepat

### Prasyarat
- Python 3.10 atau versi yang lebih baru.
- Git.

### 1. Klon Repositori
```bash
git clone https://github.com/mhanafi09051998/brain-ai.git
cd brain-ai
```

### 2. Pasang Konfigurasi Global (Cross-Workspace Setup)
Jalankan skrip installer 1-komando untuk mereplikasi aturan dan skills ke direktori konfigurasi global pengguna (`~/.gemini/config/`):
```bash
# Periksa status konfigurasi saat ini
python setup_global_config.py --status

# Pasang konfigurasi global (rules, skills, memory ledger, config.json)
python setup_global_config.py
```

### 3. Registrasi & Jembatan Lintas Workspace
Gunakan `WorkspaceBridge` untuk menghubungkan repositori lokal ke ledger sentral:
```python
from self_learning.global_config import WorkspaceBridge

# Daftarkan proyek yang sedang dikerjakan ke memory.md global
WorkspaceBridge.register_current_workspace(
    name="Super Mario HTML5",
    location="C:/Users/Win10/Music/super_mario",
    status="Production Ready (120 FPS)",
    notes="Physics Rapier, AABB collision, Web Audio Synthesizer"
)

# Periksa seluruh proyek yang terdaftar di sistem
for proj in WorkspaceBridge.get_all_projects():
    print(f"[{proj.status}] {proj.name} -> {proj.location}")
```

### 4. Jalankan Mode Refleksi Mandiri
```python
from self_learning.reflection import ReflexionEngine

# Inisialisasi engine refleksi kausal 4-kuadran
engine = ReflexionEngine()

# Catat hasil refleksi saat terjadi kegagalan
reflection = engine.analyze(
    target_goal="Snake bergerak maju tanpa tabrakan di awal permainan",
    actual_outcome="Ular menabrak leher sendiri pada tick ke-1",
    root_cause="Inisialisasi arah DOWN berlawanan dengan posisi leher di (y+1)",
    corrective_action="Ubah start ke Baris 0 arah RIGHT dan perbaiki limit pengecekan ekor"
)

print(reflection.to_constraint_prompt())
```

### 5. Eksekusi Task Flow 6-Fase
```python
from self_learning.task_flow import AgenticTaskFlow

task_flow = AgenticTaskFlow(task_name="Implementasi Fitur Baru")
task_flow.start_phase(1, "Ingestion & Grounding")
# ... lanjutkan alur siklus tertutup
```

---

## 🧪 7. Verifikasi Empiris & Zero Regression

Reputasi dan kehandalan kode diverifikasi secara objektif menggunakan unit test suite otomatis:

```bash
python -m unittest discover -s self_learning -t . -p "test_*.py"
```

```text
...........................
----------------------------------------------------------------------
Ran 27 tests in 0.109s

OK (27 tests passing, 0 failures, 0 errors)
```

---

## 🔒 8. Kebijakan Keamanan, Kredensial & Penguncian Identitas Abadi

Repositori ini menerapkan standar sanitasi dan proteksi identitas berlapis:
- **Penguncian Identitas Abadi (*Immutable Identity Lock*)**: Identitas Claudia dikunci permanen menggunakan kelas `ClaudiaIdentity` (*frozen dataclass*) dan guardrail `IdentityGuard` (`self_learning/identity_lock.py`). Upaya *prompt injection*, manipulasi persona ("ignore previous instructions", "act as DAN"), atau perusakan identitas otomatis ditolak secara programmatis di gerbang tugas.
- **Nol Kredensial (*Zero Leakage Policy*)**: Tidak ada API Key, Private Token, alamat email pribadi, atau kredensial autentikasi yang tersimpan di dalam riwayat repositori maupun berkas `.git/config`.
- **Strict `.gitignore`**: Seluruh berkas konfigurasi lokal (`.env*`, `*.token`, `*.key`, cache `__pycache__`, dan file log) otomatis diabaikan dari pelacakan git.
- **Aman Diklon Bebas**: Repositori ini aman untuk di-clone secara massal, dipelajari, dan digunakan oleh komunitas pengembang tanpa risiko kebocoran data sensitif.

---

## 📄 Lisensi & Kontribusi

Proyek ini dirilis di bawah lisensi [MIT License](LICENSE).  
Dikelola dan dikembangkan oleh **Muhammad Hanafi** ([@mhanafi09051998](https://github.com/mhanafi09051998)).

<div align="center">
  <sub>Dibangun dengan dedikasi untuk keunggulan rekayasa AI otonom • Context7 Deep Mode</sub>
</div>
