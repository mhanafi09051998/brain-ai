# Neuron N017: Program-Aided Mathematical Reasoning & AIME Invariants

## 📌 Domain & Karakteristik
- **Domain**: Pembuktian Matematika Formal, AIMO (AI Mathematical Olympiad), AIME, & GPQA Diamond.
- **Strategi Utama**: *Program-Aided Language Models (PAL)* & *Process-Supervised Reasoning*.
- **Prinsip**: Jangan pernah menebak hasil komputasi aljabar secara probabilistik jika invariant dapat diverifikasi via eksekusi kode deterministik.

---

## 🧮 4 Pilar Heuristik AIME & Olympiad:

1. **Diophantine Equation & Integer Grid Constraints**:
   - Untuk persamaan lingkaran $x^2 + y^2 = R^2$, faktorisasi Gaussian Integers $\mathbb{Z}[i]$.
   - Hitung seluruh permutasi tanda $(\pm x, \pm y)$ dan urutan $x \le y$ secara eksak.
2. **Combinatorics & Modulo Parity Invariants**:
   - Uji batas $n \le 1000$ yang habis dibagi $4$ dan memiliki digit non-zero berbeda menggunakan teknik *digit-DP* atau *inclusion-exclusion*.
3. **Polynomial Root Dynamics & Recurrence Sequences**:
   - Deret $a_{n+1} = a_n + n \implies a_n = a_1 + \frac{n(n-1)}{2}$.
   - Selalu cari formula bentuk tertutup (*closed-form equation*) sebelum menghitung nilai suku ke-$k$.
4. **SymPy / Python Invariant Verification**:
   - Selalu bungkus hasil akhir dalam tag format baku `\boxed{jawaban}` tanpa teks penutup tambahan.
