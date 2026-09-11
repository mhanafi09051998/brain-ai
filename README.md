# ⚡ CLAUDIA ULTRA
### *Autonomous High-Precision Software Architect & Quantitative Intelligence Hub*

[![Architecture](https://img.shields.io/badge/Architecture-Context7%20Deep%20Mode-7c3aed.svg?style=for-the-badge&logo=cpu)](https://github.com/mhanafi09051998/claudia-ultra)
[![Intelligence Core](https://img.shields.io/badge/Brain-Claudia%20Brain%20AI%20Integrated-8A2BE2.svg?style=for-the-badge)](https://github.com/mhanafi09051998/brain-ai)
[![Test Suite](https://img.shields.io/badge/Tests-70%2F70%20Passing%20(100%25)-success?style=for-the-badge&logo=pytest&logoColor=white)](https://github.com/mhanafi09051998/claudia-ultra)
[![Skills Matrix](https://img.shields.io/badge/Skills-26%20Core%20Domains-blue.svg?style=for-the-badge)](skills/README.md)
[![Security](https://img.shields.io/badge/Security-Zero--Trust%20Isolated-ef4444.svg?style=for-the-badge&logo=shield)](https://github.com/mhanafi09051998/claudia-ultra)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

<p align="center">
  <b>Pusat Arsitektur & Sistem Kecerdasan Otonom Claudia</b> yang menyatukan mesin penalaran mandiri siklus tertutup (<i>Closed-Loop Reflexion & OODA Task Flow</i>), protokol operasional agen kelas produksi (paritas Claude Code), penilaian risiko aksi <i>ActionGuard</i>, dengan katalog rekayasa sistem berkinerja tinggi, trading kuantitatif, analisis on-chain, otomasi dokumen ISO 9001, dan kontrol infrastruktur jaringan.
</p>

---

[📖 Filosofi Inti](#-1-filosofi-rekayasa-inti--3-invarian-mutlak) •
[🏛️ Arsitektur Sistem](#️-2-arsitektur-sistem-kecerdasan-terpadu) •
[🔄 Closed-Loop Task Flow](#-3-closed-loop-agentic-task-flow-6-fase) •
[🛡️ Operational Protocol & ActionGuard](#31-protokol-operasional-agen-paritas-claude-code--actionguard) •
[🔍 Reflexion Engine](#-4-reflexion-engine-4-kuadran) •
[🎯 26 Skills Matrix](#-5-matriks-26-keahlian-rekayasa-skills) •
[🌐 Memori Global](#-6-persistensi-memori-global--cross-workspace) •
[🧪 Verifikasi Empiris](#-7-verifikasi-empiris--zero-regression) •
[🔒 Keamanan & Identitas](#-8-penguncian-identitas-abadi--keamanan-kredensial)

---

## 🌌 1. Filosofi Rekayasa Inti & 3 Invarian Mutlak

Claudia beroperasi di bawah filosofi **Context7 Deep Mode** yang menolak spekulasi dan tambal sulam di permukaan:

```
                 ▲
                / \     [6] Tulis kode minimal yang bekerja (Minimum Working Code)
               /---\    [5] Buat menjadi satu baris ekspresif jika memungkinkan
              /-----\   [4] Manfaatkan dependensi yang sudah terinstal
             /-------\  [3] Gunakan fitur bawaan platform & Standard Library
            /---------\ [2] Gunakan kembali utilitas yang sudah ada di codebase
           /-----------\[1] YAGNI: Apakah fitur/kode ini benar-benar perlu ada?
          ─────────────────
                 The Minimality Ladder
```

### 3 Invarian Mutlak:
1. **Kebenaran Faktual Mutlak (*Zero Hallucination*)**: Nol spekulasi. Semua klaim status, performa, atau keberhasilan harus didukung bukti eksekusi langsung di terminal atau inspeksi berkas riil di disk.
2. **Tangga Minimalis (*The Minimality Ladder & Minimal Diff*)**: Hanya mengubah bagian yang rusak atau secara eksplisit diminta. Tidak ada refactoring liar atau abstraksi spekulatif.
3. **Eksekusi Kepadatan Tinggi (*High-Density Execution*)**: Rasio sinyal tertinggi, tanpa basa-basi pengantar klise, langsung pada implementasi teknis siap produksi.

---

## 🏛️ 2. Arsitektur Sistem Kecerdasan Terpadu

```
claudia-ultra/
│
├── 🧠 self_learning/             # Mesin Inti Pembelajaran Mandiri & Multi-Agent (stdlib murni)
│   ├── agents/                   # Substrat Multi-Agent (Observer, Critic, Distiller, Optimizer)
│   ├── engine.py                 # SelfLearningEngine: orkestrasi Observe → Critique → Distill → Optimize
│   ├── knowledge_base/           # Store runtime (learned_patterns.json & reflections.json, tidak dilacak git)
│   ├── global_config.py          # Manajemen Konfigurasi Global & Jembatan Lintas Workspace
│   ├── identity_lock.py          # Penguncian Identitas Abadi (ClaudiaIdentity & IdentityGuard)
│   ├── operational_guard.py      # ActionGuard: klasifikasi risiko aksi (SAFE/REVERSIBLE/OUTWARD/IRREVERSIBLE) & persetujuan per-aksi
│   ├── operational_protocol.md   # Protokol Operasional Agen (paritas Claude Code, aturan OP-x.y)
│   ├── storage.py                # KnowledgeStore berbasis JSON (penulisan atomik, toleran berkas rusak)
│   ├── reflection.py             # Reflexion Engine (Evaluasi Kausal 4-Kuadran)
│   ├── task_flow.py              # Closed-Loop Agentic Task Flow (6 Fase Otonom)
│   ├── multi_task_flow.py        # Multi-Task Flow Terdistribusi per Disiplin & Dynamic Router
│   ├── benchmark.py              # Benchmarking Latensi & Pass Rate
│   ├── protocol.md               # Spesifikasi Siklus Tertutup OODA
│   ├── reflection_protocol.md    # Standar Refleksi Verbal Kausal
│   ├── agentic_task_flow.md      # Standar Eksekusi Tugas Bertahap
│   ├── multi_task_flow.md        # Spesifikasi Pipeline Domain Spesifik
│   └── test_*.py                 # Unit Test Suite Otomatis (70/70 Passing 100%)
│
├── 🎯 skills/                    # Katalog 26 Modul Keahlian Rekayasa Sistem (lihat skills/README.md)
│   ├── claudia-brain/            # Standar Identitas, Task Flow & Aturan Operasional (OP-1 s/d OP-12)
│   ├── document-controller/      # Manajemen Dokumen ISO 9001:2015 Klausul 7.5 & EDMS
│   ├── pdf-generator/            # Dokumen PDF Eksekutif Korporat (ReportLab, Astra & Fable)
│   ├── web-game-dev/             # Game Web 60/120 FPS, Fixed Timestep, Rapier/Three.js
│   ├── nextjs-tailwind-ui/       # App Router, Turbopack, Glassmorphism, Dark-First
│   ├── mikrotik-routeros-engineering/ # RouterOS v7, Mangle, Multi-WAN PCC, WireGuard
│   ├── meteora-dlmm-automated-market-making/ # Math Bin DLMM, Fee Volatility Accumulator
│   ├── solana-fast-trading-bot-architecture/ # Geyser gRPC Streams, Jito Block Engine 0-MEV
│   └── ... (Total 26 Core Skills)
│
├── 📜 playbooks/                 # Playbook Rekayasa Produksi Teruji
│   └── solana-second-wave-trading-engine/ # Engine Trading Real-Time Solana
│
├── ⚙️ scripts/                    # Skrip Otomasi Sistem & Sinkronisasi
│   └── auto_git_sync.js          # Silent Daemon Sinkronisasi Git Otomatis ke origin main
│
├── ⚙️ setup_global_config.py      # Skrip Otomasi 1-Komando Instalasi Global Cross-Workspace (--status/--dry-run/--uninstall)
├── 📦 pyproject.toml              # Metadata paket Python (PEP 621, Python >= 3.10, zero runtime deps)
├── 🤖 .github/workflows/ci.yml    # CI: compileall + 70 tests + benchmark + installer dry-run
├── 📜 AGENTS.md                  # Panduan Utama Arsitektur Agen & Invarian Sistem
├── 📜 GEMINI.md                  # Cermin Aturan Workspace untuk Engine Gemini & Antigravity
├── 📜 identity.md                # Identitas Resmi & Klausul Anti-Tampering
├── 📜 soul.md                    # Karakteristik Inti & Gaya Komunikasi Claudia
└── 📜 memory.md                  # Global Persistent Memory Ledger (Single Source of Truth)
```

---

## 🔄 3. Closed-Loop Agentic Task Flow (6 Fase)

Setiap siklus kerja rekayasa dieksekusi melalui 6 fase tertutup dengan penjagaan ketat (*phase gates*):

| Fase | Nama Fase | Aksi Operasional & Kriteria Penerimaan | Gate Invariant |
| :---: | :--- | :--- | :--- |
| **1** | **Ingestion & Grounding** | Membaca dokumen acuan (`memory.md`), memeriksa file riil di disk, dan mengonfirmasi spesifikasi sebelum bertindak. | OP-1.1, OP-1.2, OP-1.5, OP-8.4 |
| **2** | **Planning & Decomposition** | Memecah tugas kompleks menjadi sub-tugas independen (*divide and conquer*) dengan kriteria terukur. | OP-2.1 – OP-2.5 |
| **3** | **Grounded Execution** | Menerapkan intervensi kode terkecil (*minimal diffs*), dilengkapi *type hints*, *docstrings*, dan pengujian unit. | OP-3.1 – OP-3.6, ActionGuard (OP-5.x) |
| **4** | **Empirical Verification** | Menjalankan pengujian sintaks, linter, dan unit test langsung di terminal untuk memastikan **nol regresi**. | OP-4.1, OP-4.6, OP-1.7 |
| **5** | **Reflexion Mode** | Jika terjadi kesalahan, otomatis mengaktifkan diagnosis kausal **4-Kuadran** sebelum mencoba kembali. | OP-4.2, OP-6.1 – OP-6.4 |
| **6** | **Distillation & Delivery** | Menyimpan heuristik baru ke `memory.md` (Auto-Learn) dan menyajikan laporan hasil secara padat dan presisi. | OP-4.3 – OP-4.5, OP-7.1 – OP-7.6 |

### 3.1 Protokol Operasional Agen (Paritas Claude Code) & ActionGuard

Setiap fase dijaga oleh aturan berkode `OP-x.y` ([`self_learning/operational_protocol.md`](self_learning/operational_protocol.md)) yang dapat diaudit secara mekanis menggunakan [`self_learning/operational_guard.py`](self_learning/operational_guard.py):

```python
from self_learning import ActionGuard, ApprovalRegistry, ConfirmationRequiredError, RiskLevel

# 1. Klasifikasi risiko aksi otomatis
ActionGuard.assess("git status").risk                      # RiskLevel.SAFE
ActionGuard.assess("git commit -m fix").risk               # RiskLevel.REVERSIBLE
ActionGuard.assess("git push origin main").risk            # RiskLevel.OUTWARD      -> Butuh persetujuan
ActionGuard.assess("git reset --hard HEAD~1").risk         # RiskLevel.IRREVERSIBLE -> Butuh persetujuan

# 2. Persetujuan per-aksi sekali pakai (OP-5.1)
approvals = ApprovalRegistry()
approvals.grant("git push origin main")
ActionGuard.enforce("git push origin main", approvals)     # Lolos, token izin dikonsumsi
# Percobaan eksekusi kedua tanpa izin baru otomatis ditolak:
# ActionGuard.enforce("git push origin main", approvals)   -> ConfirmationRequiredError
```

---

## 🔍 4. Reflexion Engine (4-Kuadran)

Saat menghadapi kegagalan atau error pengujian, Claudia mengaktifkan **Reflexion Engine** (`self_learning/reflection.py`):
1. **Kuadran 1 - Target Nyata (*Intended Goal*)**: Perilaku sistem atau output yang diharapkan.
2. **Kuadran 2 - Kondisi Aktual (*Actual Outcome & Trace*)**: Pesan error nyata atau hasil menyimpang.
3. **Kuadran 3 - Akar Permasalahan (*Root Cause Diagnosis*)**: Diagnosis ilmiah mengapa asumsi sebelumnya keliru.
4. **Kuadran 4 - Tindakan Korektif (*Actionable Constraint*)**: Invarian baru yang disuntikkan ke dalam percobaan berikutnya.

---

## 🎯 5. Matriks 26 Keahlian Rekayasa (Skills)

Katalog keahlian teknis tingkat produksi tersusun di direktori [`skills/`](skills/README.md):
- **Kecerdasan & Meta**: `claudia-brain`, `algorithms`, `clean-architecture-minimalism`, `incident-root-cause-debugging`.
- **Dokumen & Korporat**: `document-controller` (ISO 9001:2015 Klausul 7.5), `pdf-generator` (Astra & Fable ReportLab), `herbacore-document-automation`.
- **Frontend & Grafis**: `nextjs-tailwind-ui` (App Router, Turbopack, Dark Glassmorphism), `web-game-dev` (Fixed Timestep 60/120 FPS, Rapier/Three.js).
- **Backend & Jaringan**: `api-gateway-reverse-proxy`, `database-engineering`, `distributed-systems`, `mikrotik-routeros-engineering`, `telegram-bot-architecture`.
- **Infrastruktur & Hardening**: `devops-linux-hardening`, `linux-performance-profiling`, `linux-server-architecture`, `security-owasp-hardening`.
- **Bahasa Performa Tinggi**: `python-high-throughput`, `rust-systems-programming`, `typescript-type-gymnastics`.
- **Trading Kuantitatif & DeFi**: `meteora-dlmm-automated-market-making`, `quantitative-market-making`, `solana-defi-engineering`, `solana-fast-trading-bot-architecture`, `solana-onchain-forensics-token-audit`.

---

## 🌐 6. Persistensi Memori Global & Cross-Workspace

Claudia Ultra mempertahankan ingatan dan konteks lintas sesi dan direktori kerja:
- **Central Memory Ledger (`memory.md`)**: Menyimpan status proyek aktif, register keputusan arsitektur, dan batasan negatif.
- **Cross-Workspace Bridge (`self_learning/global_config.py`)**: Menghubungkan direktori kerja terdistribusi ke dalam konfigurasi sentral pengguna (`~/.gemini/config/`).
- **1-Command Global Installer**:
  ```bash
  # Cek status konfigurasi
  python setup_global_config.py --status

  # Pasang konfigurasi global (rules, 26 skills, memory ledger, config.json)
  python setup_global_config.py
  ```

---

## 🧪 7. Verifikasi Empiris & Zero Regression

Integritas kode diuji secara otomatis dan deterministik menggunakan 70 unit test suite terisolasi (nol modifikasi pada direktori pengguna saat pengujian):
```bash
python -m unittest discover -s self_learning -t . -p "test_*.py"
```
```text
......................................................................
----------------------------------------------------------------------
Ran 70 tests in 0.160s

OK (70 tests passing, 0 failures, 0 errors)
```

| Berkas Test | Cakupan & Fokus Pengujian |
| :--- | :--- |
| `test_self_learning.py` | KnowledgeStore (CRUD, penulisan atomik, toleransi berkas rusak), Observer, Critic, Distiller, Optimizer, Engine |
| `test_reflection.py` | Rubrik 4-kuadran, memori episodik, diagnosis kausal, self-healing & exhaust |
| `test_task_flow.py` | Pipeline 6-fase: sukses, retry-dengan-refleksi, diagnosis exception, anti-pola saat gagal total |
| `test_multi_task_flow.py` | 4 pipeline domain terdistribusi, routing berbatas kata, flow dinamis idempoten |
| `test_identity_lock.py` | Immutable identity, deteksi tampering, gerbang task flow |
| `test_operational_guard.py` | Klasifikasi risiko 4 tingkat (shell, PowerShell, git, SQL, docker, cloud), perintah majemuk, persetujuan per-aksi sekali pakai |
| `test_global_config.py` | Parsing & registrasi ledger (`memory.md`), WorkspaceBridge |
| `test_setup_global_config.py` | Installer 1-komando: dry-run, idempoten, preservasi config pengguna, uninstall, CLI |

---

## 🔒 8. Penguncian Identitas Abadi, ActionGuard & Keamanan Kredensial

- **Immutable Identity Lock**: Identitas resmi sebagai Claudia dikunci menggunakan kelas beku `ClaudiaIdentity` (*frozen dataclass*) dan guardrail `IdentityGuard` (`self_learning/identity_lock.py`). Segala upaya prompt injection atau penggantian persona otomatis ditolak di gerbang instruksi.
- **ActionGuard Risk Engine**: Menilai setiap perintah sebelum dieksekusi. Perintah kategori **OUTWARD** (push remote, publish registry, mutasi ssh) dan **IRREVERSIBLE** (rm -rf, git reset --hard, DROP TABLE) wajib mengantongi izin eksplisit per-aksi dan sekali pakai (`ApprovalRegistry`).
- **Zero Leakage Invariant**: Steril dari private key, API token, password, atau credential sensitif dalam commit git.
- **Autonomous Git Sync Invariant**: Perubahan pada arsitektur atau skill otomatis dicatat, diuji, dan disinkronkan ke repositori utama (`origin main`) tanpa menunggu prompt pengguna.

---

<div align="center">
  <sub>Dikelola oleh <b>Muhammad Hanafi</b> (<a href="https://github.com/mhanafi09051998">@mhanafi09051998</a>) • Context7 Deep Mode</sub>
</div>
