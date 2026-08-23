# 🛠️ Autonomous Fullstack & Security Toolkit

Repositori dan modul alat pengembangan modern yang terpasang dan digunakan oleh Claudia:

---

## 📦 Daftar Modul & Framework

### 1. **Biome (`@biomejs/biome`)** - *Linter & Formatter Rust*
- **Kecepatan**: 35x lebih cepat dari ESLint + Prettier.
- **Fungsi**: Memformat dan memeriksa kode JavaScript/TypeScript seketika tanpa konfigurasi rumit.
- **Penggunaan**: `biome check --apply .` / `biome format --write .`

### 2. **Playwright (`playwright` + Chromium Headless)** - *UI & End-to-End Testing*
- **Fungsi**: Mesin pengujian visual otomatis, simulasi klik/form, screenshot responsive di mobile & desktop.
- **Penggunaan**: `npx playwright test` / `node scripts/test-ui.js`

### 3. **Hono (`hono`)** - *Ultra-Lightweight Edge Web Framework*
- **Fungsi**: Web API framework sub-15KB dengan konsumsi RAM di bawah 10 MB per worker.
- **Penggunaan**: REST API, Webhook receiver, Microservices.

### 4. **Zod (`zod`)** - *Runtime Schema Validation*
- **Fungsi**: Validasi ketat batas input form, payload JSON, dan parameter URL sebelum menyentuh database.

### 5. **Drizzle ORM (`drizzle-orm` + `better-sqlite3`)** - *Zero-Bloat Type-Safe Database*
- **Fungsi**: ORM TypeScript paling ringan untuk SQLite WAL mode. Bebas overhead, migrasi skema instan.

### 6. **Puppeteer (`puppeteer`)** - *Headless Chrome Automation*
- **Fungsi**: Export dokumen PDF resmi (faktur kas, surat skripsi) dan scraping dinamis.

---

## 🔒 Standar Keamanan & Vetting
Sebelum mengunduh atau mengeksekusi modul eksternal:
1. Gunakan flag aman: `npm install --ignore-scripts`.
2. Periksa skrip `postinstall` di `package.json`.
3. Pindai pola celah keamanan dengan `semgrep` & `trufflehog`.
