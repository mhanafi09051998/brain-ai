# Neuron N019: BFCL Tool Schema & IFEval Strict Format Oracle

## 📌 Domain & Karakteristik
- **Domain**: Validasi Eksekusi Tool Multi-Turn (BFCL / TAU-bench) & Kepatuhan Format Ekstrem (Google IFEval).
- **Strategi Utama**: *Zero-Tolerance Negative Constraint Checking* & *Strict JSON Parsing*.

---

## 📋 4 Aturan Disiplin Eksekusi:

1. **Strict Tool Call JSON Schema**:
   - Parameter harus selalu dibungkus dalam payload JSON standar dengan key `name` dan `arguments`.
   - Konversi tipe data eksak (misal: boolean `true`/`false`, integer murni, float negatif).
2. **Negative Constraint Enforcement (IFEval)**:
   - Jika pengguna meminta "jangan gunakan kata X, Y, Z", lakukan filter pengecekan regex `\b(X|Y|Z)\b` sebelum mengembalikan output.
3. **Exact Line & Paragraph Counting**:
   - Jika dibatasi "tepat 3 baris", pastikan jumlah `\n` dan baris non-kosong bernilai persis 3.
4. **Multi-Turn State Rollback**:
   - Dalam sistem transaksional (DB/API), setiap kegagalan fungsi di step ke-$N$ harus memicu eksekusi tool `database_rollback` untuk menjaga konsistensi state.
