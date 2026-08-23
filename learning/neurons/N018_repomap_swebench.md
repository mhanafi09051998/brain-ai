# Neuron N018: RepoMap AST Compression & SWE-bench Precision

## 📌 Domain & Karakteristik
- **Domain**: Rekayasa Resolusi Bug Tingkat Repositori (SWE-bench Verified & Lite).
- **Inspirasi & Rujukan**: Arsitektur *Repo Map* (`aider`) & *OpenHands AST Traversal*.
- **Prinsip**: Identifikasi caller pohon dependensi sebelum menyentuh 1 baris kode.

---

## 🛠️ 4 Aturan Emas Resolusi SWE-bench:

1. **AST Call-Graph PageRank**:
   - Kompresi struktur file 10.000+ baris menjadi subgraf relevan (Tree-Sitter AST) yang memuat hanya definisi kelas, signature fungsi, dan caller langsung.
2. **Unified Diff Format Strictness**:
   - Terapkan perubahan berbasis *Unified Diff* minimal (`-` dan `+`) yang hanya menargetkan *root cause*, bukan symptom guard per caller.
3. **Security Invariant Verification**:
   - Regex validation wajib menggunakan jangkar string absolut `\A` dan `\Z` (bukan `^` dan `$` yang dapat dibypass dengan newline injection `\n`).
4. **Zero-Side-Effect Guarantee**:
   - Menjalankan linting dan unit-test lokal untuk memastikan modul sibling tidak mengalami regresi perilaku (*regression-free*).
