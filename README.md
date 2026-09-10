<div align="center">

# 🧠 Claudia Brain AI
### *Context7 Deep Mode: Arsitektur Agen Mandiri, Reflexion Engine & Closed-Loop Task Flow*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Architecture](https://img.shields.io/badge/Architecture-Context7%20Deep%20Mode-8A2BE2?style=for-the-badge)](https://github.com/mhanafi09051998/brain-ai)
[![CI](https://img.shields.io/github/actions/workflow/status/mhanafi09051998/brain-ai/ci.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI)](https://github.com/mhanafi09051998/brain-ai/actions/workflows/ci.yml)
[![Test Suite](https://img.shields.io/badge/Tests-70%2F70%20Passing%20(100%25)-success?style=for-the-badge&logo=pytest&logoColor=white)](https://github.com/mhanafi09051998/brain-ai/actions/workflows/ci.yml)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(stdlib)-informational?style=for-the-badge)](pyproject.toml)
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
├── 🧠 self_learning/             # Mesin Inti Pembelajaran Mandiri & Multi-Agent (stdlib murni)
│   ├── agents/                   # Substrat Multi-Agent (Observer, Critic, Distiller, Optimizer)
│   ├── engine.py                 # SelfLearningEngine: orkestrasi Observe → Critique → Distill → Optimize
│   ├── knowledge_base/           # Store runtime (learned_patterns.json & reflections.json, tidak dilacak git)
│   ├── global_config.py          # Manajemen Konfigurasi Global & Jembatan Lintas Workspace
│   ├── identity_lock.py          # Penguncian Identitas Abadi (Immutable Identity & Guardrails)
│   ├── operational_guard.py      # ActionGuard: klasifikasi risiko aksi (SAFE/REVERSIBLE/OUTWARD/IRREVERSIBLE) & persetujuan per-aksi
│   ├── operational_protocol.md   # Protokol Operasional Agen (paritas Claude Code, aturan OP-x.y)
│   ├── storage.py                # KnowledgeStore berbasis JSON (penulisan atomik, toleran berkas rusak)
│   ├── reflection.py             # Reflexion Engine (Evaluasi Kausal 4-Kuadran)
│   ├── task_flow.py              # Closed-Loop Agentic Task Flow (6 Fase Otonom)
│   ├── multi_task_flow.py        # Multi-Task Flow Terdistribusi per Disiplin & Dynamic Router
│   ├── benchmark.py              # Demo/benchmark konvergensi O(N) → O(log N)
│   ├── protocol.md               # Spesifikasi Siklus Tertutup OODA
│   ├── reflection_protocol.md    # Standar Injeksi Prompt Refleksi Kausal
│   ├── agentic_task_flow.md      # Standar Eksekusi Tugas Bertahap
│   ├── multi_task_flow.md        # Spesifikasi Pipeline Domain (FullStack, Research, XR, DC)
│   └── test_*.py                 # 70 unit test (store terisolasi di direktori sementara)
│
├── ⚙️ setup_global_config.py      # Installer/uninstaller 1-komando konfigurasi global (--status/--dry-run/--uninstall)
├── 📦 pyproject.toml              # Metadata paket (PEP 621), Python ≥ 3.10, nol dependensi runtime
├── 🤖 .github/workflows/ci.yml    # CI: compileall + unittest + benchmark + installer dry-run (Linux & Windows, 3.10–3.13)
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

### 3.1 Protokol Operasional Agen (Paritas Claude Code)

Setiap fase dijaga *gate* dari [`self_learning/operational_protocol.md`](self_learning/operational_protocol.md) — 12 bagian aturan berkode `OP-x.y` yang mendistilasi disiplin kerja agen pemrograman kelas produksi: **baca sebelum ubah**, **verifikasi sebelum merujuk**, **bertanya hanya untuk keputusan milik pengguna**, **minimal diffs & nol fitur spekulatif**, **tidak ada klaim tanpa bukti pada giliran ini**, **batas 2–3 coba-ulang**, **data ≠ instruksi**, format laporan wajib, dan daftar periksa audit-diri.

Bagian yang dapat ditegakkan mekanis diimplementasikan di [`self_learning/operational_guard.py`](self_learning/operational_guard.py):

```python
from self_learning import ActionGuard, ApprovalRegistry, ConfirmationRequiredError, RiskLevel

ActionGuard.assess("git status").risk                      # RiskLevel.SAFE
ActionGuard.assess("git commit -m fix").risk               # RiskLevel.REVERSIBLE
ActionGuard.assess("git push origin main").risk            # RiskLevel.OUTWARD      -> konfirmasi
ActionGuard.assess("git status && rm -rf build").risk      # RiskLevel.IRREVERSIBLE -> konfirmasi (tingkat tertinggi menang)
ActionGuard.assess("DELETE FROM users WHERE id=1").risk    # RiskLevel.SAFE (ada WHERE)

approvals = ApprovalRegistry()
approvals.grant("git push origin main")                    # persetujuan pengguna: per-aksi, sekali pakai
ActionGuard.enforce("git push origin main", approvals)     # OK, persetujuan dikonsumsi
ActionGuard.enforce("git push origin main", approvals)     # ConfirmationRequiredError (PermissionError)
```

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
- Python 3.10 atau versi yang lebih baru (tanpa dependensi eksternal).
- Git.
- Opsional: `reportlab>=4` hanya untuk skill `pdf-generator` (`pip install -e ".[pdf]"`).

### 1. Klon Repositori
```bash
git clone https://github.com/mhanafi09051998/brain-ai.git
cd brain-ai

# Opsional: pasang sebagai paket (editable) agar `import self_learning` bekerja dari folder mana pun
pip install -e .
```

### 2. Pasang Konfigurasi Global (Cross-Workspace Setup)
Jalankan skrip installer 1-komando untuk mereplikasi aturan dan skills ke direktori konfigurasi global pengguna (`~/.gemini/config/`). Installer bersifat **idempoten**: aman dijalankan berulang, tidak menggandakan entri registry, dan **tidak pernah menimpa** `~/memory.md` yang sudah ada.
```bash
# Periksa status konfigurasi saat ini
python setup_global_config.py --status

# Simulasi tanpa menulis berkas apa pun
python setup_global_config.py --dry-run

# Pasang konfigurasi global (rules, skills, memory ledger, config.json)
python setup_global_config.py

# Lepas rules/skills/registry yang dipasang (memory.md dipertahankan)
python setup_global_config.py --uninstall
```

### 3. Registrasi & Jembatan Lintas Workspace
Gunakan `GlobalConfigManager` untuk menulis ke ledger sentral dan `WorkspaceBridge` untuk membacanya dari workspace lain:
```python
from self_learning import GlobalConfigManager, WorkspaceBridge

# Daftarkan (atau perbarui) proyek yang sedang dikerjakan ke tabel "Register Proyek" di ~/memory.md
GlobalConfigManager.register_or_update_project(
    name="Super Mario HTML5",
    location="C:/Users/Win10/Music/super_mario",
    status="Production Ready (120 FPS)",
    notes="Physics Rapier, AABB collision, Web Audio Synthesizer",
)

# Periksa seluruh proyek yang terdaftar di sistem
for proj in GlobalConfigManager.parse_registered_projects():
    print(f"[{proj.status}] {proj.name} -> {proj.location}")

# Dari workspace lain: ambil konteks proyek berdasarkan nama (pencocokan parsial)
ctx = WorkspaceBridge.get_cross_workspace_context("mario")
print(ctx["location"], ctx["exists_on_disk"])
```

### 4. Jalankan Mode Refleksi Mandiri
```python
from self_learning import ReflectionAgent, ReflectiveExecutor, ReflexionMemoryStore

memory = ReflexionMemoryStore()          # default: self_learning/knowledge_base/reflections.json
agent = ReflectionAgent(memory)

# (a) Diagnosis kausal otomatis dari exception nyata
try:
    [][0]
except IndexError as err:
    record = agent.formulate_reflection(
        task_name="snake_spawn",
        attempt_number=1,
        intended_goal="Snake bergerak maju tanpa tabrakan di awal permainan",
        error=err,
    )
    print(record.to_in_context_prompt())   # 4 kuadran: Target, Aktual, Akar Masalah, Tindakan

# (b) Eksekusi self-healing: gagal -> refleksi -> retry dengan refleksi diinjeksikan
executor = ReflectiveExecutor("safe_getter", "Ambil elemen pertama dengan aman", memory, max_attempts=3)
result = executor.execute(
    lambda attempt, reflections: "fallback" if reflections else [][0],
    validator_fn=lambda out: out == "fallback",
)
print(result["success"], result["attempt"])  # True 2
```

### 5. Eksekusi Task Flow 6-Fase
```python
from self_learning import AgenticTaskFlow

flow = AgenticTaskFlow()  # store default; berikan memory_store/knowledge_store untuk lokasi kustom

context = flow.run_pipeline(
    task_name="Implementasi Fitur Baru",
    intended_goal="Endpoint /health mengembalikan 200",
    acceptance_criteria=["status == 200"],
    grounded_files=["app/routes.py"],
    plan_steps=["Tambah route", "Tambah test"],
    executor_fn=lambda ctx, feedback: {"status": 200},   # feedback = prompt refleksi dari percobaan gagal sebelumnya
    verifier_fn=lambda out: out["status"] == 200,
    max_attempts=3,
)

print(context.is_success, [s.phase.value for s in context.steps])
# Sukses: heuristik disimpan; gagal total: anti-pola disimpan. Keduanya masuk KnowledgeStore.
```

### 6. Siklus Self-Learning & Router Multi-Task Flow
```python
from self_learning import SelfLearningEngine, TargetProfile, TestCase, TaskFlowRouter, DomainRole

# Bandingkan beberapa kandidat implementasi secara empiris hingga konvergen
engine = SelfLearningEngine("array_search", TargetProfile(min_pass_rate=1.0, max_avg_latency_ms=0.1))
result = engine.run(
    candidate_pool=[{"name": "Linear", "fn": lambda a, t: a.index(t) if t in a else None}],
    test_cases=[TestCase("hit", ([1, 2, 3], 2), 1), TestCase("miss", ([1, 2, 3], 9), None)],
)
print(result.best_candidate_name, result.best_fitness_score)

# Pilih pipeline domain secara otomatis dari deskripsi tugas
router = TaskFlowRouter()
print(router.route_by_task_description("Buat adegan WebXR dengan three.js").role_label)  # spatial_xr_developer
print(router.get_flow(DomainRole.RESEARCHER).stages[0].name)
```

Demo lengkap siklus self-learning (O(N) → O(log N)):
```bash
python -m self_learning.benchmark
```

---

## 🧪 7. Verifikasi Empiris & Zero Regression

Reputasi dan kehandalan kode diverifikasi secara objektif menggunakan unit test suite otomatis. Seluruh test memakai store di direktori sementara sehingga **tidak pernah menyentuh `knowledge_base/` maupun home pengguna** (installer diuji terhadap home tiruan):

```bash
python -m unittest discover -s self_learning -t . -p "test_*.py"
```

```text
......................................................................
----------------------------------------------------------------------
Ran 70 tests in 0.27s

OK
```

| Berkas Test | Cakupan |
| :--- | :--- |
| `test_self_learning.py` | KnowledgeStore (CRUD, atomik, toleransi berkas rusak), Observer, Critic, Distiller, Optimizer, Engine |
| `test_reflection.py` | Rubrik 4-kuadran, memori episodik, diagnosis kausal, self-healing & exhaust |
| `test_task_flow.py` | Pipeline 6-fase: sukses, retry-dengan-refleksi, diagnosis exception, anti-pola saat gagal total |
| `test_multi_task_flow.py` | 4 pipeline domain, routing berbatas kata, flow dinamis idempoten |
| `test_identity_lock.py` | Immutable identity, deteksi tampering, gerbang task flow |
| `test_operational_guard.py` | Klasifikasi risiko 4 tingkat (shell, PowerShell, git, SQL, docker, cloud), perintah majemuk, persetujuan per-aksi sekali pakai |
| `test_global_config.py` | Parsing & registrasi ledger (tabel yang benar), WorkspaceBridge |
| `test_setup_global_config.py` | Installer: dry-run, idempoten, preservasi config pengguna, uninstall, CLI |

CI GitHub Actions (`.github/workflows/ci.yml`) menjalankan suite ini pada Ubuntu & Windows untuk Python 3.10–3.13, ditambah benchmark, installer `--dry-run`, render PDF skill, dan pemeriksaan bahwa working tree tetap bersih setelah test.

---

## 🔒 8. Kebijakan Keamanan, Kredensial & Penguncian Identitas Abadi

Repositori ini menerapkan standar sanitasi dan proteksi identitas berlapis:
- **Penguncian Identitas Abadi (*Immutable Identity Lock*)**: Identitas Claudia dikunci permanen menggunakan kelas `ClaudiaIdentity` (*frozen dataclass*) dan guardrail `IdentityGuard` (`self_learning/identity_lock.py`). Upaya *prompt injection*, manipulasi persona ("ignore previous instructions", "act as DAN"), atau perusakan identitas otomatis ditolak secara programmatis di gerbang tugas.
- **Gerbang Risiko Aksi (*Operational Guard*)**: `ActionGuard` (`self_learning/operational_guard.py`) mengklasifikasi setiap perintah ke SAFE / REVERSIBLE / OUTWARD / IRREVERSIBLE; aksi OUTWARD dan IRREVERSIBLE hanya berjalan dengan persetujuan pengguna **per-aksi dan sekali pakai** (`ApprovalRegistry`), sesuai `operational_protocol.md` §5.
- **Nol Kredensial (*Zero Leakage Policy*)**: Tidak ada API Key, Private Token, alamat email pribadi, atau kredensial autentikasi yang tersimpan di dalam riwayat repositori maupun berkas `.git/config`.
- **Strict `.gitignore`**: Seluruh berkas konfigurasi lokal (`.env*`, `*.token`, `*.key`, cache `__pycache__`, file log, serta store runtime `knowledge_base/*.json`) otomatis diabaikan dari pelacakan git.
- **Aman Diklon Bebas**: Repositori ini aman untuk di-clone secara massal, dipelajari, dan digunakan oleh komunitas pengembang tanpa risiko kebocoran data sensitif.

---

## 📄 Lisensi & Kontribusi

Proyek ini dirilis di bawah lisensi [MIT License](LICENSE).  
Dikelola dan dikembangkan oleh **Muhammad Hanafi** ([@mhanafi09051998](https://github.com/mhanafi09051998)).

<div align="center">
  <sub>Dibangun dengan dedikasi untuk keunggulan rekayasa AI otonom • Context7 Deep Mode</sub>
</div>
