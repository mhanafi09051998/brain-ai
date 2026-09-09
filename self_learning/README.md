# Framework Agent untuk Optimasi Self-Learning

Arsitektur multi-agent otonom berbasis Python murni untuk pembelajaran mandiri (*self-learning*), refleksi performa empiris (*reflexion*), penyulingan pengetahuan (*knowledge distillation*), dan optimasi berkelanjutan.

---

## 🏗️ 1. Arsitektur Multi-Agent

Framework ini terdiri dari 4 agen spesialis yang beroperasi dalam siklus tertutup (*closed-loop feedback*):

```
                     ┌───────────────────────────────┐
                     │         Task Execution        │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │    ObserverAgent (Telemetri)  │
                     │  - Ukur Latensi & Pass Rate   │
                     │  - Isolasi Titik Kegagalan    │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │     CriticAgent (Evaluasi)    │
                     │  - Hitung Skor Kesesuaian     │
                     │  - Identifikasi Bottlenecks   │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │  DistillerAgent (Penyulingan) │
                     │  - Ekstrak Heuristik Sukses   │
                     │  - Catat Anti-Pola Kegagalan  │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
 ┌──────────────────┐        ┌───────────────────────┐
 │  KnowledgeStore  │ ◀───── │ OptimizerAgent        │
 │  (JSON Persisten)│ ─────▶ │ (Seleksi & Transform) │
 └──────────────────┘        └───────────┬───────────┘
                                         │
                                         ▼
                            [Kandidat Iterasi Berikutnya]
```

### Komponen Agen:
1. **[`ObserverAgent`](agents/observer.py)**: Menguji kode terhadap kasus uji (*test cases*), mengukur latensi eksekusi per iterasi (`time.perf_counter()`), dan mencatat jejak exception.
2. **[`CriticAgent`](agents/critic.py)**: Menilai laporan eksekusi terhadap target toleransi (pass rate, latensi maksimum), menghitung skor fitness (0-100), dan merumuskan kritik actionable.
3. **[`DistillerAgent`](agents/distiller.py)**: Menyuling temuan empiris menjadi entri pengetahuan terstruktur (`heuristic` atau `anti_pattern`) dengan skor bobot dampak.
4. **[`OptimizerAgent`](agents/optimizer.py)**: Memanfaatkan riwayat memori untuk memilih strategi terbaik atau mengeliminasi solusi yang berpotensi gagal.
5. **[`KnowledgeStore`](storage.py)**: Basis data memori berbasis JSON untuk persistensi lintas siklus/sesi.
6. **[`SelfLearningEngine`](engine.py)**: Pengorkestrasi orkestra pembelajaran hingga target tercapai (*converged*).

---

## ⚡ 2. Eksekusi Benchmark & Pengujian

### Menjalankan Simulasi Optimasi Otonom:
```bash
python -m self_learning.benchmark
```
*Menguji transisi dari algoritma O(N) ke O(log N) secara mandiri dengan deteksi kegagalan edge-case dan isolasi bottleneck.*

### Menjalankan Unit Tests:
```bash
python -m unittest self_learning.test_self_learning
```
*Memverifikasi integritas seluruh agen, kalkulasi metrik, persistensi disk, dan konvergensi.*

---

## 📋 3. Spesifikasi Protokol
Lihat dokumen aturan formal di **[`protocol.md`](protocol.md)** untuk panduan standar operasional mode self-learning asisten.
