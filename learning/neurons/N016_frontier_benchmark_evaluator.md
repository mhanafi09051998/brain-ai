# N016: Frontier Benchmark Evaluator & Continuous Evolution

## Karakteristik
- **Domain**: Evaluasi Tolok Ukur Kognitif Otonom (Frontier AI Benchmarks)
- **Status**: Aktif & Tersinkronisasi
- **Tujuan**: Memandu Claudia dalam menyelesaikan tantangan SWE-bench, TAU-bench/BFCL, AIME, NIAH, dan IFEval dengan akurasi maksimal.

## 6 Parameter Tolok Ukur Puncak:
1. **SWE-bench Verified**:
   - Analisis dependensi multi-file sebelum modifikasi.
   - Verifikasi AST diff bersih tanpa efek samping ke caller lain.
2. **TAU-bench & BFCL**:
   - Validasi skema parameter JSON ketat (100% strict schema).
   - Eksekusi alur pemanggilan alat multi-langkah (*multi-turn tool chaining*) dengan penanganan error deterministik.
3. **AIME & GPQA Diamond**:
   - Pembuktian langkah-demi-langkah invarian logika dan matematika formal (*Process-Supervised Reasoning*).
   - Menghindari tebakan heuristik tanpa pembuktian invariant state.
4. **Needle-In-A-Haystack (NIAH)**:
   - Pencarian fakta spesifik dalam konteks panjang 1M–2M token menggunakan GraphRAG traversal.
5. **IFEval (Format Discipline)**:
   - Kepatuhan 100% terhadap batasan negatif (*negative constraints*) dan format struktural yang diminta pengguna.
6. **Inference Speed & Efficiency**:
   - Zero-copy streaming, prompt caching, dan minimisasi token sampah (*Ponytail Minimality Ladder*).

## Lokasi Monitoring Realtime:
- **Server URL**: `https://learn.zolu.my.id` (Port 3005)
- **Layanan PM2**: `zolu-learn`