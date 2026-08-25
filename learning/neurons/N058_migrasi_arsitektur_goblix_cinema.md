# N058: Migrasi Arsitektur Goblix Cinema ke Next.js App Router

- **Kategori:** Architecture
- **Tanggal Sintesis:** 2026-08-25 16:58:50
- **Status:** Active Operational Invariant

---

## 🎯 Inti Pembelajaran (Engineering Invariant)
Platform streaming Goblix Cinema telah dimigrasikan penuh ke Next.js 14 App Router, port 3070, domain goblix.my.id, dengan Server/Client Components, Route Handlers HTTP 206 partial streaming, dan sanitized WebVTT.

## 🔒 Disiplin Eksekusi
- Hindari pembuatan abstraksi berlebih (YAGNI).
- Terapkan perbaikan langsung pada fungsi akar bersama (*single root fix*).
- Kode tetap berada di bawah batas maksimal 300 baris per file.
