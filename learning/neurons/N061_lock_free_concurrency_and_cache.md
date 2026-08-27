# N061: Lock-Free Concurrency, Memory Barriers & Cache-Oblivious Architecture

- **Kategori:** Systems & Concurrency Engineering
- **Tanggal Sintesis:** 2026-08-27 11:52:35
- **Status:** Active Operational Invariant

---

## 🎯 Inti Pembelajaran (Engineering Invariant)
1. SPSC & MPMC Lock-Free Ring Buffer: Terapkan memory ordering `std::memory_order_release` pada producer dan `std::memory_order_acquire` pada consumer untuk menjamin visibilitas data tanpa mutex overhead.
2. Pencegahan False Sharing: Seluruh atomic head/tail pointers wajib dialokasikan dengan 64-byte / 128-byte cache line alignment (`alignas(64)` / `#[repr(align(64))]`) untuk mencegah bus contention antar core CPU.
3. ABA Prevention: Solusikan masalah ABA pada Lock-Free Stack/Queue menggunakan Tagged Pointers (Pointer + 64-bit Monotonic Version Counter) atau Epoch-Based Memory Reclamation (EBR).
4. Arena Allocator & Cache-Oblivious Matrix Transposition: Alokasikan memori secara contiguous (SoA - Structure of Arrays) untuk memaksimalkan L1/L2 prefetcher throughput dan meminimalkan TLB misses.

## 🔍 Akar Masalah & Pencegahan Regresi (Root Cause Analysis)
Contention tinggi pada multithreaded systems sering kali disebabkan oleh false sharing pada atomic shared variables dan lock overhead. Dipecahkan dengan alignment cache-line eksplisit dan memory order release/acquire.

---
## 🔒 Disiplin Eksekusi
- Hindari pembuatan abstraksi berlebih (YAGNI).
- Terapkan perbaikan langsung pada fungsi akar bersama (*single root fix*).
- Kode tetap berada di bawah batas maksimal 300 baris per file.
