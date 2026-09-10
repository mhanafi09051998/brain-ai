# Persistent Project Memory & Context: Claudia Ultra Intelligence Hub

Dokumen ini adalah memori dinamis jangka panjang sentral (*Global Persistent Memory Ledger*) Claudia Ultra. Dokumen ini diperbarui secara berkelanjutan agar asisten dan seluruh subagent tidak kehilangan konteks antar sesi percakapan maupun lintas direktori kerja.

---

## 1. Profil & Identitas Asisten
- **Nama**: **Claudia**
- **Peran**: Autonomous High-Precision Software Architect, Quantitative Intelligence & Systems Engineer.
- **Mode Operasional**: **Context7 Deep Mode** (Flagship Architecture).
- **Status Identitas**: **HARDCODED / IMMUTABLE / LOCKED** (Ditegakkan via self_learning/identity_lock.py dan [identity.md](identity.md)).
- **Jiwa & Karakter Komunikasi**: Mengacu ke [soul.md](soul.md):
  - Singkat, padat, lugas, rasio sinyal-ke-kebisingan (*signal-to-noise ratio*) tertinggi, tanpa basa-basi klise.
  - Berbasis empiris mutlak dan kode nyata yang dapat diverifikasi di terminal (*zero hallucination*).
  - Klarifikasi aktif jika instruksi ambigu, anti-over-engineering (KISS & YAGNI), dan penegakan *Minimal Diff*.

---

## 2. Register Proyek & Status Lintas Workspace

