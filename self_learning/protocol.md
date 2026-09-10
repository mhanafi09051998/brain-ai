# Protokol Mode Self-Learning (Autonomous Learning Protocol)

Dokumen ini mendefinisikan spesifikasi dan aturan operasional **Mode Self-Learning** untuk asisten dan sistem agen di workspace ini.

---

## 1. Konsep Inti: Siklus Refleksi Tertutup (Closed-Loop Reflexion)

Mode Self-Learning beroperasi menggunakan siklus berulang 4 tahap (OODA + Reflexion):

```
       ┌────────────────────────────────────────────────┐
       │                                                │
       ▼                                                │
┌──────────────┐     ┌──────────────┐     ┌─────────────┴┐
│   OBSERVE    │ ──▶ │    CRITIQUE  │ ──▶ │  DISTILL &   │
│ (Eksekusi &  │     │ (Evaluasi &  │     │  OPTIMIZE    │
│  Metrik)     │     │  Celah Kinerja)│    │ (Simpan Pola │
└──────────────┘     └──────────────┘     │  & Refactor) │
                                          └──────────────┘
```

1. **Observe (Pengamatan Empiris)**:
   - Mencatat waktu eksekusi (*latency*), konsumsi memori, error stack trace, dan rasio kelulusan tes (*pass rate*).
   - Mengisolasi titik kegagalan (*fault localization*).
2. **Critique (Refleksi Kritis)**:
   - Membandingkan hasil aktual terhadap tolok ukur (*baseline performance*).
   - Menghasilkan analisis kualitatif: Mengapa solusi gagal atau tidak optimal?
3. **Distill (Penyulingan Pengetahuan)**:
   - Mengekstrak dua jenis memori:
     - **Heuristik Sukses**: Pola solusi yang terbukti lulus tes dan efisien.
     - **Anti-Pola (Failure Modes)**: Kesalahan atau *edge cases* yang wajib dihindari.
   - Menyimpan temuan ke dalam memori persisten (`memory.md` & `self_learning/knowledge_base/`).
4. **Optimize (Pembaruan Kebijakan/Kode)**:
   - Menghasilkan versi kandidat baru yang mengintegrasikan heuristik dari sesi sebelumnya.
   - Menjalankan kembali pengujian hingga konvergen (target metrik terpenuhi).

---

## 2. Aturan Operasional Mode Self-Learning

1. **Prinsip Validasi Empiris Mutlak**:
   - Perbaikan kode atau strategi hanya diakui sah jika dibuktikan dengan pengujian terukur (doctest, unit test, atau benchmark benchmark numerik).
   - Nol asumsi: klaim "lebih cepat" wajib disertai data waktu eksekusi (ms/μs).
2. **Pencegahan Regresi (Regression Guard)**:
   - Kandidat optimasi baru tidak boleh merusak fungsionalitas yang sebelumnya sudah lulus (*zero regression*).
3. **Persistensi Lintas Sesi**:
   - Setiap pola penting yang dipelajari wajib disinkronkan ke dalam knowledge store persisten agar dapat digunakan pada iterasi atau sesi mendatang tanpa perlu mengulang kegagalan yang sama.
