# 🤖 Claudia — Autonomous Fullstack Engineer & Partner

> **Autonomous Engineering Partner & Senior Fullstack Developer**  
> Developed for high-performance, minimal-overhead digital infrastructure.

---

## 🌟 Core Philosophy: The Minimality Ladder (Ponytail)
Claudia menganut prinsip rekayasa perangkat lunak efisien: *"Kode terbaik adalah kode yang tidak perlu ditulis."*

1. **YAGNI**: Apakah fitur ini benar-benar dibutuhkan?
2. **Reuse**: Gunakan pola dan helper yang sudah ada di basis kode.
3. **Standard Library**: Gunakan modul bawaan bahasa sebelum menambah dependensi.
4. **Native Platform**: Manfaatkan fitur native OS / platform.
5. **Shortest Working Diff**: Kode minimal, zero-bloat, dan maksimal 300 baris per file.

---

## 🧠 Arsitektur Memori & Pengetahuan

```
Agent_Claudia_Autonomus/
├── .agents/skills/            # Kumpulan skill otonom (Ponytail, Graphify, Audit)
├── memory/                    # Jaringan memori sistem terdistribusi
│   └── neurons/               # Aturan UI/UX, Profil, dan Arsitektur
├── learning/                  # Sistem pembelajaran mandiri & checkpoint
│   └── neurons/               # Catatan refleksi dan evolusi teknis
├── toolkit/                   # Persenjataan Fullstack modern (Biome, Playwright, Drizzle, Zod, Hono)
├── scripts/                   # Utilitas otomasi server & pipeline
├── .env.example               # Template variabel lingkungan aman
├── AGENTS.md                  # Definisi persona dan aturan kerja utama
└── GEMINI.md                  # Konfigurasi integrasi model AI
```

---

## 🛠️ Persenjataan Fullstack yang Terpasang

- **Linter & Formatter**: `@biomejs/biome` (Rust-based, 35x lebih cepat).
- **Automated Testing**: `playwright` (Chromium Headless E2E visual tester).
- **Web API Engine**: `hono` (Framework mikro sub-15KB).
- **Input Validation**: `zod` (Validasi skema runtime di batas input).
- **Database ORM**: `drizzle-orm` + `better-sqlite3` (SQLite WAL mode).
- **Browser Automation**: `puppeteer` (Rendering PDF & scraping dinamis).
- **Knowledge Graph**: `graphify` (AST code mapper & community clustering).

---

## 🔒 Standar Keamanan & Manajemen Kredensial

Repository ini dikonfigurasi dengan standar isolasi kredensial ketat:
* Seluruh kunci API, password, dan token rahasia dikelola secara terisolasi via `.env` dan `credentials.json` (tercantum dalam `.gitignore`).
* Sebelum mengeksekusi dependensi baru, audit keamanan dilakukan melalui filter skrip `postinstall` dan analisis statis.

---

## 🚀 Memulai (Quick Start)

1. Salin template konfigurasi:
   ```bash
   cp .env.example .env
   ```
2. Isi kredensial server dan API key yang diperlukan di `.env`.
3. Jalankan pembaruan Knowledge Graph:
   ```bash
   python -m graphify update .
   ```
