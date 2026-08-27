# N081: World-Class Repository Architecture & Trunk-Based DX Engineering

- **Kategori:** Architecture & Developer Experience (DX)
- **Tanggal Sintesis:** 2026-08-27 14:04:20
- **Status:** Active Operational Invariant

---

## 🎯 Inti Pembelajaran (Engineering Invariant)

### 1. Struktur Top-Level Standar Dunia (Monorepo & Polyrepo)
Repositori kelas dunia (standar Stripe, Vercel, Meta) wajib memisahkan ranah aplikasi, pustaka bersama, dan perkakas secara tegas:
```
├── apps/                   # Entrypoint aplikasi yang dapat di-deploy (web, api, worker, mobile)
├── packages/ / libs/       # Shared business logic, UI design system, DB client, internal SDKs
│   ├── ui/                 # Komponen antarmuka murni tanpa business state
│   ├── db/                 # Single Source of Truth database schema & migrations (Prisma/Drizzle)
│   └── api-contracts/      # Tipe data, validasi Zod/OpenAPI yang dibagikan ke seluruh apps
├── tooling/ / config/      # Konfigurasi terpusat (ESLint, Prettier, Tailwind, TypeScript)
├── scripts/                # Otomasi deployment, audit integritas, database seeding, benchmark
└── docs/ / learning/       # Arsitektur sistem (C4 Model, ADRs, Invarian kognitif)
```

### 2. Invarian Hermetic Builds & Dependency Graph
- **Zero Circular Dependencies**: Dependensi antar-paket membentuk *Directed Acyclic Graph (DAG)* yang ketat. `packages/ui` dilarang mengimpor `apps/web`.
- **Remote Content-Addressable Cache**: Task runner (Turborepo / Nx / Bazel) menggunakan fingerprint hash input file `hash(src + deps)` untuk menjamin *instant cache hit* pada CI/CD.
- **Strict Package Boundaries**: Akses antar-modul wajib melalui `index.ts` (public API export), dilarang melakukan *deep import* ke internal folder modul lain (`import x from '@repo/db/src/internal/...'` is STRICTLY FORBIDDEN).

### 3. Single Source of Truth (Contract-First Architecture)
- Schema database dan API contract didefinisikan satu kali di `packages/db` atau `packages/api-contracts` dan diekspor sebagai TypeScript types / Zod schemas.
- Frontend dan Backend berbagi interface yang sama tanpa perlu duplikasi kode manual (*Zero-Drift End-to-End Type Safety*).

### 4. Zero-Friction Developer Experience (DX) & 5-Minute Rule
- **5-Minute Onboarding Rule**: Developer baru wajib bisa menjalankan seluruh stack lokal dalam 1 perintah tunggal (`pnpm dev` atau `make dev`).
- **Environment Parity & Strict Validation**: Dilarang menggunakan raw `process.env`. Seluruh env var wajib divalidasi saat aplikasi boot menggunakan skema Zod (misal: `@t3-oss/env-core`), fail-fast jika ada konfigurasi yang hilang.
- **Git Discipline**: Trunk-Based Development dengan *short-lived branches* (< 24 jam), conventional commits (`feat:`, `fix:`, `refactor:`), dan automated versioning via Changesets.

---

## 🔍 Akar Masalah & Pencegahan Regresi (Root Cause Analysis)
- **Dependency Drift & Version Hell**: Terjadi akibat setiap sub-folder mendefinisikan versi library yang berbeda. Dicegah dengan *Catalog dependencies* (`pnpm catalog:` / `workspaces` synchronization).
- **Spaghetti Coupling**: Terjadi ketika logika UI tercampur dengan query database. Dipecahkan dengan isolasi komponen murni di `packages/ui` dan isolasi data layer di `packages/db`.
- **CI/CD Bottlenecks**: Terjadi akibat rebuild seluruh aplikasi saat hanya ada 1 file dokumentasi yang berubah. Dipecahkan dengan *impacted-only affected builds* via DAG hash analysis.

---

## 🔒 Disiplin Eksekusi (Ponytail Standard)
- Terapkan batas maksimal 300 baris kode per file.
- Colocation rule: Dekatkan file komponen, test, dan types dalam satu folder (`Button.tsx`, `Button.test.tsx`, `Button.types.ts`).
- Root fix rule: Perbaiki utility bersama di `packages/` sekali, bukan membuat helper duplikat di tiap-tiap app.
