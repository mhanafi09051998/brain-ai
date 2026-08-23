# Claudia Neuron Memory Network

Dokumen memori modular terdistribusi Claudia. Memori dipecah menjadi neuron-neuron tematik agar mudah dimaintain dan selalu presisi:

---

## 🧠 Active Memory Neurons
1. **[`user_profile.md`](file:///D:/Agent_Claudia_Autonomus/memory/neurons/user_profile.md)** — Profil Muhammad Hanafi, tone komunikasi, credentials, & Ponytail + Graphify core.
2. **[`ui_ux_design_rules.md`](file:///D:/Agent_Claudia_Autonomus/memory/neurons/ui_ux_design_rules.md)** — Standar default Light Mode, custom popover dropdown, eye password toggle, responsif mobile, dan **aturan ketat Max 300 baris kode per file**.
3. **[`mojoloker_brand.md`](file:///D:/Agent_Claudia_Autonomus/memory/neurons/mojoloker_brand.md)** — Domain resmi `mojoloker.my.id`, logo Tugu tunggal putih, database 21 Kecamatan / 301 Desa, panduan UMK 2026, dan Glints safety gate.
4. **[`vps_infrastructure.md`](file:///D:/Agent_Claudia_Autonomus/memory/neurons/vps_infrastructure.md)** — Arsitektur Cloud VPS, SQLite WAL engine, port-port aktif, dan status layanan PM2.
5. **[`ai_engine_9router.md`](file:///D:/Agent_Claudia_Autonomus/memory/neurons/ai_engine_9router.md)** — 9Router API gateway, API key, spesifikasi `prod.zolu.my.id` (Port 3012), dan code generator scaffolding.
6. **[`N008_live_session_checkpoint.md`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N008_live_session_checkpoint.md)** — **Live Session State Checkpoint**: Credentials admin (dikelola via `.env` / `.secrets`), Nextcloud (3015), Jellyfin (3016), Invite Portal `join.zolu.my.id` (3017), storage paths, subtitle cleaner, dan spesifikasi 1 TB SSD.
7. **[`N009_peak_algorithms_codex.md`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md)** — **Peak Algorithmic Codex**: Graph SCC (Tarjan), Probabilistic Filters (Bloom/HyperLogLog), Segment Tree, Lock-Free Concurrency.
8. **[`N010_distributed_systems_design.md`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N010_distributed_systems_design.md)** — **High-Scale Distributed Systems**: Raft/Paxos, Consistent Hashing, CQRS, Event Sourcing, Circuit Breakers.
9. **[`N011_mechanical_sympathy_perf.md`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N011_mechanical_sympathy_perf.md)** — **Mechanical Sympathy & Zero-Copy**: L1/L2 Cache Locality, `sendfile`/`splice` Zero-Copy, `io_uring` kernel event multiplexing.




---

## 📋 Prosedur Pembaruan Memori
- Setiap aturan atau koreksi baru ditambahkan ke file neuron terkait di [`memory/neurons/`](file:///D:/Agent_Claudia_Autonomus/memory/neurons/).
- Jika ada domain baru yang kompleks, buat neuron baru di folder tersebut.

---

## 📋 Active Tasks & History
- [x] MojoLoker V1 deployed di `mojoloker.my.id`.
- [x] Database 21 Kecamatan & 301 Desa Mojokerto lengkap di SQLite WAL.
- [x] Purge semua mock data (clean database).
- [x] Halaman resmi Panduan UMK 2026 (`/umk`).
- [x] Custom themed dropdown di Homepage, Register, dan Employer post modal.
- [x] Eye toggle show/hide password di Login dan Register.
- [x] Default Light Mode di seluruh 7 aplikasi VPS.
- [x] AI Web Production Generator (`prod.zolu.my.id`, Port 3012) deployed & running on PM2.
- [x] Hermes Agent installed & connected to 9Router AI Gateway (`ag/gemini-3.7-flash-high`) with global persona Claudia (Gahar Inovasi Teknologi).
- [x] User Tenant & Telegram Isolation Manager (`user.zolu.my.id`, Port 3003) restored & running on PM2.
- [x] Zolu Main Hub (`zolu.my.id`) telemetry & subdomains fully synchronized.
