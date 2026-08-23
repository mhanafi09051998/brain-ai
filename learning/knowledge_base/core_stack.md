# Core Stack & Architecture

## 1. Database & Storage
- **Database Engine**: **SQLite via WSL / Linux Environment** (menggunakan `better-sqlite3` dengan WAL mode `PRAGMA journal_mode = WAL;`).
- **Pola Akses**: File-based zero-overhead, langsung dieksekusi di Linux/WSL/VPS environment agar performa I/O native dan konsisten.

## 2. Web & Service Stack
- **Framework Utama**: **Next.js (App Router) + TypeScript + Node.js (V8 runtime)**.
- **Styling & UI**: **Tailwind CSS + Lucide Icons** (Dark-mode first, Mobile-first, zero horizontal overflow).
- **Process Manager**: **PM2** (Zero-downtime fork execution).
- **Tunnel & Edge Routing**: **Cloudflare Tunnel (`cloudflared`)** ke domain `*.zolu.my.id`.

## 3. Engineering & Intelligence Engines
1. **Ponytail**: Lazy Senior Dev principles (YAGNI, stdlib-first, zero-bloat, shortest working diff).
2. **Graphify**: Multimodal knowledge graph parser (`graphifyy` / AST + semantic) di `graphify-out/`.
3. **9Router**: Local proxy gateway untuk multi-model AI routing.

