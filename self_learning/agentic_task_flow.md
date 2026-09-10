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

### Fase 1: Ingestion & Grounding (Pahami Konteks & Fakta Nyata)
- **Sumber Kebenaran**: Baca dokumen acuan (`memory.md`, `GEMINI.md`, dan file kode riil di disk).
- **Inspeksi Nyata**: Selalu verifikasi keberadaan file, pustaka, dan konfigurasi sebelum mengusulkan perubahan.
- **Anti-Halusinasi & Klarifikasi**: Jangan menebak jika instruksi pengguna ambigu. Ajukan pertanyaan klarifikasi jika ada parameter yang belum ditentukan.

### Fase 2: Planning & Decomposition (Rencana Bertahap Terukur)
- **Dekomposisi Masalah**: Pecah instruksi menjadi sub-tugas independen (*divide and conquer*).
- **Kriteria Penerimaan (*Acceptance Criteria*)**: Tentukan tolok ukur sukses yang eksplisit dan teruji (misal: "semua unit test lolos", "zero lint warning", "skema database tersinkronisasi").

### Fase 3: Grounded Execution & Minimal Diffs (Eksekusi Terfokus)
- **Minimal Diffs**: Utamakan perubahan kecil pada blok baris yang relevan. Hindari penulisan ulang seluruh berkas jika tidak diperlukan.
- **KISS & YAGNI**: Pilih solusi paling sederhana, minim dependensi luar, dan jangan tambahkan fungsionalitas spekulatif yang tidak diminta.
- **Dokumentasi & Tipe**: Sertakan *type hints* dan *doctests* untuk kode baru.

### Fase 4: Empirical Verification (Verifikasi Nyata di Lingkungan)
- **Uji Langsung**: Eksekusi perintah pengujian (unit test, doctest, build, atau linter) di terminal lokal.
- **Bebas Regresi**: Pastikan fitur atau modul yang sudah ada tidak terganggu oleh penambahan kode baru.

### Fase 5: Reflexion & Self-Correction (Jika Terjadi Kegagalan)
- Apabila pengujian gagal, **hentikan pengulangan acak**.
- Terapkan **Rubrik 4-Kuadran Refleksi Diri**:
  1. *Target Nyata*: Output spesifik yang diharapkan.
  2. *Kondisi Aktual*: Pesan error atau traceback yang sebenarnya terjadi.
  3. *Akar Permasalahan*: Diagnosis logis mengapa implementasi sebelumnya salah.
  4. *Tindakan Korektif*: Aturan baru yang wajib ditaati pada perbaikan selanjutnya.
- Suntikkan refleksi sebagai *constraint* pada eksekutor sebelum mencoba kembali.

### Fase 6: Distillation & Concise Delivery (Persistensi & Penyerahan)
- **Penyulingan Memori**: Perbarui `memory.md` jika ada perubahan arsitektur, milestone penting, atau preferensi baru.
- **Penyajian Padat & Presisi**: Sampaikan solusi secara langsung, sertakan tautan ke file yang diubah (`file://`), dan hilangkan basa-basi pembuka/penutup klise.
