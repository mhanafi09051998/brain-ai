import os
import sys
import json
import datetime
import subprocess

WORKSPACE = r"D:\GEMINI-HANAFI"
os.chdir(WORKSPACE)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

print("🧠 [SYNTHESIZING NEURON N081: WORLD-CLASS REPOSITORY ARCHITECTURE]")
print("===================================================================")

now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
neuron_id = "N081"
n_file = "N081_world_class_repository_architecture.md"
n_path = os.path.join(WORKSPACE, "learning", "neurons", n_file)

md_content = """# N081: World-Class Repository Architecture & Trunk-Based DX Engineering

- **Kategori:** Architecture & Developer Experience (DX)
- **Tanggal Sintesis:** """ + now_iso + """
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
"""

with open(n_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"  [✓] File neuron berhasil dibuat: learning/neurons/{n_file}")

# Update Index
index_path = os.path.join(WORKSPACE, "learning", "NEURON_INDEX.json")
with open(index_path, "r", encoding="utf-8-sig") as f:
    index_data = json.load(f)

neurons = index_data.get("neurons", [])
existing_ids = {n["id"]: n for n in neurons}

mem_file = os.path.join(WORKSPACE, "memory.md")
with open(mem_file, "r", encoding="utf-8") as f:
    mem_text = f.read()

meta_entry = {
    "id": neuron_id,
    "label": "Neuron N081: World-Class Repository Architecture & Trunk-Based DX Engineering",
    "file": n_file,
    "connections": ["N001", "N004", "N030", "N036", "N054"],
    "synapse_count": 5,
    "size_bytes": os.path.getsize(n_path)
}

if neuron_id not in existing_ids:
    neurons.append(meta_entry)
    new_mem = f"{len(neurons)}. **[`{n_file}`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/{n_file})** — **{meta_entry['label']}**: Top-level monorepo/polyrepo structure, DAG package boundaries, contract-first single source of truth, 5-minute DX onboarding rule.\n"
    if "## 🧠 Active Memory Neurons" in mem_text:
        parts = mem_text.split("## 🧠 Active Memory Neurons\n")
        mem_text = parts[0] + "## 🧠 Active Memory Neurons\n" + new_mem + parts[1]
else:
    existing_ids[neuron_id] = meta_entry

index_data["neurons"] = neurons
index_data["total_neurons"] = len(neurons)
index_data["total_synapses"] = sum(len(n.get("connections", [])) for n in neurons)
index_data["updated_at"] = now_iso

with open(index_path, "w", encoding="utf-8") as f:
    json.dump(index_data, f, indent=2, ensure_ascii=False)

with open(mem_file, "w", encoding="utf-8") as f:
    f.write(mem_text)

print(f"[✓] Jaringan Neuron berhasil ditingkatkan: Total {len(neurons)} Master Neurons aktif.")

# Pre-Flight Brain Integrity Check
print("\n[*] Menjalankan Pre-Flight Brain Integrity Check...")
res = subprocess.run([sys.executable, os.path.join(WORKSPACE, "scripts", "test_brain.py")], capture_output=True, text=True)
print(res.stdout.strip())
if res.returncode != 0:
    print("[!] Gagal verifikasi integritas otak:", res.stderr.strip())
    sys.exit(1)

# Auto-sync to GitHub
print("\n[*] Menyinkronkan seluruh 81 Master Neurons ke GitHub...")
sync_res = subprocess.run([sys.executable, os.path.join(WORKSPACE, "scripts", "auto_sync_github.py")], capture_output=True, text=True)
print(sync_res.stdout.strip())

print("\n✨ NEURON N081 SYNTHESIZED, VERIFIED & SYNCHRONIZED TO GITHUB!")
