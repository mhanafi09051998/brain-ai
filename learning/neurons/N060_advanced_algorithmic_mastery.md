# N060: Advanced Algorithmic Mastery & Dynamic Graph Automata

- **Kategori:** Algorithms & Competitive Programming
- **Tanggal Sintesis:** 2026-08-27 11:52:35
- **Status:** Active Operational Invariant

---

## 🎯 Inti Pembelajaran (Engineering Invariant)
1. Tree DP with $O(N)$ Rerooting: Hitung agregasi pohon secara global dalam 2 kali DFS traversal (DFS 1: bottom-up subtree DP, DFS 2: top-down parent contribution broadcast) tanpa re-kalkulasi $O(N^2)$.
2. 2D Range Point-Update & Range-Query via Fenwick Tree (BIT): Reduksi memori dari 2D Segment Tree $O(N^2 \log^2 N)$ ke 2D Binary Indexed Tree $O(N^2)$ dengan operasi bitwise `i += i & (-i)` dan `i -= i & (-i)`.
3. Li Chao Segment Tree (Dynamic Convex Hull Trick): Optimasi DP linear $O(N^2) \to O(N \log C)$ untuk evaluasi persamaan garis dinamis $y = mx + c$ tanpa syarat gradien terurut monotonik.
4. Strongly Connected Components (Tarjan $O(V+E)$): Traversal DFS tunggal menggunakan `lowlink` dan `dfn` stack untuk identifikasi directed cycles & condensation DAG.
5. Invariant Eksekusi: Hindari rekursi dalam yang memicu stack overflow; ubah ke iterasi eksplisit dengan bounded stack pada input $N \ge 10^5$.

## 🔍 Akar Masalah & Pencegahan Regresi (Root Cause Analysis)
Pemecahan masalah graf berskala besar sering kali mengalami TLE karena rekursi unoptimized atau komputasi berulang. Ditetapkan invarian Tree Rerooting dan Li Chao Tree sebagai standar reduksi kompleksitas waktu linear-logaritmik.

---
## 🔒 Disiplin Eksekusi
- Hindari pembuatan abstraksi berlebih (YAGNI).
- Terapkan perbaikan langsung pada fungsi akar bersama (*single root fix*).
- Kode tetap berada di bawah batas maksimal 300 baris per file.
