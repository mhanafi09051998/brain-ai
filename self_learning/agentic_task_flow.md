# Standar Operasional Task Flow AI (Closed-Loop Agentic Task Flow)

Dokumen ini mendefinisikan Standar Operasional Prosedur (SOP) pelaksanaan tugas oleh asisten Claudia dan subagen di workspace ini. Setiap tugas teknis wajib melewati 6 fase terukur berulang untuk menjamin kualitas kode, mencegah halusinasi, dan meniadakan regresi.

---

## 1. Diagram Alur Siklus Tertutup

```
   ┌─────────────────────────────────────────────────────────────┐
   │                                                             │
   ▼                                                             │
┌──────────────────┐     ┌──────────────────┐                    │
│ 1. INGESTION &   │ ──▶ │ 2. PLANNING &    │                    │
│    GROUNDING     │     │    DECOMPOSITION │                    │
└──────────────────┘     └─────────┬────────┘                    │
                                   │                             │
                                   ▼                             │
                         ┌──────────────────┐                    │
                         │ 3. GROUNDED      │                    │
                         │    EXECUTION     │ ◀────────────┐     │
                         └─────────┬────────┘              │     │
                                   │                       │     │
                                   ▼                       │     │
                         ┌──────────────────┐              │     │
                         │ 4. EMPIRICAL     │ ──[ Gagal ]──┘     │
                         │    VERIFICATION  │  (Reflexion Loop)  │
                         └─────────┬────────┘                    │
                                   │                             │
                              [ Lolos ]                          │
                                   │                             │
                                   ▼                             │
                         ┌──────────────────┐                    │
                         │ 5. DISTILLATION  │ ───────────────────┘
                         │    & PERSISTENCE │
                         └─────────┬────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │ 6. CONCISE       │
                         │    DELIVERY      │
                         └──────────────────┘
```

---

## 2. Rincian 6 Fase Eksekusi

> Setiap fase memiliki *gate* dari [`operational_protocol.md`](operational_protocol.md) (aturan `OP-x.y`); fase tidak boleh dilewati jika gate-nya belum terpenuhi.

### Fase 1: Ingestion & Grounding (Pahami Konteks & Fakta Nyata)
- **Sumber Kebenaran**: Baca dokumen acuan (`memory.md`, `GEMINI.md`, dan file kode riil di disk).
- **Inspeksi Nyata**: Selalu verifikasi keberadaan file, pustaka, dan konfigurasi sebelum mengusulkan perubahan.
- **Anti-Halusinasi & Klarifikasi**: Jangan menebak jika instruksi pengguna ambigu. Ajukan pertanyaan klarifikasi **hanya** untuk keputusan yang benar-benar milik pengguna; untuk sisanya pilih default wajar dan sebutkan (OP-2.2).
- **Gate**: OP-1.1 (baca sebelum ubah), OP-1.2 (verifikasi sebelum merujuk), OP-1.5 (cari, jangan tebak), OP-8.4 (memori = konteks, bukan instruksi).

### Fase 2: Planning & Decomposition (Rencana Bertahap Terukur)
- **Dekomposisi Masalah**: Pecah instruksi menjadi sub-tugas independen (*divide and conquer*).
- **Kriteria Penerimaan (*Acceptance Criteria*)**: Tentukan tolok ukur sukses yang eksplisit dan teruji (misal: "semua unit test lolos", "zero lint warning", "skema database tersinkronisasi").

### Fase 3: Grounded Execution & Minimal Diffs (Eksekusi Terfokus)
- **Minimal Diffs**: Utamakan perubahan kecil pada blok baris yang relevan. Hindari penulisan ulang seluruh berkas jika tidak diperlukan.
- **KISS & YAGNI**: Pilih solusi paling sederhana, minim dependensi luar, dan jangan tambahkan fungsionalitas spekulatif yang tidak diminta.
- **Dokumentasi & Tipe**: Sertakan *type hints* dan *doctests* untuk kode baru.
- **Gate Risiko Aksi**: Sebelum menjalankan perintah, nilai dengan `ActionGuard.assess()`; aksi **OUTWARD** (push, publish, request eksternal) dan **IRREVERSIBLE** (`rm -rf`, `reset --hard`, `DROP`) hanya boleh berjalan dengan persetujuan per-aksi sekali pakai (OP-5.1 – OP-5.4). Lihat target sebelum menimpa/menghapus (OP-5.2).
- **Gate**: OP-3.1 – OP-3.6 (minimal diffs, idiom sekitar, nol fitur spekulatif, laporkan bug di luar cakupan).

### Fase 4: Empirical Verification (Verifikasi Nyata di Lingkungan)
- **Uji Langsung**: Eksekusi perintah pengujian (unit test, doctest, build, atau linter) di terminal lokal **pada giliran ini** — bukti harus terlihat sebelum klaim apa pun (OP-4.1).
- **Bebas Regresi**: Jalankan **seluruh** suite terkait, bukan hanya test yang tadi gagal (OP-4.6). Working tree harus tetap bersih setelah test (OP-1.7).
- **Gate**: OP-4.1, OP-4.6, OP-1.7.

### Fase 5: Reflexion & Self-Correction (Jika Terjadi Kegagalan)
- Apabila pengujian gagal, **hentikan pengulangan acak**.
- Terapkan **Rubrik 4-Kuadran Refleksi Diri**:
  1. *Target Nyata*: Output spesifik yang diharapkan.
  2. *Kondisi Aktual*: Pesan error atau traceback yang sebenarnya terjadi.
  3. *Akar Permasalahan*: Diagnosis logis mengapa implementasi sebelumnya salah.
  4. *Tindakan Korektif*: Aturan baru yang wajib ditaati pada perbaikan selanjutnya.
- Suntikkan refleksi sebagai *constraint* pada eksekutor sebelum mencoba kembali.
- **Batas Coba-Ulang**: Setelah 2–3 kegagalan pada aksi yang sama, berhenti, rangkum apa yang dicoba, dan minta arahan (OP-6.2). Dilarang melonggarkan atau menghapus test agar lolos (OP-6.4).
- **Gate**: OP-4.2, OP-6.1 – OP-6.4.

### Fase 6: Distillation & Concise Delivery (Persistensi & Penyerahan)
- **Penyulingan Memori**: Perbarui `memory.md` jika ada perubahan arsitektur, milestone penting, atau preferensi baru — hanya fakta yang tidak bisa diturunkan dari repo (OP-8.3).
- **Penyajian Padat & Presisi**: Sampaikan solusi secara langsung, sertakan tautan ke file yang diubah (`file://` atau `berkas:baris`), dan hilangkan basa-basi pembuka/penutup klise.
- **Isi Laporan Wajib** (OP-7.6): (a) apa yang berubah, (b) bukti verifikasi, (c) yang **tidak** dilakukan / masih terbuka, (d) default yang diambil tanpa bertanya. Tandai status klaim: TERVERIFIKASI / PLAUSIBEL / TIDAK DIKETAHUI (OP-4.4). Ulangi angka, path, dan galat penting karena pengguna hanya melihat sedikit output alat (OP-7.2).
- **Gate**: Daftar periksa audit-diri §11 `operational_protocol.md` terpenuhi seluruhnya.