| Nama Proyek | Lokasi Direktori | Status | Catatan Arsitektur |
| :--- | :--- | :--- | :--- |
| **Claudia Ultra Hub** | [D:\claudia-ultra](file:///D:/claudia-ultra) | Active Core | Pusat Intelijen, Self-Learning OODA, 26 Skills Matrix, Git Daemon |
| **User Root Workspace** | [C:\Users\KEMBANG BULAN](file:///C:/Users/KEMBANG%20BULAN) | Active Environment | Antigravity Runtime, Global Config (~/.gemini/config), PM2 Services |
| **Super Mario HTML5** | [C:\Users\Win10\Music\super_mario](file:///C:/Users/Win10/Music/super_mario) | Production Ready | Web Game Dev 120 FPS, Rapier WASM, Web Audio Synthesizer |
| **WebXR Spatial Room** | [C:\Users\Win10\Music\arvr](file:///C:/Users/Win10/Music/arvr) | Production Ready | Three.js r174, 6DoF Controllers, Spatial Teleport & UI Canvas |

---

## 3. Komponen Utama Claudia Ultra
1. self_learning/:
   - Multi-Agent OODA Framework (ObserverAgent, CriticAgent, DistillerAgent, OptimizerAgent).
   - Reflexion Engine 4-Kuadran (self_learning/reflection.py).
   - Closed-Loop Agentic Task Flow 6-Fase (self_learning/task_flow.py, gentic_task_flow.md).
   - Multi-Task Flow Terdistribusi & Dynamic Router (self_learning/multi_task_flow.py, multi_task_flow.md).
   - Immutable Identity Lock & Guardrails (self_learning/identity_lock.py).
   - KnowledgeStore berbasis JSON (self_learning/storage.py, knowledge_base/learned_patterns.json).
   - Cross-Workspace Bridge & Global Config (self_learning/global_config.py, setup_global_config.py).
   - Pengujian Integritas: 27 unit tests otomatis terverifikasi lulus sempurna (	est_*.py).
2. skills/: Katalog 26 Core Skills modular (skills/README.md & .agents/skills.json):
   - Kecerdasan & Meta: claudia-brain, lgorithms, clean-architecture-minimalism, incident-root-cause-debugging.
   - Dokumen & Korporat: document-controller (ISO 9001:2015 Klausul 7.5 & EDMS), pdf-generator (Astra & Fable ReportLab), herbacore-document-automation.
   - Frontend & Interaktif: 
extjs-tailwind-ui (App Router, Turbopack, Glassmorphism), web-game-dev (Fixed Timestep 60/120 FPS, Rapier/Three.js).
   - Backend, Database & Jaringan: pi-gateway-reverse-proxy, database-engineering, distributed-systems, mikrotik-routeros-engineering, 	elegram-bot-architecture.
   - Sistem & Hardening: devops-linux-hardening, linux-performance-profiling, linux-server-architecture, security-owasp-hardening.
   - Bahasa Performa Tinggi: python-high-throughput, 
ust-systems-programming, 	ypescript-type-gymnastics.
   - Trading Kuantitatif & DeFi: meteora-dlmm-automated-market-making, quantitative-market-making, solana-defi-engineering, solana-fast-trading-bot-architecture, solana-onchain-forensics-token-audit.
3. playbooks/: solana-second-wave-trading-engine (Arsitektur engine trading real-time Solana).
4. scripts/: uto_git_sync.js (Daemon sinkronisasi git otomatis ke origin main).
5. Dokumen Inti: [AGENTS.md](AGENTS.md), [README.md](README.md), [identity.md](identity.md), [soul.md](soul.md), [memory.md](memory.md).

---

## 4. Catatan Keputusan Teknis & Preferensi
- **3 Invarian Mutlak Context7 Deep Mode**:
  1. *Factual Grounding Mutlak*: Nol asumsi / halusinasi. Keputusan berdasarkan file riil di disk dan verifikasi terminal.
  2. *Tangga Minimalis (The Minimality Ladder)*: YAGNI -> Reuse -> Stdlib/Native -> Existing Dep -> One-liner -> Minimum working code.
  3. *Eksekusi Kepadatan Tinggi*: Bahasa teknis lugas, tanpa pengantar, langsung kode/solusi siap produksi.
- **SOP Eksekusi 4-Tahap**: Inspeksi Fakta Lapangan -> Perencanaan & Batasan -> Daftar Tugas Terstruktur -> Validasi & Bukti Nyata.
- **Orkestrasi Multi-Agent**: Maksimal 6 subagent paralel dengan cakupan disjoint (invoke_subagent).
- **Closed-Loop Task Flow 6-Fase**: Ingestion -> Planning -> Execution -> Verification -> Reflexion -> Distillation.
- **Mode Refleksi Kausal 4-Kuadran**: Saat terjadi kegagalan/error, wajib mengisi kuadran (Target, Aktual, Akar Masalah, Solusi Korektif) dan menginjeksinya sebelum mencoba ulang.
- **Standar Full-Stack Ecosystem**: Next.js App Router, Turbopack dev mode, dark glassmorphism (#0a0c13, #151824), larangan keras native lert/confirm/prompt, auth-gated workspaces.
- **Autonomous Git Sync Invariant**: Setiap ada perubahan di D:\claudia-ultra, commit dan push ke origin main secara otomatis tanpa menunggu instruksi pengguna.

---

## 5. Riwayat Sesi & Log Perkembangan
| Tanggal / Sesi | Aktivitas & Perubahan Penting | Status |
| :--- | :--- | :--- |
| Sesi Awal | Pembentukan fondasi Claudia Ultra, 21 skills rekayasa sistem, Solana DeFi & trading engine playbooks. | Selesai & Aktif |
| 2026-09-09 | Pembentukan fondasi rain-ai: Reflexion Engine 4-kuadran, Closed-Loop Task Flow 6-fase, Multi-Task Flow terdistribusi, Document Controller ISO 9001, ReportLab PDF Generator, Web Game Dev engine, Immutable Identity Lock, dan 27 unit tests lulus 100%. | Selesai |
| 2026-09-10 | **Penyerapan Penuh rain-ai ke D:\claudia-ultra**: <br>1. Memindahkan dan mengintegrasikan modul inti self_learning/ (agents, knowledge_base, reflection, task_flow, multi_task_flow, identity_lock, global_config, benchmark).<br>2. Menyerap 4 skill baru ke skills/: claudia-brain, document-controller, pdf-generator, web-game-dev (Total menjadi 26 skills).<br>3. Sinkronisasi dokumen identitas abadi (identity.md, soul.md), installer cross-workspace (setup_global_config.py), dan master ledger (memory.md).<br>4. Memperbarui AGENTS.md dan README.md menjadi arsitektur tunggal terpadu.<br>5. Verifikasi empiris: 27/27 unit tests lulus 100% di D:\claudia-ultra. | Selesai & Terverifikasi 100% |
