# N062: Distributed Consensus Invariants, Log Compaction & Idempotent SAGA

- **Kategori:** Distributed Systems & Reliability
- **Tanggal Sintesis:** 2026-08-27 11:52:35
- **Status:** Active Operational Invariant

---

## 🎯 Inti Pembelajaran (Engineering Invariant)
1. Raft Term Monotonicity & Leader Election: Setiap RPC term harus strict monotonic; node yang menerima term lebih tinggi wajib langsung revert ke Follower state dan mengupdate local term.
2. Fencing Tokens & Split-Brain Immunity: Distribusi lock wajib menyertakan monotonic fencing token di storage layer agar mutasi dari mantan leader (zombie process) ditolak otomatis.
3. Snapshot Log Compaction: Segment log di-truncate hanya setelah snapshot state disk telah ter-fsync permanen untuk mencegah data loss saat sudden power failure.
4. Idempotent SAGA Compensation Flow: Setiap langkah transaksi terdistribusi wajib memiliki UUID Idempotency-Key dan kompensasi rollback deterministik yang aman dipanggil berulang kali (*idempotent replay*).

## 🔍 Akar Masalah & Pencegahan Regresi (Root Cause Analysis)
Inkonsistensi data transaksi terdistribusi kerap terjadi saat network partition dan dual-primary election. Dipecahkan dengan aturan fencing token di database layer dan replay kompensasi SAGA berbasis idempotency key.

---
## 🔒 Disiplin Eksekusi
- Hindari pembuatan abstraksi berlebih (YAGNI).
- Terapkan perbaikan langsung pada fungsi akar bersama (*single root fix*).
- Kode tetap berada di bawah batas maksimal 300 baris per file.
